# Hand-Eye Calibration — Azure Kinect (eye-in-hand) on ABB IRB6700

This document describes how to run the eye-in-hand hand-eye calibration for the
Azure Kinect DK mounted on the SWK-160 tool changer of the ABB IRB6700 175/3.05.

The calibration computes the fixed transform between the robot flange (`rob1_tool0`)
and the camera optical frame (`rob1_rgb_camera_optical_frame`), so the camera can be
used for vision-guided tasks in the robot's coordinate system.

---

## Prerequisites

- ROS2 Humble workspace built and sourced (`~/ws_moveit`).
- Robot reachable over the network (IRC5 at `192.168.0.20`).
- Azure Kinect connected via USB.
- Printed ChArUco board, rigidly mounted (clamp / stand — must NOT move during sampling).
- `numpy < 2` in the environment (Humble's cv_bridge / cv2 are built against NumPy 1.x).

### ChArUco board parameters (MEASURED — board was scaled on A3 print)

| Parameter      | Value      |
|----------------|------------|
| dictionary     | DICT_4X4_50 |
| squares_x      | 5          |
| squares_y      | 7          |
| square_length  | 0.0548 m   |
| marker_length  | 0.04062 m  |

> These are the *measured* physical sizes, not the nominal design sizes.
> Always re-measure if the board is reprinted, and update
> `kinect_handeyecalib.launch.py` accordingly.


---

## Three-terminal launch

All terminals: `cd ~/ws_moveit && source install/setup.bash` first.

**T1 — robot + MoveIt (provides robot TF: `rob1_axis -> rob1_tool0`):**
```bash
ros2 launch abb_irb6700_with_rail_moveit_config demo.launch.py \
  use_fake_hardware:=false rws_ip:=192.168.0.20
```

**T2 — Azure Kinect driver only (no robot_description overwrite):**
```bash
ros2 launch abb_kinect_description kinect_with_urdf.launch.py
```

**T3 — ChArUco detector + easy_handeye2 server + rqt calibrator:**
```bash
ros2 launch abb_kinect_description kinect_handeyecalib.launch.py
```

---

## Verify before sampling

```bash
# 1. Camera is streaming:
ros2 topic hz /rgb/image_raw

# 2. Detector sees the board and publishes its pose:
ros2 topic echo /charuco_detector/pose --once

# 3. The marker frame is connected in the TF tree (THE key check):
ros2 run tf2_ros tf2_echo rob1_rgb_camera_optical_frame rob1_charuco_board
```

If step 3 returns a transform (not "frames not connected"), the pipeline is ready.

Optional — watch the detection overlay (marker boxes + corner dots + drawn axis):
```bash
ros2 run rqt_image_view rqt_image_view
# select /charuco_detector/debug_image
```

---

## Taking samples (rqt calibrator window)

easy_handeye2 computes the calibration continuously — there is **no Compute button**.
Just take samples and Save.

1. Move the robot to a new pose; keep the board well in view (healthy corner count).
2. Let the robot fully settle (no motion).
3. Click **Take Sample**.
4. Repeat for **15-20 samples**.

**Sample quality rules:**
- Vary **orientation** aggressively (tilt, roll, approach direction), not just position.
  Rotational diversity is what constrains the solution.
- Keep the board **rigidly fixed** for the entire session.
- Stay in the detection sweet spot (~50-80 cm, full board visible, >= 8 corners).
- Avoid robot poses near singularities / joint limits (SafeMove / supervision faults).

When done: **Save**. Result is written to:
```
~/.ros2/easy_handeye2/calibrations/abb_irb6700_kinect_eih.calib
```

---

## After calibration

- Inspect the result:
  ```bash
  cat ~/.ros2/easy_handeye2/calibrations/abb_irb6700_kinect_eih.calib
  ```
- Publish it and verify visually with the point cloud in RViz:
  ```bash
  ros2 launch easy_handeye2 publish.launch.py name:=abb_irb6700_kinect_eih
  ```
  In RViz set Fixed Frame to `rob1_axis`, add a PointCloud2 display, and check
  the board in the cloud lines up with its real-world location.
- Revert the `MoveAbsJ home` comment in RAPID.

---

## Notes / troubleshooting

- **"frames not connected"** in handeye_server → the detector is not publishing
  `rob1_charuco_board` (board not detected, or detector died). Check the T3 terminal.
- **detector crashes on a bad frame** → the node guards against < 8 corners and wraps
  each frame in try/except; if it still dies, check the traceback in T3.
- **camera_info frame mismatch** → the detector publishes the marker as a child of
  `rob1_rgb_camera_optical_frame` (the MoveIt/prefixed tree), so the marker pose lands
  in the same tree the robot uses. Do not point it at the driver's unprefixed frames.
- The kinematic chain now includes the **ABB force sensor (62mm) + adapter plate (4mm)**
  between `tool0` and the SWK-160. Calibrations taken before this change are stale and
  must be redone.
