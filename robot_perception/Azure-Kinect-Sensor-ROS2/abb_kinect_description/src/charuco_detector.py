#!/usr/bin/env python3
# ============================================================
# Package:     abb_kinect_description
# File:        charuco_detector.py
# Description: ChArUco board detector for hand-eye calibration.
#              Subscribes to RGB image + camera_info, detects the
#              ChArUco board, solves its pose, and broadcasts TF
#              tracking_base_frame -> tracking_marker_frame so that
#              easy_handeye2 can sample it.
#
#              CRITICAL: publishes the marker TF as a child of the
#              PREFIXED optical frame (rob1_rgb_camera_optical_frame),
#              so the marker lands in the MoveIt TF tree (Tree 1),
#              NOT the orphaned driver tree (Tree 2). This is what
#              makes easy_handeye2's lookupTransform succeed.
#
# Board (MEASURED, not nominal — print was scaled up on A3):
#   dictionary    : DICT_4X4_50
#   squares_x     : 5
#   squares_y     : 7
#   square_length : 0.0548  m   (measured: 274mm/5 = 38.4cm/7 = ~54.8mm)
#   marker_length : 0.04062 m   (measured marker edge = 40.62mm)
#
# Author: Farzaneh Eskandari
# Email:       farzane.eskandarii@gmail.com
# Date:        2026-06-18
# ============================================================
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped, TransformStamped
from tf2_ros import TransformBroadcaster
from cv_bridge import CvBridge
import numpy as np
import cv2
from cv2 import aruco
from scipy.spatial.transform import Rotation as R


