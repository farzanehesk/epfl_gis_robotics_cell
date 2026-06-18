# ============================================================
# Package:     abb_kinect_description
# File:        kinect_handeyecalib.launch.py
# Description: Hand-eye calibration launch for Azure Kinect
#              eye-in-hand on ABB IRB6700.
#              Uses easy_handeye2 with ArUco/ChArUco tracking.
#
# Usage:
#   Terminal 1: ros2 launch abb_irb6700_with_rail_moveit_config demo.launch.py use_fake_hardware:=false rws_ip:=192.168.0.20
#   Terminal 2: ros2 launch abb_kinect_description kinect_with_urdf.launch.py
#   Terminal 3: ros2 launch abb_kinect_description kinect_handeyecalib.launch.py
#
# Result is saved to ~/.ros/easy_handeye2/abb_irb6700_kinect_eih.yaml

# Author:      Farzaneh Eskandari
# Email:       farzane.eskandarii@gmail.com
# Date:        2026-06-15
# ============================================================
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():

    # --------------------------------------------------------
    # ChArUco detector node
    # Detects the ChArUco board in the RGB image and publishes
    # the board pose as a TF frame.
    # Run straight from source so no rebuild is needed.
    # --------------------------------------------------------
    charuco_detector = ExecuteProcess(
        cmd=['python3',
             '/home/farzaneh/ws_moveit/src/Robotics/epfl_gis_robotics_cell/robot_perception/'
             'Azure-Kinect-Sensor-ROS2/abb_kinect_description/src/charuco_detector.py',
             '--ros-args',
             '-p', 'square_length:=0.0548',
             '-p', 'marker_length:=0.04062',
             '-p', 'squares_x:=5',
             '-p', 'squares_y:=7',
             '-p', 'dictionary:=DICT_4X4_50',
             '-p', 'camera_frame:=rob1_rgb_camera_optical_frame',
             '-p', 'marker_frame:=rob1_charuco_board',
             '-p', 'image_topic:=/rgb/image_raw',
             '-p', 'camera_info_topic:=/rgb/camera_info',
        ],
        output='screen',
    )

    # --------------------------------------------------------
    # easy_handeye2 calibration server + rqt GUI
    # --------------------------------------------------------
    handeye_server = Node(
        package='easy_handeye2',
        executable='handeye_server',
        name='handeye_server',
        parameters=[{
            'name':                   'abb_irb6700_kinect_eih',
            'calibration_type':       'eye_in_hand',
            'tracking_base_frame':    'rob1_rgb_camera_optical_frame',
            'tracking_marker_frame':  'rob1_charuco_board',
            'robot_base_frame':       'rob1_axis',
            'robot_effector_frame':   'rob1_tool0',
        }]
    )
 
    handeye_gui = Node(
        package='easy_handeye2',
        executable='rqt_calibrator.py',
        name='handeye_rqt_calibrator',
        parameters=[{
            'name':                   'abb_irb6700_kinect_eih',
            'calibration_type':       'eye_in_hand',
            'tracking_base_frame':    'rob1_rgb_camera_optical_frame',
            'tracking_marker_frame':  'rob1_charuco_board',
            'robot_base_frame':       'rob1_axis',
            'robot_effector_frame':   'rob1_tool0',
        }]
    )
 
    return LaunchDescription([
        charuco_detector,
        handeye_server,
        handeye_gui,
    ])
 