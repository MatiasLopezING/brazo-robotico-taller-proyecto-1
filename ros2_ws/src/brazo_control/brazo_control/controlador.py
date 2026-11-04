#!/usr/bin/env python3
"""Controlador del brazo: expone la interfaz estandar de un manipulador.

Ofrece la accion `control_msgs/FollowJointTrajectory`, que es lo que exponen los
drivers de los robots industriales y lo que hablan MoveIt y
`joint_trajectory_controller`. Encima de esa interfaz se puede montar cualquier
cosa; debajo, hoy, hay una simulacion cinematica, y manana un puente serie a la
EDU-CIAA o un `ros2_control`. Esa es la unica razon por la que este nodo existe
separado del planificador: para que el cambio de abajo no toque nada de arriba.

Antes de aceptar una trayectoria la revisa entera, punto por punto: ventanas de
recorrido (ADR-010) y guarda contra la caja base. Si un punto no pasa, RECHAZA
la meta y dice cual y por que. Es *guarded motion* en el sentido del control
supervisor: el operador manda, el sistema no ejecuta lo que lo dañaria.
"""
import math
import time

import rclpy
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState

from . import cinematica as cin


def a_segundos(d):
    return d.sec + d.nanosec*1e-9


class Controlador(Node):

    def __init__(self):
        super().__init__('controlador')
        self.declare_parameter('periodo', 0.02)
        self.declare_parameter('pose_inicial', [0.0, 90.0, 60.0, -60.0])
        self.declare_parameter('apertura_pinza', 62.0)

        self.periodo = self.get_parameter('periodo').value
        self.q = list(self.get_parameter('pose_inicial').value)      # grados
        self.pinza = math.radians(self.get_parameter('apertura_pinza').value)

        ok, motivo = cin.alcanzable(self.q)
        if not ok:
            self.get_logger().warn(f'la pose inicial no es valida: {motivo}')

        grupo = ReentrantCallbackGroup()
        self.pub = self.create_publisher(JointState, 'joint_states', 10)
        self.create_timer(self.periodo, self.publicar, callback_group=grupo)
        self.servidor = ActionServer(
            self, FollowJointTrajectory, 'follow_joint_trajectory',
            execute_callback=self.ejecutar, goal_callback=self.revisar,
            cancel_callback=lambda _: CancelResponse.ACCEPT,
            callback_group=grupo)
        self.cancelar = False
        self.get_logger().info(
            'listo: accion follow_joint_trajectory, estado en /joint_states')

    # ---------------- estado ----------------
    def publicar(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(cin.EJES) + ['dedo_izq', 'dedo_der']
        msg.position = [math.radians(v) for v in self.q] + [self.pinza]*2
        self.pub.publish(msg)

    # ---------------- la guarda, antes de aceptar ----------------
    def revisar(self, pedido):
        # rclpy le pasa a goal_callback el mensaje Goal, no el handle
        tray = pedido.trajectory
        if not tray.points:
            self.get_logger().warn('trayectoria vacia')
            return GoalResponse.REJECT
        if list(tray.joint_names) != list(cin.EJES):
            self.get_logger().warn(f'nombres de articulacion inesperados: '
                                   f'{list(tray.joint_names)}')
            return GoalResponse.REJECT
        for i, p in enumerate(tray.points):
            q = [math.degrees(v) for v in p.positions]
            ok, motivo = cin.alcanzable(q)
            if not ok:
                self.get_logger().warn(f'trayectoria rechazada en el punto {i}: {motivo}')
                return GoalResponse.REJECT
        self.get_logger().info(f'trayectoria aceptada: {len(tray.points)} puntos, '
                               f'{a_segundos(tray.points[-1].time_from_start):.2f} s')
        return GoalResponse.ACCEPT

    # ---------------- ejecucion ----------------
    def ejecutar(self, meta):
        tray = meta.request.trajectory
        res = FollowJointTrajectory.Result()
        t0 = self.get_clock().now()
        for p in tray.points:
            if meta.is_cancel_requested:
                meta.canceled()
                res.error_code = FollowJointTrajectory.Result.SUCCESSFUL
                res.error_string = 'cancelada por el cliente'
                return res
            # el ejecutor es multihilo, asi que dormir acá no frena ni la
            # publicacion de estado ni la atencion de otras metas
            falta = (a_segundos(p.time_from_start)
                     - (self.get_clock().now() - t0).nanoseconds*1e-9)
            if falta > 0.0:
                time.sleep(falta)
            self.q = [math.degrees(v) for v in p.positions]

            fb = FollowJointTrajectory.Feedback()
            fb.joint_names = list(cin.EJES)
            fb.desired, fb.actual = p, p
            meta.publish_feedback(fb)

        meta.succeed()
        res.error_code = FollowJointTrajectory.Result.SUCCESSFUL
        res.error_string = 'ok'
        return res


def main():
    rclpy.init()
    nodo = Controlador()
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
