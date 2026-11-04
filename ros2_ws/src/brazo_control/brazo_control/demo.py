#!/usr/bin/env python3
"""La demostración, automatizada: tomar el vaso de un punto y depositarlo en otro.

Es un cliente: no sabe nada de cinemática ni de trayectorias, sólo pide puntos.
Toda la cuenta está del otro lado, en el planificador, y eso es a propósito —si
mañana el brazo cambia, este archivo no se toca—.

    ros2 run brazo_control demo
"""
import math
import sys

import rclpy
from brazo_interfaces.action import IrAPunto
from brazo_interfaces.srv import MemorizarPose
from geometry_msgs.msg import Point
from rclpy.action import ActionClient
from rclpy.node import Node

R_VASO, Z_GARRA, Z_ALTO = 0.250, 0.070, 0.170     # m
ANG_TOMA, ANG_DEPOSITO = 35.0, 82.0               # grados de base

PASOS = [('acercarse sobre el vaso', ANG_TOMA, Z_ALTO),
         ('bajar a tomarlo', ANG_TOMA, Z_GARRA),
         ('levantar', ANG_TOMA, Z_ALTO),
         ('trasladar girando la base', ANG_DEPOSITO, Z_ALTO),
         ('bajar a depositar', ANG_DEPOSITO, Z_GARRA),
         ('retirarse', ANG_DEPOSITO, Z_ALTO)]


class Demo(Node):

    def __init__(self):
        super().__init__('demo')
        self.cliente = ActionClient(self, IrAPunto, 'ir_a_punto')
        self.memoria = self.create_client(MemorizarPose, 'memorizar_pose')

    def ir(self, nombre, grados, z):
        punto = Point(x=R_VASO*math.cos(math.radians(grados)),
                      y=R_VASO*math.sin(math.radians(grados)), z=z)
        meta = IrAPunto.Goal(punto=punto, alfa_grados=90.0, duracion_s=0.0)
        self.get_logger().info(
            f'{nombre}: ({punto.x*1000:.0f}, {punto.y*1000:.0f}, {punto.z*1000:.0f}) mm')

        fut = self.cliente.send_goal_async(meta)
        rclpy.spin_until_future_complete(self, fut)
        handle = fut.result()
        if not handle.accepted:
            self.get_logger().error('  la meta fue rechazada')
            return False
        fut_res = handle.get_result_async()
        rclpy.spin_until_future_complete(self, fut_res)
        res = fut_res.result().result
        if not res.exito:
            self.get_logger().error(f'  no se pudo: {res.motivo}')
            return False
        self.get_logger().info(
            f'  listo, q = {[round(v, 1) for v in res.q_final]}')
        return True

    def memorizar(self, nombre):
        if not self.memoria.wait_for_service(timeout_sec=2.0):
            return
        fut = self.memoria.call_async(MemorizarPose.Request(nombre=nombre))
        rclpy.spin_until_future_complete(self, fut)
        r = fut.result()
        self.get_logger().info(f'pose "{nombre}": {r.motivo}')


def main():
    rclpy.init()
    nodo = Demo()
    if not nodo.cliente.wait_for_server(timeout_sec=10.0):
        nodo.get_logger().error('el planificador no responde: ¿está levantado?')
        nodo.destroy_node()
        rclpy.try_shutdown()
        return 1

    salida = 0
    for i, (nombre, grados, z) in enumerate(PASOS):
        if not nodo.ir(f'{i + 1}. {nombre}', grados, z):
            salida = 1
            break
        if i == 1:                      # ya en el punto de agarre: lo memorizo
            nodo.memorizar('agarre')
    else:
        nodo.get_logger().info('demostración completa')

    nodo.destroy_node()
    rclpy.try_shutdown()
    return salida


if __name__ == '__main__':
    sys.exit(main())
