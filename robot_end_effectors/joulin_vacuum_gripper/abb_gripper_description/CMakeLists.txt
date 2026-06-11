# ============================================================
# Package:     abb_gripper_description
# Description: CMake build configuration for Joulin PP-PG-160x600
#              vacuum gripper description package on ABB IRB6700
# Author:      Farzaneh Eskandari
# Email:       farzane.eskandarii@gmail.com
# Date:        2026-06-05
# ============================================================
cmake_minimum_required(VERSION 3.8)
project(abb_gripper_description)

find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)

install(DIRECTORY urdf/ DESTINATION share/${PROJECT_NAME}/urdf)
install(DIRECTORY meshes/ DESTINATION share/${PROJECT_NAME}/meshes)
install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}/launch)

ament_package()
