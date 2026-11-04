#!/usr/bin/env python3
"""Planificador: convierte pedidos en trayectorias y se las manda al controlador.

Expone lo que el proyecto necesita por encima de la interfaz estandar:

  accion   ir_a_punto           lleva el TCP a un punto; resuelve la inversa
  servicio resolver_inversa     consulta pura, no mueve nada
  servicio memorizar_pose       guarda la pose actual con un nombre
  servicio ir_a_pose            reproduce una pose guardada

Lo que se guarda al memorizar son **angulos de articulacion**, no coordenadas
(ADR-011): reproducir una pose no necesita inversa, no puede fallar por alcance
y no arrastra el error del modelo. La inversa sirve para *calcular* un destino;
lo que se guarda es el resultado.

Si el punto pedido no es alcanzable, la meta se **rechaza con el motivo**. No se
satura al borde: el borde del espacio alcanzable es irregular —parte lo fija la
caja base y parte el tope del hombro— y proyectar sobre el no tiene significado
fisico claro.
"""
import math
import os
import threading
import time

import rclpy
import yaml
from brazo_interfaces.action import IrAPunto
from brazo_interfaces.srv import IrAPoseMemorizada, MemorizarPose, ResolverInversa
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient, ActionServer, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from . import cinematica as cin
from . import perfil


def a_duracion(t):
    return Duration(sec=int(t), nanosec=int((t - int(t))*1e9))


