

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('abb_io_controller'),
        'config',
        'rws_credentials.yaml'
    )

    return LaunchDescription([
        Node(
            package='abb_io_controller',
            executable='abb_io_controller_node',
            name='abb_io_controller_node',
            parameters=[config],
            output='screen'
        )
    ])