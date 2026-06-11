# EPFL GIS Robotics Cell

ROS2 package for controlling digital I/O signals on the ABB IRC5 controller via RWS (Robot Web Services) — used for the Schunk SWS-160 tool changer and the Joulin PP-PG-160x600 vacuum gripper.

**Robot:** ABB IRB6700 175/3.05 on IRBT6004 7m rail\
**Author:** Farzaneh Eskandari\
**Email:** farzane.eskandarii@gmail.com / farzaneh.eskandari@epfl.ch
---

## Packages

### `abb_io_controller`
ROS2 I/O control for the Schunk SWS-160 tool changer and Joulin vacuum gripper via ABB RWS digital signals. See package [README](abb_io_controller/README.md) for details.

### `robot_end_effectors`
URDF/xacro descriptions for end effectors:
- Joulin PP-PG-160x600 vacuum gripper
- Schunk SWS-160 automatic tool changer (SWK-160 robot side + SWA-160 tool side)

### `robot_perception`
Perception packages for the cell, including Azure Kinect DK integration (via [Azure_Kinect_ROS_Driver](https://github.com/microsoft/Azure_Kinect_ROS_Driver) submodule).

---

## Future Development

- [ ] Additional end effectors / tool descriptions
- [ ] Perception pipelines (object detection, calibration, point cloud processing)
- [ ] Additional I/O signal mappings and feedback sensors
- [ ] Pick-and-place / task-level integration packages
- [ ] System-level launch files combining MoveIt, perception, and I/O control

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