class Planificador(Node):

    def __init__(self):
        super().__init__('planificador')
        self.declare_parameter('archivo_poses', '')
        self.declare_parameter('periodo', 0.02)
        self.periodo = self.get_parameter('periodo').value
        self.archivo = self.get_parameter('archivo_poses').value

        self.q = None                       # ultima pose conocida, en grados
        self.poses = self.cargar()
        grupo = ReentrantCallbackGroup()

        self.create_subscription(JointState, 'joint_states', self.estado, 10,
                                 callback_group=grupo)
        self.cliente = ActionClient(self, FollowJointTrajectory,
                                    'follow_joint_trajectory',
                                    callback_group=grupo)
        self.servidor = ActionServer(
            self, IrAPunto, 'ir_a_punto', execute_callback=self.ir_a_punto,
            goal_callback=lambda _: GoalResponse.ACCEPT, callback_group=grupo)
        self.create_service(ResolverInversa, 'resolver_inversa',
                            self.resolver, callback_group=grupo)
        self.create_service(MemorizarPose, 'memorizar_pose',
                            self.memorizar, callback_group=grupo)
        self.create_service(IrAPoseMemorizada, 'ir_a_pose',
                            self.ir_a_pose, callback_group=grupo)
        self.get_logger().info(
            f'listo: accion ir_a_punto, servicios resolver_inversa, '
            f'memorizar_pose e ir_a_pose. {len(self.poses)} poses guardadas')

    # ---------------- estado y memoria ----------------
    def estado(self, msg):
        try:
            idx = [msg.name.index(n) for n in cin.EJES]
        except ValueError:
            return
        self.q = [math.degrees(msg.position[i]) for i in idx]

    def cargar(self):
        if not self.archivo or not os.path.exists(self.archivo):
            return {}
        with open(self.archivo, 'r', encoding='utf-8') as f:
            datos = yaml.safe_load(f) or {}
        return {k: [float(v) for v in q] for k, q in datos.items()}

    def guardar(self):
        if not self.archivo:
            return
        with open(self.archivo, 'w', encoding='utf-8') as f:
            yaml.safe_dump({k: [round(v, 3) for v in q]
                            for k, q in self.poses.items()}, f,
                           allow_unicode=True, sort_keys=True)

    # ---------------- servicios ----------------
    def resolver(self, pedido, respuesta):
        p = pedido.punto
        q, motivo = cin.inversa(p.x, p.y, p.z, pedido.alfa_grados)
        respuesta.alcanzable = q is not None
        respuesta.motivo = motivo
        respuesta.q = q if q else []
        self.get_logger().info(
            f'consulta ({p.x:.3f}, {p.y:.3f}, {p.z:.3f}) a {pedido.alfa_grados:.0f}'
            f' grados -> {motivo}')
        return respuesta

    def memorizar(self, pedido, respuesta):
        if self.q is None:
            respuesta.exito, respuesta.motivo = False, 'todavia no se recibio joint_states'
            return respuesta
        ok, motivo = cin.alcanzable(self.q)
        if not ok:
            respuesta.exito, respuesta.motivo = False, f'la pose actual no es valida: {motivo}'
            return respuesta
        self.poses[pedido.nombre] = list(self.q)
        self.guardar()
        respuesta.exito, respuesta.motivo, respuesta.q = True, 'ok', list(self.q)
        self.get_logger().info(f'pose "{pedido.nombre}" guardada: '
                               f'{[round(v, 1) for v in self.q]}')
        return respuesta

    def ir_a_pose(self, pedido, respuesta):
        if pedido.nombre not in self.poses:
            respuesta.exito = False
            respuesta.motivo = (f'no hay ninguna pose guardada con el nombre '
                                f'"{pedido.nombre}"')
            return respuesta
        ok, motivo = self.mover(self.poses[pedido.nombre], pedido.duracion_s)
        respuesta.exito, respuesta.motivo = ok, motivo
        return respuesta

    # ---------------- accion ----------------
    def ir_a_punto(self, meta):
        pedido = meta.request
        res = IrAPunto.Result()
        q, motivo = cin.inversa(pedido.punto.x, pedido.punto.y, pedido.punto.z,
                                pedido.alfa_grados)
        if q is None:
            self.get_logger().warn(f'meta rechazada: {motivo}')
            meta.abort()
            res.exito, res.motivo, res.q_final = False, motivo, []
            return res

        ok, motivo = self.mover(q, pedido.duracion_s, meta)
        if ok:
            meta.succeed()
        else:
            meta.abort()
        res.exito, res.motivo = ok, motivo
        res.q_final = list(self.q) if self.q else q
        return res

    # ---------------- el movimiento ----------------
    def mover(self, q_destino, duracion=0.0, meta=None):
        """Arma la trayectoria suave y se la manda al controlador."""
        if self.q is None:
            return False, 'todavia no se recibio joint_states'
        if not self.cliente.wait_for_server(timeout_sec=2.0):
            return False, 'el controlador no responde'

        minima = perfil.duracion_minima(self.q, q_destino)
        if duracion <= 0.0:
            duracion = minima
        elif duracion < minima:
            return False, (f'{duracion:.2f} s es demasiado rapido: el minimo que '
                           f'respeta los topes es {minima:.2f} s')

        tray = JointTrajectory()
        tray.joint_names = list(cin.EJES)
        for t, q in perfil.muestrear(self.q, q_destino, duracion, self.periodo):
            punto = JointTrajectoryPoint()
            punto.positions = [math.radians(v) for v in q]
            punto.time_from_start = a_duracion(t)
            tray.points.append(punto)

        v, a = perfil.picos(self.q, q_destino, duracion)
        self.get_logger().info(
            f'trayectoria de {duracion:.2f} s, {len(tray.points)} puntos: '
            f'pico {v:.2f} m/s y {a:.2f} m/s2 contra el tope de {perfil.A_TOPE:.2f}')

        objetivo = FollowJointTrajectory.Goal()
        objetivo.trajectory = tray
        fin = threading.Event()
        estado = {}

        def aceptada(fut):
            handle = fut.result()
            if not handle.accepted:
                estado['motivo'] = 'el controlador rechazo la trayectoria'
                fin.set()
                return
            handle.get_result_async().add_done_callback(terminada)

        def terminada(fut):
            r = fut.result().result
            estado['ok'] = r.error_code == FollowJointTrajectory.Result.SUCCESSFUL
            estado['motivo'] = r.error_string or 'ok'
            fin.set()

        self.cliente.send_goal_async(objetivo).add_done_callback(aceptada)

        # el ejecutor es multihilo: esperar acá no bloquea las demas devoluciones
        t0 = time.time()
        while not fin.wait(timeout=0.05):
            if time.time() - t0 > duracion + 10.0:
                return False, 'el controlador no termino a tiempo'
            if meta is not None and self.q is not None:
                fb = IrAPunto.Feedback()
                fb.progreso = min(1.0, (time.time() - t0)/duracion)
                fb.q_actual = list(self.q)
                meta.publish_feedback(fb)
        return estado.get('ok', False), estado.get('motivo', 'sin respuesta')


def main():
    rclpy.init()
    nodo = Planificador()
    ejecutor = MultiThreadedExecutor()
    ejecutor.add_node(nodo)
    try:
        ejecutor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