class CharucoDetector(Node):
    def __init__(self):
        super().__init__('charuco_detector')

        # ---- Parameters (override from launch) -------------
        self.declare_parameter('squares_x', 5)
        self.declare_parameter('squares_y', 7)
        self.declare_parameter('square_length', 0.0548)
        self.declare_parameter('marker_length', 0.04062)
        self.declare_parameter('dictionary', 'DICT_4X4_50')
        self.declare_parameter('image_topic', '/rgb/image_raw')
        self.declare_parameter('camera_info_topic', '/rgb/camera_info')
        # IMPORTANT: this must be the PREFIXED optical frame (Tree 1)
        self.declare_parameter('camera_frame', 'rob1_rgb_camera_optical_frame')
        self.declare_parameter('marker_frame', 'rob1_charuco_board')
        self.declare_parameter('publish_debug_image', True)

        self.squares_x = self.get_parameter('squares_x').value
        self.squares_y = self.get_parameter('squares_y').value
        self.square_length = self.get_parameter('square_length').value
        self.marker_length = self.get_parameter('marker_length').value
        dict_name = self.get_parameter('dictionary').value
        self.camera_frame = self.get_parameter('camera_frame').value
        self.marker_frame = self.get_parameter('marker_frame').value
        self.publish_debug = self.get_parameter('publish_debug_image').value

        # ---- ChArUco board (OpenCV 4.7+ API) ---------------
        self.aruco_dict = aruco.getPredefinedDictionary(getattr(aruco, dict_name))
        self.board = aruco.CharucoBoard(
            (self.squares_x, self.squares_y),
            self.square_length,
            self.marker_length,
            self.aruco_dict,
        )
        # CharucoDetector wraps marker + corner interpolation
        self.detector = aruco.CharucoDetector(self.board)

        self.bridge = CvBridge()
        self.camera_matrix = None
        self.dist_coeffs = None

        self.tf_broadcaster = TransformBroadcaster(self)
        self.pose_pub = self.create_publisher(PoseStamped, '~/pose', 10)
        if self.publish_debug:
            self.debug_pub = self.create_publisher(Image, '~/debug_image', 10)

        self.create_subscription(
            CameraInfo, self.get_parameter('camera_info_topic').value,
            self.info_cb, 10)
        self.create_subscription(
            Image, self.get_parameter('image_topic').value,
            self.image_cb, 10)

        self.get_logger().info(
            f'ChArUco detector up: {self.squares_x}x{self.squares_y}, '
            f'square={self.square_length}m marker={self.marker_length}m {dict_name}')
        self.get_logger().info(
            f'Publishing TF: {self.camera_frame} -> {self.marker_frame}')

    def info_cb(self, msg: CameraInfo):
        if self.camera_matrix is None:
            self.camera_matrix = np.array(msg.k, dtype=np.float64).reshape(3, 3)
            self.dist_coeffs = np.array(msg.d, dtype=np.float64)
            self.get_logger().info('Camera intrinsics received.')

    def image_cb(self, msg: Image):
        # Crash guard: a single degenerate frame (bad solvePnP input,
        # cv_bridge encoding hiccup, empty corners) must NOT kill the
        # whole node — that freezes the board TF and breaks sampling.
        try:
            self._image_cb_impl(msg)
        except Exception as e:
            self.get_logger().warn(
                f'Skipped frame due to error: {e}',
                throttle_duration_sec=2.0)

    def _image_cb_impl(self, msg: Image):
        if self.camera_matrix is None:
            self.get_logger().warn('Waiting for camera_info...', throttle_duration_sec=2.0)
            return

        img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # detectBoard returns interpolated charuco corners + ids
        charuco_corners, charuco_ids, marker_corners, marker_ids = \
            self.detector.detectBoard(gray)

        # solvePnP's DLT algorithm needs >= 6 point correspondences.
        # Use 8 as a safety margin for pose stability.
        MIN_CORNERS = 8
        if charuco_ids is None or len(charuco_ids) < MIN_CORNERS:
            n = 0 if charuco_ids is None else len(charuco_ids)
            self.get_logger().warn(
                f'Board not well detected ({n} corners, need >={MIN_CORNERS}).',
                throttle_duration_sec=2.0)
            if self.publish_debug:
                self._publish_debug(img, marker_corners, marker_ids, None)
            return

        # Solve board pose
        obj_pts, img_pts = self.board.matchImagePoints(charuco_corners, charuco_ids)
        if obj_pts is None or len(obj_pts) < MIN_CORNERS:
            return
        ok, rvec, tvec = cv2.solvePnP(
            obj_pts, img_pts, self.camera_matrix, self.dist_coeffs)
        if not ok:
            return

        # Build TF: camera_optical_frame -> charuco_board
        rot = R.from_rotvec(rvec.flatten()).as_quat()  # xyzw
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = self.camera_frame      # PREFIXED -> Tree 1
        t.child_frame_id = self.marker_frame
        t.transform.translation.x = float(tvec[0])
        t.transform.translation.y = float(tvec[1])
        t.transform.translation.z = float(tvec[2])
        t.transform.rotation.x = float(rot[0])
        t.transform.rotation.y = float(rot[1])
        t.transform.rotation.z = float(rot[2])
        t.transform.rotation.w = float(rot[3])
        self.tf_broadcaster.sendTransform(t)

        # Also publish PoseStamped (handy for debugging)
        p = PoseStamped()
        p.header = t.header
        p.pose.position.x = t.transform.translation.x
        p.pose.position.y = t.transform.translation.y
        p.pose.position.z = t.transform.translation.z
        p.pose.orientation = t.transform.rotation
        self.pose_pub.publish(p)

        self.get_logger().info(
            f'Board pose: t=[{tvec[0,0]:.3f},{tvec[1,0]:.3f},{tvec[2,0]:.3f}] '
            f'({len(charuco_ids)} corners)',
            throttle_duration_sec=1.0)

        if self.publish_debug:
            self._publish_debug(img, marker_corners, marker_ids,
                                (charuco_corners, charuco_ids, rvec, tvec))

    def _publish_debug(self, img, marker_corners, marker_ids, pose):
        dbg = img.copy()
        if marker_ids is not None:
            aruco.drawDetectedMarkers(dbg, marker_corners, marker_ids)
        if pose is not None:
            charuco_corners, charuco_ids, rvec, tvec = pose
            aruco.drawDetectedCornersCharuco(dbg, charuco_corners, charuco_ids)
            cv2.drawFrameAxes(dbg, self.camera_matrix, self.dist_coeffs,
                              rvec, tvec, self.square_length)
        self.debug_pub.publish(self.bridge.cv2_to_imgmsg(dbg, encoding='bgr8'))


def main():
    rclpy.init()
    node = CharucoDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()