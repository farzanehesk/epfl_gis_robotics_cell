# ============================================================
# Package:     abb_kinect_description
# File:        kinect_with_urdf.launch.py
# Description: Launches Azure Kinect driver WITHOUT overwriting
#              robot_description, and bridges the driver's camera
#              tree into the robot TF tree at the hand-eye
#              calibrated camera frame so the point cloud appears
#              correctly in the robot/world frame.
#              Terminal 1 (MoveIt) publishes the robot TF including
#              the calibrated rob1_rgb_camera_optical_frame.
# Usage:       ros2 launch abb_kinect_description kinect_with_urdf.launch.py
# Author:      Farzaneh Eskandari
# Institution: EPFL
# Email:       farzane.eskandarii@gmail.com - farzaneh.eskandari@epfl.ch
# Date:        2026-06-19
# ============================================================
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg_driver = get_package_share_directory('azure_kinect_ros_driver')

    # Launch driver with overwrite_robot_description:=false
    # so it does NOT start its own robot_state_publisher
    # which would overwrite the MoveIt robot_description TF
    kinect_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_driver, 'launch', 'driver.launch.py')
        ),
        launch_arguments={
            'overwrite_robot_description': 'false'
        }.items()
    )

    # Bridge the driver's camera tree (orphan: camera_base -> ... ->
    # rgb_camera_link) into the robot TF tree. Attaches camera_base under
    # the calibrated rob1_rgb_camera_optical_frame using the driver's own
    # internal rgb_camera_link -> camera_base transform, so rgb_camera_link
    # (the point cloud frame) coincides with the calibrated optical frame.
    # This makes /points2 display correctly in the world/robot frame.
    cloud_bridge = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='kinect_cloud_bridge',
        arguments=[
            '--x', '-0.032', '--y', '0.0', '--z', '0.004',
            '--qx', '0.499', '--qy', '-0.502', '--qz', '0.498', '--qw', '0.501',
            '--frame-id', 'rob1_rgb_camera_optical_frame',
            '--child-frame-id', 'camera_base',
        ],
    )

    return LaunchDescription([
        kinect_driver,
        cloud_bridge,
    ])