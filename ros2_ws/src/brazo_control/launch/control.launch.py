"""Levanta el brazo completo: controlador, planificador y RViz 2.

    ros2 launch brazo_control control.launch.py
    ros2 launch brazo_control control.launch.py demo:=true

Debajo del controlador hoy hay una simulación cinemática. El día que exista el
brazo, lo que se reemplaza es ese nodo —o se pasa a `ros2_control` con un
`hardware_interface` que hable con la EDU-CIAA por puerto serie—: el
planificador, la demostración y RViz no se enteran, porque todos hablan con la
interfaz estándar `FollowJointTrajectory`.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    desc = get_package_share_directory('brazo_description')
    ctrl = get_package_share_directory('brazo_control')
    urdf = os.path.join(desc, 'urdf', 'brazo.urdf')
    rviz = os.path.join(desc, 'rviz', 'brazo.rviz')
    poses = os.path.join(ctrl, 'config', 'poses.yaml')

    with open(urdf, 'r', encoding='utf-8') as f:
        descripcion = f.read()

    return LaunchDescription([
        DeclareLaunchArgument('demo', default_value='false',
                              description='correr la demostración al levantar'),
        DeclareLaunchArgument('poses', default_value=poses,
                              description='archivo de poses memorizadas'),

        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': descripcion}], output='screen'),

        Node(package='brazo_control', executable='controlador', name='controlador',
             output='screen'),

        Node(package='brazo_control', executable='planificador', name='planificador',
             output='screen',
             parameters=[{'archivo_poses': LaunchConfiguration('poses')}]),

        Node(package='brazo_control', executable='demo', name='demo', output='screen',
             condition=IfCondition(LaunchConfiguration('demo'))),

        Node(package='rviz2', executable='rviz2', arguments=['-d', rviz],
             output='screen'),
    ])
