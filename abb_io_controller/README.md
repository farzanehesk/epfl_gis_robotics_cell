# abb_io_controller

ROS2 package for controlling digital I/O signals on the ABB IRC5 controller via RWS (Robot Web Services) — used for the Schunk SWS-160 tool changer and the Joulin PP-PG-160x600 vacuum gripper.

**Robot:** ABB IRB6700 175/3.05 on IRBT6004 7m rail\
**Author:** Farzaneh Eskandari (farzane.eskandarii@gmail.com)

---

## Overview

This package exposes ROS2 services and an action server that write to the IRC5's `Local_IO` digital I/O module (ABB **DSQC1030** Scalable I/O base device) via RWS.

It uses `RWSManager::runPriorityService()` to call `RWSStateMachineInterface::setIOSignal(name, value)`.

---

## Hardware reference

I/O module: **ABB DSQC1030** (Digital base device, 16 DI / 16 DO)

Official manual:
[ABB Scalable I/O – Application Manual (3HAC070208-001)](https://search.abb.com/library/Download.aspx?DocumentID=3HAC070208-001&LanguageCode=en&DocumentPartId=&Action=Launch)


<img src="Screenshot%20from%202026-06-12%2010-49-42.png" alt="alt text" width="50%"> 
<img src="Screenshot%20from%202026-06-12%2010-50-26.png" alt="alt text" width="50%">


---

## Interfaces


## Confirmed I/O signal mapping

| Signal | RWS name | Function | Polarity |
|---|---|---|---|
| DO1 | `Local_IO_0_DO1` | Vacuum gripper air supply | `1` = air on (grip), `0` = off (release) |
| DO9 | `Local_IO_0_DO9` | SWS-160 tool changer | `1` = release/unlock, `0` = locked |

Mapping verified on-site (2026-06-11) on the IRC5 controller at `192.168.0.20`, `Local_IO` EtherNetIP module (DSQC1030).

---
## TODO — Additional DO documentation

- [ ] Document remaining unused DOs (DO2-DO8, DO10-DO16) and DIs (DI1-DI16) — physical wiring status, candidate functions
- [ ] Add DI feedback signals if available (e.g. tool changer "locked" sensor, vacuum "part present" sensor)
- [ ] Document how to set/read a signal manually via RWS for debugging:

```bash
  # Read signal value
  curl -s --digest -u "Default User:robotics" \
    "http://192.168.0.20/rw/iosystem/signals/EtherNetIP/Local_IO/Local_IO_0_DOx" \
    -H "Accept: application/xhtml+xml" | grep lvalue

  # Set signal value
  curl -s --digest -u "Default User:robotics" \
    "http://192.168.0.20/rw/iosystem/signals/EtherNetIP/Local_IO/Local_IO_0_DOx/?action=set" \
    -H "Accept: application/xhtml+xml" --data "lvalue=1"
```

- [ ] Add wiring diagram / photos of the physical I/O cabinet for reference


---

## Build & Run

```bash
cd ~/ws_moveit
colcon build --packages-select abb_io_controller
source install/setup.bash
ros2 run abb_io_controller abb_io_controller_node
```

## Test commands

```bash
# Vacuum gripper: grip
ros2 action send_goal /gripper/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 1.0, max_effort: 0.0}}"

# Vacuum gripper: release
ros2 action send_goal /gripper/gripper_cmd control_msgs/action/GripperCommand "{command: {position: 0.0, max_effort: 0.0}}"

# Tool changer: unlock
ros2 service call /tool_changer/unlock std_srvs/srv/Trigger

# Tool changer: lock
ros2 service call /tool_changer/lock std_srvs/srv/Trigger
```

⚠️ **Safety:** Before toggling the tool changer, ensure no tool is attached or that it is properly supported — unlocking will release the SWA-160 adapter.


## Operational Requirements

- **Controller must be in AUTO mode** for `setIOSignal` (digital output writes) to succeed via RWS.
- In MANUAL mode, IRC5 rejects external I/O writes with HTTP 403 (error code -1073445881) — this is an intentional IRC5 safety restriction, not a bug or permission/mastership issue.
- RWS mastership domains are `cfg`, `motion`, `rapid` only — there is no `iosystem` mastership; I/O writes are gated solely by operating mode.
- Verified 2026-06-11: GET (read) requests work in any mode; POST `?action=set` requires AUTO.

