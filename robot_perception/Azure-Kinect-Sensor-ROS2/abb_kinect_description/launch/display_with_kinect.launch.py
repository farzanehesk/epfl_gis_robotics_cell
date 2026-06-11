# ============================================================
# Package:     abb_kinect_description
# File:        display_with_kinect.launch.py
# Description: Launch file to visualize ABB IRB6700 + Azure
#              Kinect URDF geometry in RViz. Does NOT stream
#              live camera data — use kinect_pointcloud_rviz
#              launch for live data visualization.
# Author:      Farzaneh Eskandari
# Email:       farzane.eskandarii@gmail.com
# Date:        2026-06-05
# ============================================================
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_description = get_package_share_directory('abb_kinect_description')
    xacro_file = os.path.join(pkg_description, 'urdf', 'robot_with_kinect.urdf.xacro')
    robot_description = Command(['xacro ', xacro_file])

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
            name='joint_state_publisher_gui',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
        ),
    ])
