# abb_kinect_description

URDF/xacro description package for mounting the Azure Kinect DK on the ABB IRB6700 flange in eye-in-hand configuration. Provides modular macros to attach or remove the camera without modifying the robot URDF.

## Overview

| Real cell | RViz (point cloud in robot frame) |
|-----------|-----------------------------------|
| <img src="docs/img/real_robot.png" width="400"/> | <img src="docs/img/rviz_view.png" width="400"/> |

## Tool chain

The camera is the last element of a fully modeled flange-to-tool chain:

```
tool0
  -> flange adapter plate A (20mm)
  -> flange adapter plate B (15mm)
  -> ABB force sensor (62mm)
  -> tool-side adapter plate (4mm)
  -> SWK-160 tool changer (clocked 15 deg about Z)
  -> SWA-160 tool side -> tcp_straight (clocking cancelled)
```

The Azure Kinect mounts on the SWK-160 chamfer face. Its optical frame,
`rob1_rgb_camera_optical_frame`, is defined directly from the hand-eye
calibration result (attached to `tool0`), so the point cloud and the
ChArUco detector both operate in accurate robot coordinates.

## Hand-eye calibration

For step-by-step instructions on running the eye-in-hand hand-eye calibration
(three-terminal launch, board parameters, sampling procedure, verification, and
troubleshooting), see:

➡️ [docs/HANDEYE_CALIBRATION.md](docs/HANDEYE_CALIBRATION.md)


## Build

This package is part of the `~/ws_moveit` workspace. Build it (and the
packages it works with) from the workspace root:

```bash
cd ~/ws_moveit
colcon build --packages-select abb_kinect_description
source install/setup.bash
```

## Run

The camera + point cloud run alongside the robot/MoveIt. Each terminal:
`cd ~/ws_moveit && source install/setup.bash` first.

**Network setup (once per session):**

```bash
sudo ip addr add 192.168.0.100/24 dev enx6c1ff704db5e
ping 192.168.0.20
```

**Terminal 1 — robot + MoveIt** (publishes robot TF incl. the calibrated
`rob1_rgb_camera_optical_frame`):

```bash
ros2 launch abb_irb6700_with_rail_moveit_config demo.launch.py \
  use_fake_hardware:=false rws_ip:=192.168.0.20
```

**Terminal 2 — Azure Kinect driver + cloud bridge** (starts the camera and
connects its point cloud into the robot TF tree):

```bash
ros2 launch abb_kinect_description kinect_with_urdf.launch.py
```