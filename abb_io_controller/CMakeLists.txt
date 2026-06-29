# ============================================================
# Package:     abb_io_controller
# Description: ROS2 I/O control for Schunk SWS-160 tool changer
#              and Joulin vacuum gripper via ABB RWS digital signals
# Robot:       ABB IRB6700 175/3.05 on IRBT6004 7m rail
# Author:      Farzaneh Eskandari
# Email:       farzane.eskandarii@gmail.com
# Date:        2026-06-10
# ============================================================
cmake_minimum_required(VERSION 3.8)
project(abb_io_controller)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_srvs REQUIRED)
find_package(control_msgs REQUIRED)
find_package(abb_egm_rws_managers REQUIRED)

find_package(rclcpp_action REQUIRED)

add_executable(abb_io_controller_node
  src/main.cpp
  src/io_controller_node.cpp
)

target_include_directories(abb_io_controller_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(abb_io_controller_node
  rclcpp
  rclcpp_action
  std_srvs
  control_msgs
  abb_egm_rws_managers
)

install(TARGETS
  abb_io_controller_node
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
