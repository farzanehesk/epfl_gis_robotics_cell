# ============================================================
# Package:     abb_force_sensor_description
# Author:      Farzaneh Eskandari
# Institution: EPFL
# Email:       farzane.eskandarii@gmail.com - farzaneh.eskandari@epfl.ch
# Date:        2026-06-19
# ============================================================
cmake_minimum_required(VERSION 3.8)
project(abb_force_sensor_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()