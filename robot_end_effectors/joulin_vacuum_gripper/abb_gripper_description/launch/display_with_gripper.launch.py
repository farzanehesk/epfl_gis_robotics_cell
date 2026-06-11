# ============================================================
# Package:     abb_gripper_description
# File:        display_with_gripper.launch.py
# Description: Launch file to visualize ABB IRB6700 + Joulin
#              PP-PG-160x600 gripper URDF geometry in RViz.
#              Does NOT connect to real hardware.
# Author:      Farzaneh Eskandari
# Email:       farzane.eskandarii@gmail.com
# Date:        2026-06-05
# Usage:       ros2 launch abb_gripper_description display_with_gripper.launch.py
# ============================================================
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg = get_package_share_directory('abb_gripper_description')
    xacro_file = os.path.join(pkg, 'urdf', 'robot_with_gripper.urdf.xacro')
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'publish_frequency': 30.0,
            }]
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
        ),
    ])