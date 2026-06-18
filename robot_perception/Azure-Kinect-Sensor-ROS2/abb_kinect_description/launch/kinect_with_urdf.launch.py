# ============================================================
# Package:     abb_kinect_description
# File:        kinect_with_urdf.launch.py
# Description: Launches Azure Kinect driver WITHOUT overwriting
#              robot_description. Terminal 1 (MoveIt) already
#              publishes the full robot TF including camera frames.
#              This launch only starts the k4a sensor node.
# Usage:       ros2 launch abb_kinect_description kinect_with_urdf.launch.py
# ============================================================
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

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

    return LaunchDescription([
        kinect_driver,
    ])