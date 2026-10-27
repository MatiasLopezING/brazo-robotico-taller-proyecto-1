cmake_minimum_required(VERSION 3.8)
project(brazo_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME})

install(PROGRAMS
  scripts/tarea.py
  scripts/verifica_urdf.py
  scripts/genera_urdf.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
