# Mini Pupper ROS 2 Jazzy Migration - Manual Completion Guide

This document walks you through every remaining step to finish the ROS 2 Jazzy
migration, build the workspace, test in simulation, and deploy on physical
hardware.  All automated code-level fixes have already been committed.  The tasks
below require a **running Ubuntu 24.04 + ROS 2 Jazzy** environment and cannot be
completed from Windows alone.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Workspace Setup](#2-workspace-setup)
3. [Fix External Dependencies](#3-fix-external-dependencies)
4. [Build the Workspace](#4-build-the-workspace)
5. [Remaining File Fix — real_table.yaml](#5-remaining-file-fix--real_tableyaml)
6. [Test Simulation (Gazebo Harmonic)](#6-test-simulation-gazebo-harmonic)
7. [Verify ros_gz_bridge Topics](#7-verify-ros_gz_bridge-topics)
8. [Test SLAM](#8-test-slam)
9. [Test Navigation](#9-test-navigation)
10. [Test on Physical Hardware](#10-test-on-physical-hardware)
11. [Known Issues and Workarounds](#11-known-issues-and-workarounds)
12. [Summary Checklist](#12-summary-checklist)

---

## 1. Prerequisites

You need an **Ubuntu 24.04** machine (physical, VM, or Docker) with:

```bash
# Install ROS 2 Jazzy (desktop-full gives you RViz, Gazebo bindings, etc.)
sudo apt update && sudo apt install -y ros-jazzy-desktop-full

# Source the ROS 2 setup
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Install essential build tools
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-vcstool

# Initialise rosdep (skip if already done)
sudo rosdep init   # only needed once
rosdep update
```

Install Gazebo Harmonic packages explicitly (some may already come with
`desktop-full`):

```bash
sudo apt install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-joint-trajectory-controller \
  ros-jazzy-robot-localization \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup
```

---

## 2. Workspace Setup

```bash
mkdir -p ~/mini_pupper_ws/src && cd ~/mini_pupper_ws/src

# Clone your fork
git clone -b ros2-jazzy https://github.com/MushfiqueTM/mini_pupper_ros.git

# Import external dependency repos (champ, ldlidar)
cd mini_pupper_ros
vcs import ~/mini_pupper_ws/src < .minipupper.repos
cd ~/mini_pupper_ws
```

At this point your workspace should have these source trees:

```
~/mini_pupper_ws/src/
├── mini_pupper_ros/          # your fork
├── champ/champ/              # champ framework
├── champ/champ_teleop/       # champ teleoperation
└── ldlidar/                  # Myzhar ldrobot-lidar-ros2
```

---

## 3. Fix External Dependencies

### 3a. CHAMP framework — likely needs patching for Jazzy

The `champ` repo's `ros2` branch targets Humble.  It will very likely fail to
compile on Jazzy due to deprecated `rclcpp` APIs.

**Steps:**

1. Try building first (Step 4).  If `champ_base` or other champ packages fail,
   note the specific errors.

2. Common fixes you'll need:
   - `rclcpp::executors::MultiThreadedExecutor` constructor signature may have
     changed — check the error messages.
   - `LifecycleNode` callback signatures may require `const
     rclcpp::Parameter &` instead of raw value.
   - Any use of `rclcpp::Time(0)` may need to become `rclcpp::Time(0, 0,
     RCL_ROS_TIME)`.

3. **Recommended approach**: Fork `mangdangroboticsclub/champ` to your own
   GitHub, create a `ros2-jazzy` branch, and fix the compile errors.  Then
   update `.minipupper.repos`:

   ```yaml
   champ/champ:
     type: git
     url: https://github.com/MushfiqueTM/champ.git
     version: ros2-jazzy
   ```

4. **Reference project**: The repo `khaledgabr77/unitree_go2_ros2` has a
   vendored version of champ that already works on Jazzy.  You can look at
   their patches for guidance:
   <https://github.com/khaledgabr77/unitree_go2_ros2>

### 3b. LiDAR driver (Myzhar ldrobot-lidar-ros2)

The `devel` branch of Myzhar's driver should build on Jazzy.  If it doesn't:

1. Check for `rclcpp` lifecycle API changes.
2. The node executable is `ldlidar_node`.  Verify the parameter names your
   launch files use (`serial_port`, `lidar_model`) match what the driver
   actually accepts.  You can check with:

   ```bash
   ros2 run ldlidar_node ldlidar_node --ros-args --list-parameters
   ```

### 3c. Cartographer availability

Check if `cartographer_ros` is available for Jazzy:

```bash
apt-cache search ros-jazzy-cartographer
```

- **If available**: `sudo apt install -y ros-jazzy-cartographer-ros`
- **If NOT available**: You have two options:
  1. Build `cartographer_ros` from source (complex, involves protobuf/absl).
  2. Use **SLAM Toolbox** instead — the `slam_toolbox.launch.py` is already
     set up in the project and is a proven Nav2-compatible alternative.

---

## 4. Build the Workspace

```bash
cd ~/mini_pupper_ws

# Install rosdep dependencies (skip packages that aren't in apt)
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="champ_base champ_teleop ldlidar_node ldlidar_stl_ros2"

# Build — start with just the core packages to catch errors early
colcon build --symlink-install --packages-up-to mini_pupper_description

# If that succeeds, build everything
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

**Troubleshooting build failures:**

| Error pattern | Likely cause | Fix |
|---|---|---|
| `Could not find package champ_base` | champ didn't build | See Section 3a |
| `CMake Error: cmake_minimum_required 3.16` | Old CMake | `sudo apt install cmake` (Jazzy needs >= 3.16) |
| `fatal error: gz/sim/...` | Missing Gazebo dev packages | `sudo apt install libgz-sim8-dev` |
| `No module named 'MangDang'` | Hardware-only BSP | Expected — only needed on physical robot |
| Python `SyntaxError` in setup.py | Python 3.12 change | Check for removed `distutils` usage |

---

## 5. Remaining File Fix — real_table.yaml

The file `mini_pupper_navigation/param/real_table.yaml` still has one
deprecated section that should be removed.  Delete the following block
(around line 324–326):

```yaml
# DELETE THIS ENTIRE BLOCK — it's deprecated in Jazzy Nav2
planner_server_rclcpp_node:
  ros__parameters:
    use_sim_time: False
```

This `*_rclcpp_node` pattern was removed in Nav2 for Jazzy.  The same
cleanup was already applied to `mini_pupper.yaml`.

---

## 6. Test Simulation (Gazebo Harmonic)

### 6a. Launch the simulation

```bash
# Make sure you've sourced the workspace
source ~/mini_pupper_ws/install/setup.bash

# Set the robot model (mini_pupper or mini_pupper_2)
export ROBOT_MODEL=mini_pupper_2

# Launch everything
ros2 launch mini_pupper_simulation main.launch.py
```

**What you should see:**
- Gazebo Harmonic GUI opens with the `mini_pupper_home` world.
- The Mini Pupper model spawns at position (0, 0, 0.066).
- RViz may or may not launch depending on your bringup config.
- No red error text in the terminal (warnings are OK).

### 6b. Verify the robot loaded correctly

In a **new terminal**:

```bash
source ~/mini_pupper_ws/install/setup.bash

# Check that the robot_description is published
ros2 topic echo /robot_description --once

# Check joint states are being published
ros2 topic echo /joint_states --once

# Check TF tree
ros2 run tf2_tools view_frames
# This creates a frames.pdf showing the TF tree
```

---

## 7. Verify ros_gz_bridge Topics

This is one of the most critical steps.  The bridge configuration in
`main.launch.py` assumes these Gazebo topic paths:

| ROS 2 Topic | Expected Gz Topic | Bridge Direction |
|---|---|---|
| `/clock` | (auto) | Gz → ROS |
| `/scan` | `/lidar/scan` | Gz → ROS |
| `/imu/data` | `/imu/data` | Gz → ROS |

**However**, Gazebo Harmonic often publishes sensor topics under
model-specific namespaces like:

```
/world/mini_pupper_home/model/mini_pupper_2/link/lidar_link/sensor/lidar/scan
```

### Checking actual Gz topics

```bash
# List all Gazebo topics
gz topic -l

# Look for scan-related topics
gz topic -l | grep -i scan

# Look for IMU topics
gz topic -l | grep -i imu
```

### If the topic paths don't match

You need to update the bridge configuration in
`mini_pupper_simulation/launch/main.launch.py`.  For example, if the LiDAR
topic is actually at a long namespaced path:

```python
gz_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        # Replace the left side with the ACTUAL Gz topic path:
        '/world/mini_pupper_home/model/mini_pupper_2/link/lidar_link/sensor/lidar/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        '/world/mini_pupper_home/model/mini_pupper_2/link/imu_link/sensor/imu_sensor/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
    ],
    remappings=[
        # Remap the full Gz path to the short ROS topic name:
        ('/world/mini_pupper_home/model/mini_pupper_2/link/lidar_link/sensor/lidar/scan', '/scan'),
        ('/world/mini_pupper_home/model/mini_pupper_2/link/imu_link/sensor/imu_sensor/imu', '/imu/data'),
    ],
    parameters=[{'use_sim_time': True}],
    output='screen'
)
```

**Alternative approach** — use `<topic>` tags in the URDF sensor definitions to
force short topic names.  This was already attempted in the URDF xacro files
with `<topic>lidar/scan</topic>`, but Gazebo Harmonic may or may not honour
this depending on the SDF version and sensor type.

### Quick verification

```bash
# After launching simulation, check that ROS 2 receives scan data
ros2 topic echo /scan --once

# Check IMU data
ros2 topic echo /imu/data --once

# Check clock
ros2 topic echo /clock --once
```

If `/scan` shows no data but `gz topic -l` shows the sensor topic exists under
a different path, update the bridge arguments as shown above.

---

## 8. Test SLAM

### 8a. SLAM Toolbox (recommended)

```bash
# Terminal 1: Launch simulation
ros2 launch mini_pupper_simulation main.launch.py

# Terminal 2: Launch SLAM Toolbox
ros2 launch mini_pupper_slam slam_toolbox.launch.py use_sim_time:=true

# Terminal 3: Launch teleoperation
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/cmd_vel
```

Drive the robot around and verify:
- The map builds incrementally in RViz.
- TF tree shows `map → odom → base_footprint → ...`
- No TF errors in the terminal.

### 8b. Cartographer (only if available)

```bash
ros2 launch mini_pupper_slam slam.launch.py use_sim_time:=true
```

If `cartographer_ros` is not installed, this will fail.  Use SLAM Toolbox
instead.

---

## 9. Test Navigation

```bash
# Terminal 1: Launch simulation
ros2 launch mini_pupper_simulation main.launch.py

# Terminal 2: Launch navigation with a pre-built map
ros2 launch mini_pupper_navigation navigation.launch.py \
  use_sim_time:=true \
  map:=/path/to/your/map.yaml
```

**Verify:**
- Nav2 nodes start without errors (check for "behavior_server" in logs, NOT
  "recoveries_server").
- You can set a 2D Nav Goal in RViz and the robot plans and moves.
- Costmaps are visible in RViz.

If you see errors about missing `recoveries_server`, the Nav2 YAML files
still have old parameter names — double-check `mini_pupper.yaml` and
`real_table.yaml`.

---

## 10. Test on Physical Hardware

### 10a. Install MangDang BSP packages

On the physical Mini Pupper (Ubuntu 24.04 on Raspberry Pi / Compute Module):

```bash
# These are hardware-specific packages from MangDang
# Follow MangDang's official instructions for installing:
# - MangDang.mini_pupper.HardwareInterface
# - MangDang.LCD.ST7789
# - MangDang.mini_pupper.ESP32Interface
# These are typically installed via pip or the MangDang setup script
```

### 10b. Build on the robot

```bash
cd ~/mini_pupper_ws
colcon build --symlink-install
source install/setup.bash
```

### 10c. Launch the bringup

```bash
export ROBOT_MODEL=mini_pupper_2  # or mini_pupper

# Basic bringup (hardware connected)
ros2 launch mini_pupper_bringup bringup.launch.py hardware_connected:=true

# In another terminal, check that hardware topics are publishing
ros2 topic list
ros2 topic echo /joint_states --once
ros2 topic echo /scan --once       # LiDAR
ros2 topic echo /imu/data --once   # IMU
```

### 10d. Test teleoperation

```bash
# On your laptop (same ROS 2 domain):
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Verify the robot moves correctly with keyboard commands.

### 10e. Test real-world SLAM and Navigation

```bash
# On the robot:
ros2 launch mini_pupper_slam slam_toolbox.launch.py use_sim_time:=false

# On your laptop: open RViz and visualize the map
rviz2

# Drive around, save the map:
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map

# Then launch navigation with the saved map:
ros2 launch mini_pupper_navigation navigation.launch.py \
  use_sim_time:=false \
  map:=$HOME/maps/my_map.yaml
```

---

## 11. Known Issues and Workarounds

### 11.1 Gazebo Classic material tags in URDF

The URDF files still contain `<gazebo>` blocks with Classic material
references like:

```xml
<gazebo reference="some_link">
  <material>Gazebo/FlatBlack</material>
</gazebo>
```

Gazebo Harmonic ignores these — they won't cause crashes but the robot may
appear with default grey materials in Gz.  To fix visuals:

- Add `<material>` tags inside `<visual>` elements in the URDF directly.
- Or define materials in SDF using `<material><ambient>`, `<diffuse>`, etc.

### 11.2 robot_localization EKF configs

The `ekf_localization.launch.py` (from champ_base) references config files
at `champ_base/config/ekf/*.yaml`.  If the champ fork's file layout changes,
update the path in the launch file.

### 11.3 Camera bridge not configured

The camera sensor is defined in the URDF but the `ros_gz_bridge` in
`main.launch.py` does not currently bridge the camera image topic.  To add
it:

```python
# Add to the gz_bridge arguments list in main.launch.py:
'/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
```

You may need to adjust the actual Gz topic path (use `gz topic -l | grep
image` to find it).

### 11.4 LiDAR topic naming on physical hardware vs simulation

- **Simulation**: LiDAR data comes from Gazebo via `ros_gz_bridge` → `/scan`
- **Physical hardware**: LiDAR data comes from the `ldlidar_node` driver →
  `/scan` (or `/ldlidar_node/scan` depending on driver config)

Make sure the topic name matches what Nav2 and SLAM expect.  Check with:

```bash
ros2 topic list | grep scan
```

If the driver publishes to `/ldlidar_node/scan`, add a remap in the bringup
launch file or configure the driver to publish to `/scan`.

### 11.5 champ_teleop may have Joy dependency issues

The `champ_teleop` package depends on `joy` and `teleop_twist_joy`.  Verify
they're available:

```bash
sudo apt install -y ros-jazzy-joy ros-jazzy-teleop-twist-joy
```

### 11.6 Python 3.12 — removed distutils

Python 3.12 (shipped with Ubuntu 24.04) removed the `distutils` module.  If
any `setup.py` file uses `from distutils.core import setup`, it must be
changed to `from setuptools import setup`.  This project already uses
`setuptools`, but third-party dependencies (like champ) might not.

Fix: `sudo apt install python3-setuptools` and update the offending
`setup.py`.

---

## 12. Summary Checklist

Use this checklist to track your progress:

- [ ] **Ubuntu 24.04 + ROS 2 Jazzy** installed and sourced
- [ ] **Gazebo Harmonic packages** installed (`ros-jazzy-ros-gz`, etc.)
- [ ] **Workspace cloned** and external repos imported via `vcs`
- [ ] **rosdep** dependencies installed
- [ ] **Remove `planner_server_rclcpp_node`** from `real_table.yaml` (Section 5)
- [ ] **champ packages** build successfully (fix or fork if needed)
- [ ] **ldlidar driver** builds successfully
- [ ] **Full `colcon build`** completes with zero errors
- [ ] **Simulation launches** — Gazebo Harmonic GUI shows world + robot
- [ ] **ros_gz_bridge verified** — `/scan`, `/imu/data`, `/clock` have data
- [ ] **SLAM Toolbox** works in simulation — map builds correctly
- [ ] **Nav2** works in simulation — robot navigates to goals
- [ ] **Physical robot bringup** — hardware topics publish correctly
- [ ] **Physical SLAM** — map builds from real LiDAR data
- [ ] **Physical navigation** — robot navigates in the real world
- [ ] **Camera bridge** added if camera features are needed (Section 11.3)

---

## Quick Reference: What Was Already Fixed (Automated)

For your reference, here is a summary of all changes that were already
committed in the `ros2-jazzy` branch:

| File | Change |
|---|---|
| All 7 `CMakeLists.txt` | Bumped `cmake_minimum_required` to 3.16 |
| `mini_pupper_simulation/CMakeLists.txt` | Removed invalid `find_package` for runtime deps |
| `mini_pupper_description/CMakeLists.txt` | Removed invalid `find_package` for runtime deps |
| `mini_pupper_description/urdf/*/mini_pupper_description.urdf.xacro` | Replaced Gazebo Classic plugins with Harmonic-native sensors; fixed `ros2_control` plugin name |
| `mini_pupper_simulation/worlds/empty.sdf` | **New** — SDF 1.9 world file |
| `mini_pupper_simulation/worlds/mini_pupper_home.sdf` | **New** — SDF 1.9 world file with room/obstacles |
| `mini_pupper_simulation/launch/gazebo.launch.py` | Updated to use `.sdf` world files |
| `mini_pupper_simulation/launch/main.launch.py` | Added `ros_gz_bridge` node |
| `mini_pupper_description/config/ros_control/mini_pupper_controller.yaml` | Fixed controller name (`joint_state_broadcaster`) |
| `mini_pupper_navigation/param/mini_pupper.yaml` | Full Nav2 Jazzy update |
| `mini_pupper_slam/launch/slam.launch.py` | Fixed argument passing to cartographer |
| `mini_pupper_slam/launch/slam_toolbox.launch.py` | Fixed `PathJoinSubstitution` usage |
| `mini_pupper_driver/.../curvature_compensation.py` | Added proper `rclpy.shutdown()` |
| `mini_pupper_driver/.../nav_vel_scaler.py` | Added proper `rclpy.shutdown()` |
| `mini_pupper_driver/package.xml` | Fixed dependency types |
| `mini_pupper_music/package.xml` | Added missing dependencies |
| `.github/workflows/industrial_ci.yml` | Updated skip keys + actions version |

---

*Guide generated as part of the ROS 2 Humble → Jazzy migration.*
*Last updated: February 2026*
