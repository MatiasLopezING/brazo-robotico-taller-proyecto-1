#!/usr/bin/env python3
"""Publica en /joint_states la tarea completa: tomar el vaso y depositarlo.

No es una animacion dibujada a mano. Cada cuadro se resuelve con la cinematica
inversa cerrada de dos eslabones iguales, a radio constante y con la pinza
horizontal, igual que en Cinematica_brazo.ipynb; el traslado entre los dos
puntos es giro puro de la base. Si una pose no cerrara dentro de las ventanas de
recorrido, la trayectoria no existiria y el nodo lo avisa al arrancar.
"""
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

L1, L2, L3 = 0.120, 0.120, 0.085
H_HOMBRO = 0.190
CAJA_H, R_GUARDA = 0.100, 0.113          # la caja base es un obstaculo (ADR-009)
Z_GARRA, Z_ALTO, R_VASO = 0.070, 0.170, 0.250
GIRO, Q1_INICIAL = 47.0, 35.0            # grados: el traslado es giro de base
DEDO_CERRADO, DEDO_ABIERTO = math.radians(62.0), 0.0

VENT = {'hombro': (50.0, 110.0), 'codo': (0.0, 120.0), 'muneca': (-108.0, 40.0)}
FASES = [('bajar al vaso', 1.2), ('cerrar la pinza', 0.8), ('levantar', 1.2),
         ('girar la base', 2.0), ('bajar a destino', 1.2), ('abrir la pinza', 0.8),
         ('retirarse', 1.2)]


def articulaciones(q2, q3, q4):
    a23, a234 = q2 + q3, q2 + q3 + q4
    codo = (L1*math.sin(q2), H_HOMBRO + L1*math.cos(q2))
    mun = (codo[0] + L2*math.sin(a23), codo[1] + L2*math.cos(a23))
    return [(0.0, H_HOMBRO), codo, mun,
            (mun[0] + L3*math.sin(a234), mun[1] + L3*math.cos(a234))]


def libre(q2, q3, q4):
    return all(z >= 0 and not (z < CAJA_H and abs(r) < R_GUARDA)
               for r, z in articulaciones(q2, q3, q4))


def inversa(r, z):
    """Angulos [grados] de hombro, codo y muneca para la punta en (r, z)."""
    rx, zy = r - L3, z - H_HOMBRO
    d = math.hypot(rx, zy)
    if d > L1 + L2:
        return None
    semi = math.acos(min(1.0, d/(L1 + L2)))        # L1 = L2: triangulo isosceles
    medio = math.atan2(rx, zy)
    for s in (1, -1):                              # codo abajo y codo arriba
        q2, q3 = medio - s*semi, 2*s*semi
        g = [math.degrees(q2), math.degrees(q3)]
        g.append(90.0 - g[0] - g[1])               # muneca asistida
        if (VENT['hombro'][0] <= g[0] <= VENT['hombro'][1]
                and VENT['codo'][0] <= g[1] <= VENT['codo'][1]
                and VENT['muneca'][0] <= g[2] <= VENT['muneca'][1]
                and libre(q2, q3, math.radians(g[2]))):
            return g
    return None


def trayectoria(dt=0.02):
    """Lista de (q1, q2, q3, q4, dedo) en radianes, un elemento cada dt."""
    m, t, fallas = [], 0.0, 0
    for k, (_, dur) in enumerate(FASES):
        n = max(1, round(dur/dt))
        for i in range(n):
            u = i/n
            z, dedo, q1 = Z_GARRA, DEDO_ABIERTO, Q1_INICIAL
            if k == 0:
                z = Z_ALTO + (Z_GARRA - Z_ALTO)*u
            elif k == 1:
                dedo = DEDO_CERRADO*u
            elif k == 2:
                z, dedo = Z_GARRA + (Z_ALTO - Z_GARRA)*u, DEDO_CERRADO
            elif k == 3:
                z, dedo, q1 = Z_ALTO, DEDO_CERRADO, Q1_INICIAL + GIRO*u
            elif k == 4:
                z, dedo, q1 = (Z_ALTO + (Z_GARRA - Z_ALTO)*u, DEDO_CERRADO,
                               Q1_INICIAL + GIRO)
            elif k == 5:
                dedo, q1 = DEDO_CERRADO*(1 - u), Q1_INICIAL + GIRO
            else:
                z, q1 = Z_GARRA + (Z_ALTO - Z_GARRA)*u, Q1_INICIAL + GIRO
            b = inversa(R_VASO, z)
            if b is None:
                fallas += 1
                b = inversa(R_VASO, Z_GARRA)
            m.append((math.radians(q1), math.radians(b[0]), math.radians(b[1]),
                      math.radians(b[2]), dedo, k))
            t += dt
    return m, fallas


class Tarea(Node):
    NOMBRES = ['base', 'hombro', 'codo', 'muneca', 'dedo_izq', 'dedo_der']

    def __init__(self):
        super().__init__('tarea')
        self.dt = 0.02
        self.cuadros, fallas = trayectoria(self.dt)
        self.i = 0
        self.fase = -1
        self.pub = self.create_publisher(JointState, 'joint_states', 10)
        self.create_timer(self.dt, self.tic)
        dur = len(self.cuadros)*self.dt
        if fallas:
            self.get_logger().error(
                f'{fallas} cuadros sin solucion dentro de las ventanas: '
                'la trayectoria no es alcanzable')
        else:
            self.get_logger().info(
                f'trayectoria resuelta: {len(self.cuadros)} cuadros, {dur:.1f} s, '
                'todas las poses dentro de las ventanas de ADR-010')

    def tic(self):
        q1, q2, q3, q4, dedo, fase = self.cuadros[self.i]
        if fase != self.fase:
            self.fase = fase
            self.get_logger().info(f'fase {fase + 1}: {FASES[fase][0]}')
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.NOMBRES
        # los dos dedos se mueven en espejo: el URDF lo declara con <mimic>, y
        # se publican los dos para no depender de que el visor lo resuelva
        msg.position = [q1, q2, q3, q4, dedo, dedo]
        self.pub.publish(msg)
        self.i = (self.i + 1) % len(self.cuadros)


def main():
    rclpy.init()
    nodo = Tarea()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
