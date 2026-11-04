"""Muestra el brazo en RViz 2.

    ros2 launch brazo_description display.launch.py              # sliders
    ros2 launch brazo_description display.launch.py modo:=tarea  # la tarea completa

Con 'sliders' levanta joint_state_publisher_gui, que da un control por
articulacion con los topes del URDF ya puestos. Con 'tarea' corre el nodo
tarea.py, que publica la trayectoria de tomar el vaso y depositarlo.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

PAQUETE = 'brazo_description'


def generate_launch_description():
    share = get_package_share_directory(PAQUETE)
    urdf = os.path.join(share, 'urdf', 'brazo.urdf')
    rviz = os.path.join(share, 'rviz', 'brazo.rviz')

    with open(urdf, 'r', encoding='utf-8') as f:
        descripcion = f.read()

    modo = LaunchConfiguration('modo')
    es_tarea = PythonExpression(["'", modo, "' == 'tarea'"])
    es_sliders = PythonExpression(["'", modo, "' == 'sliders'"])

    return LaunchDescription([
        DeclareLaunchArgument(
            'modo', default_value='sliders',
            description="'sliders' para mover cada eje a mano, 'tarea' para "
                        "reproducir la secuencia completa"),

        # publica las transformadas de todos los eslabones a partir del URDF
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             name='robot_state_publisher', output='screen',
             parameters=[{'robot_description': descripcion}]),

        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui',
             name='joint_state_publisher_gui', condition=IfCondition(es_sliders)),

        Node(package=PAQUETE, executable='tarea.py', name='tarea',
             output='screen', condition=IfCondition(es_tarea)),

        Node(package='rviz2', executable='rviz2', name='rviz2',
             arguments=['-d', rviz], output='screen'),
    ])
