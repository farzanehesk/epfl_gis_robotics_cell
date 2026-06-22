# EPFL GIS Robotics Cell

ROS2 package for controlling digital I/O signals on the ABB IRC5 controller via RWS (Robot Web Services) — used for the Schunk SWS-160 tool changer and the Joulin PP-PG-160x600 vacuum gripper.

Robot: ABB IRB6700 175/3.05 on IRBT6004 7m rail\
Author: Farzaneh Eskandari\
Email: farzane.eskandarii@gmail.com / farzaneh.eskandari@epfl.ch


## Packages

### `abb_io_controller`
ROS2 digital I/O control via ABB RWS (Robot Web Services). Provides services and
actions for the Schunk SWS-160 tool changer (lock/unlock) and the Joulin
PP-PG-160x600 vacuum gripper. See the package [README](abb_io_controller/README.md).

### `robot_end_effectors`
URDF/xacro descriptions for end effectors:
- **`joulin_vacuum_gripper`** — Joulin PP-PG-160x600 vacuum gripper.
- **`schunk_tool_changer`** — Schunk SWS-160 automatic tool changer (SWK-160
  robot side + SWA-160 tool side), including the `tcp_straight` frame that
  cancels the changer's mounting clocking.

### `robot_force_sensor`
Description of the ABB force sensor stack mounted between the robot flange and
the tool changer.
- **`abb_force_sensor_description`** — URDF/xacro for the ABB force sensor
  (large, 3HAC091307-001/02) plus the two flange-side adapter plates. Outputs
  the `force_adapter_mount` frame where the tool changer attaches.
- *(planned)* interface/driver package for reading force/torque data.

### `robot_perception`
Perception packages for the cell:
- **`Azure-Kinect-Sensor-ROS2`** — Azure Kinect DK integration (eye-in-hand),
  including camera description, the hand-eye calibration pipeline (ChArUco
  detector + easy_handeye2), and the point-cloud bridge into the robot TF tree.
  Uses the [Azure_Kinect_ROS_Driver](https://github.com/microsoft/Azure_Kinect_ROS_Driver)
  submodule. See its [README](robot_perception/Azure-Kinect-Sensor-ROS2/abb_kinect_description/README.md)
  for build/run and [HANDEYE_CALIBRATION_iNSTRUCTIONS](robot_perception/Azure-Kinect-Sensor-ROS2/abb_kinect_description/docs/HANDEYE_CALIBRATION.md)for calibration instructions. 
- **`easy_handeye2`** — hand-eye calibration framework (submodule).

---
## Tool chain

The full flange-to-tool kinematic chain, modeled across the description packages:

```
tool0
  -> flange adapter plate A (20mm)
  -> flange adapter plate B (15mm)
  -> ABB force sensor (62mm)
  -> tool-side adapter plate (4mm)
  -> SWK-160 tool changer (mounted with 15 deg clocking about Z)
  -> SWA-160 tool side
  -> tcp_straight (clocking cancelled; nominal-aligned TCP for all tools)
```

The Azure Kinect mounts on the SWK-160 chamfer face (eye-in-hand). Its optical
frame is defined directly from the hand-eye calibration, so perception data is
expressed in accurate robot coordinates.

---

## Setup

```bash
git clone --recurse-submodules git@github.com:farzanehesk/epfl_gis_robotics_cell.git
```


If already cloned without submodules:
```bash
git submodule update --init --recursive
```

Build:
```bash
cd ~/ws_moveit
colcon build
source install/setup.bash
```


## Future Development

- [ ] Force/torque interface package (read sensor data into ROS2 as WrenchStamped)
- [ ] Per-tool TCP definitions below `tcp_straight` (vacuum gripper, sharp tools)
- [ ] Perception pipelines (object detection, point cloud segmentation, octomap)
- [ ] Additional end effectors / tool descriptions
- [ ] Additional I/O signal mappings and feedback sensors
- [ ] Pick-and-place / task-level integration packages
- [ ] System-level launch files combining MoveIt, perception, and I/O control
- [ ] Full two-robot synchronized system (two IRB6700s, two rails, spindle)
