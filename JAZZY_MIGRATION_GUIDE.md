# Mini Pupper ROS 2 Jazzy Migration - Manual Completion Guide

This document walks you through every remaining step to finish the ROS 2 Jazzy
migration.  All automated code-level fixes have already been committed.  The tasks
below require a **running Ubuntu 24.04 + ROS 2 Jazzy** environment.

The guide is organised into three parts:

- **Part A** — Tasks on your **PC / Laptop** (simulation, SLAM, Nav2 in sim)
- **Part B** — Tasks on the **Mini Pupper robot** (hardware bringup, real SLAM/nav)
- **Part C** — Reference material (known issues, what was already fixed, checklist)

---

## Table of Contents

### Part A — On Your PC / Laptop

1. [PC Prerequisites](#a1-pc-prerequisites)
2. [PC Workspace Setup](#a2-pc-workspace-setup)
3. [Fix External Dependencies (PC)](#a3-fix-external-dependencies-pc)
4. [Remaining File Fix — real_table.yaml](#a4-remaining-file-fix--real_tableyaml)
5. [Build the Workspace (PC)](#a5-build-the-workspace-pc)
6. [Test Simulation — Gazebo Harmonic](#a6-test-simulation--gazebo-harmonic)
7. [Verify ros_gz_bridge Topics](#a7-verify-ros_gz_bridge-topics)
8. [Test SLAM in Simulation](#a8-test-slam-in-simulation)
9. [Test Navigation in Simulation](#a9-test-navigation-in-simulation)

### Part B — On the Mini Pupper Robot

10. [Robot Prerequisites](#b1-robot-prerequisites)
11. [Robot Workspace Setup & Build](#b2-robot-workspace-setup--build)
12. [Hardware Bringup](#b3-hardware-bringup)
13. [Test Teleoperation](#b4-test-teleoperation)
14. [Real-World SLAM](#b5-real-world-slam)
15. [Real-World Navigation](#b6-real-world-navigation)

### Part C — Reference

16. [Known Issues and Workarounds](#c1-known-issues-and-workarounds)
17. [What Was Already Fixed (Automated)](#c2-what-was-already-fixed-automated)
18. [Summary Checklist](#c3-summary-checklist)

---
---

# Part A — On Your PC / Laptop

> Everything in this section runs on your **development PC** (Ubuntu 24.04,
> natively or in a VM).  This is where you build, simulate, and validate
> before deploying to the physical robot.

---

## A1. PC Prerequisites

You need **Ubuntu 24.04** (physical install, VM, or WSL2 with GUI support).

### Install ROS 2 Jazzy

```bash
sudo apt update && sudo apt install -y ros-jazzy-desktop-full

echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Install build tools

```bash
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-vcstool \
  python3-setuptools

sudo rosdep init   # only needed once ever
rosdep update
```

### Install Gazebo Harmonic and ROS 2 simulation packages

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
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-teleop-twist-keyboard
```

---

## A2. PC Workspace Setup

```bash
mkdir -p ~/mini_pupper_ws/src && cd ~/mini_pupper_ws/src

# Clone your fork
git clone -b ros2-jazzy https://github.com/MushfiqueTM/mini_pupper_ros.git

# Import external dependency repos (champ, ldlidar)
cd mini_pupper_ros
vcs import ~/mini_pupper_ws/src < .minipupper.repos
cd ~/mini_pupper_ws
```

Your workspace should now look like:

```
~/mini_pupper_ws/src/
├── mini_pupper_ros/          # your fork (all mini_pupper_* packages)
├── champ/champ/              # champ quadruped framework
├── champ/champ_teleop/       # champ joystick teleoperation
└── ldlidar/                  # Myzhar ldrobot-lidar-ros2 driver
```

---

## A3. Fix External Dependencies (PC)

### A3a. CHAMP framework — likely needs patching for Jazzy

The `champ` repo's `ros2` branch targets ROS 2 Humble.  It will very likely
fail to compile on Jazzy due to deprecated `rclcpp` APIs.

**Steps:**

1. Try building first (Section A5).  If `champ_base` or other champ packages
   fail, note the specific compiler errors.

2. Common fixes you'll need inside the champ source code:
   - `rclcpp::executors::MultiThreadedExecutor` constructor signature may have
     changed — check the error messages.
   - `LifecycleNode` callback signatures may need `const rclcpp::Parameter &`
     instead of raw value.
   - Any use of `rclcpp::Time(0)` may need `rclcpp::Time(0, 0, RCL_ROS_TIME)`.

3. **Recommended approach**: Fork `mangdangroboticsclub/champ` to your own
   GitHub, create a `ros2-jazzy` branch, and fix the compile errors.  Then
   update `.minipupper.repos` in mini_pupper_ros:

   ```yaml
   champ/champ:
     type: git
     url: https://github.com/MushfiqueTM/champ.git
     version: ros2-jazzy
   ```

4. **Reference project** that has champ working on Jazzy:
   <https://github.com/khaledgabr77/unitree_go2_ros2>

### A3b. LiDAR driver (Myzhar ldrobot-lidar-ros2)

The `devel` branch should build on Jazzy.  If it doesn't:

1. Check for `rclcpp` lifecycle API changes in the error output.
2. After building, verify parameter names match what your launch files use:

   ```bash
   ros2 run ldlidar_node ldlidar_node --ros-args --list-parameters
   ```

### A3c. Cartographer availability

```bash
apt-cache search ros-jazzy-cartographer
```

- **If available**: `sudo apt install -y ros-jazzy-cartographer-ros`
- **If NOT available**: Use **SLAM Toolbox** instead — it's already configured
  in `slam_toolbox.launch.py` and is a proven Nav2-compatible alternative.
  Skip Cartographer entirely.

---

## A4. Remaining File Fix — real_table.yaml

The file `mini_pupper_navigation/param/real_table.yaml` still has one
deprecated section that should be removed.  **Delete the following block**
(around lines 324-326):

```yaml
# DELETE THIS ENTIRE BLOCK — it's deprecated in Jazzy Nav2
planner_server_rclcpp_node:
  ros__parameters:
    use_sim_time: False
```

This `*_rclcpp_node` pattern was removed in Nav2 for Jazzy.  The same cleanup
was already applied to `mini_pupper.yaml`.

---

## A5. Build the Workspace (PC)

```bash
cd ~/mini_pupper_ws

# Install rosdep dependencies (skip packages not available for Jazzy)
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="champ_base champ_teleop ldlidar_node ldlidar_stl_ros2 velodyne_gazebo_plugins gazebo_ros2_control"

# Build incrementally — start with core packages to catch errors early
colcon build --symlink-install --packages-up-to mini_pupper_description

# If that succeeds, build everything
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

### Troubleshooting build failures

| Error pattern | Likely cause | Fix |
|---|---|---|
| `Cannot locate rosdep definition for [velodyne_gazebo_plugins]` | Gazebo Classic dep in champ | Add to `--skip-keys` (already done above) |
| `Cannot locate rosdep definition for [gazebo_ros2_control]` | Gazebo Classic dep in champ | Add to `--skip-keys` (already done above) |
| `Could not find package champ_base` | champ didn't compile | See Section A3a — fork and fix |
| `CMake Error: cmake_minimum_required 3.16` | Old CMake | `sudo apt install cmake` |
| `fatal error: gz/sim/...` | Missing Gazebo dev headers | `sudo apt install libgz-sim8-dev` |
| `No module named 'MangDang'` | Hardware-only BSP package | Expected on PC — only needed on robot |
| Python `SyntaxError` in setup.py | Python 3.12 removed distutils | Change to `from setuptools import setup` |

---

## A6. Test Simulation — Gazebo Harmonic

### A6a. Launch the simulation

```bash
source ~/mini_pupper_ws/install/setup.bash

# Set the robot model
export ROBOT_MODEL=mini_pupper_2

# Launch everything
ros2 launch mini_pupper_simulation main.launch.py
```

**What you should see:**
- Gazebo Harmonic GUI opens with the `mini_pupper_home` world (room with walls
  and obstacles).
- The Mini Pupper model spawns at position (0, 0, 0.066).
- No red error text in the terminal (warnings about unused parameters are OK).

### A6b. Verify the robot loaded correctly

Open a **second terminal**:

```bash
source ~/mini_pupper_ws/install/setup.bash

# Verify robot_description is published
ros2 topic echo /robot_description --once

# Verify joint states
ros2 topic echo /joint_states --once

# Visualize TF tree
ros2 run tf2_tools view_frames
# Opens frames.pdf showing the full TF tree
```

---

## A7. Verify ros_gz_bridge Topics

This is one of the **most critical steps**.  The bridge in `main.launch.py`
currently assumes these Gazebo topic paths:

| ROS 2 Topic | Expected Gz Topic | Direction |
|---|---|---|
| `/clock` | (auto) | Gz -> ROS |
| `/scan` | `/lidar/scan` | Gz -> ROS |
| `/imu/data` | `/imu/data` | Gz -> ROS |

**However**, Gazebo Harmonic often publishes sensor topics under long
model-specific namespaces like:

```
/world/mini_pupper_home/model/mini_pupper_2/link/lidar_link/sensor/lidar/scan
```

### Step 1: Check the actual Gz topic names

With the simulation still running, open **another terminal**:

```bash
# List ALL Gazebo topics
gz topic -l

# Filter for scan topics
gz topic -l | grep -i scan

# Filter for IMU topics
gz topic -l | grep -i imu
```

### Step 2: If the topic paths DON'T match

Edit `mini_pupper_simulation/launch/main.launch.py` and update the bridge
arguments.  For example, if the actual LiDAR topic is at a long path:

```python
gz_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        # Use the ACTUAL Gz topic path on the left side:
        '/world/mini_pupper_home/model/mini_pupper_2/link/lidar_link/sensor/lidar/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        '/world/mini_pupper_home/model/mini_pupper_2/link/imu_link/sensor/imu_sensor/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
    ],
    remappings=[
        ('/world/mini_pupper_home/model/mini_pupper_2/link/lidar_link/sensor/lidar/scan', '/scan'),
        ('/world/mini_pupper_home/model/mini_pupper_2/link/imu_link/sensor/imu_sensor/imu', '/imu/data'),
    ],
    parameters=[{'use_sim_time': True}],
    output='screen'
)
```

### Step 3: Verify data flows into ROS 2

```bash
ros2 topic echo /scan --once
ros2 topic echo /imu/data --once
ros2 topic echo /clock --once
```

If any of these return no data, go back to Step 1 and double-check the Gz
topic path.

---

## A8. Test SLAM in Simulation

### SLAM Toolbox (recommended)

```bash
# Terminal 1 — Simulation (if not already running)
ros2 launch mini_pupper_simulation main.launch.py

# Terminal 2 — SLAM
ros2 launch mini_pupper_slam slam_toolbox.launch.py use_sim_time:=true

# Terminal 3 — Teleoperation (drive the robot around)
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Verify:**
- A map builds incrementally in RViz as you drive.
- TF tree shows `map -> odom -> base_footprint -> ...`
- No TF errors in the terminal.

### Cartographer (only if installed)

```bash
ros2 launch mini_pupper_slam slam.launch.py use_sim_time:=true
```

If `cartographer_ros` is not installed, this will fail — use SLAM Toolbox
instead.

### Save the map (for navigation testing)

```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/sim_map
```

---

## A9. Test Navigation in Simulation

```bash
# Terminal 1 — Simulation
ros2 launch mini_pupper_simulation main.launch.py

# Terminal 2 — Navigation (use the map you just saved)
ros2 launch mini_pupper_navigation navigation.launch.py \
  use_sim_time:=true \
  map:=$HOME/maps/sim_map.yaml
```

**Verify:**
- Nav2 nodes start without errors.
- You should see `behavior_server` in the logs (NOT `recoveries_server`).
- In RViz: set "2D Pose Estimate" to localise, then "2D Nav Goal" to navigate.
- The robot plans a path and drives to the goal.
- Local and global costmaps are visible in RViz.

---
---

# Part B — On the Mini Pupper Robot

> Everything in this section runs on the **Mini Pupper** itself
> (Raspberry Pi / Compute Module running Ubuntu 24.04).
> Some commands also run on your PC as a remote station — those are
> clearly marked as **[On your PC]**.

---

## B1. Robot Prerequisites

The Mini Pupper should be running **Ubuntu 24.04** on its onboard computer.

### Install ROS 2 Jazzy on the robot

```bash
sudo apt update && sudo apt install -y ros-jazzy-ros-base

echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

> **Note:** We use `ros-base` instead of `desktop-full` on the robot because
> the robot doesn't need Gazebo, RViz, or GUI tools.  Those run on your PC.

### Install build tools

```bash
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-vcstool \
  python3-setuptools

sudo rosdep init   # skip if already done
rosdep update
```

### Install runtime ROS 2 packages

```bash
sudo apt install -y \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-joint-trajectory-controller \
  ros-jazzy-robot-localization \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-teleop-twist-keyboard
```

### Install MangDang BSP (Board Support Packages)

These are hardware-specific Python packages that interface with the servos,
IMU, display, and ESP32.  Follow MangDang's official instructions:

```bash
# Typical installation (check MangDang docs for the latest method):
# - MangDang.mini_pupper.HardwareInterface
# - MangDang.LCD.ST7789
# - MangDang.mini_pupper.ESP32Interface
#
# These are usually installed via pip or MangDang's setup script.
# Without these, the hardware driver nodes will fail with:
#   "No module named 'MangDang'"
```

> MangDang's official setup guide:
> <https://github.com/mangdangroboticsclub/mini_pupper_ros>

---

## B2. Robot Workspace Setup & Build

```bash
mkdir -p ~/mini_pupper_ws/src && cd ~/mini_pupper_ws/src

# Clone your fork
git clone -b ros2-jazzy https://github.com/MushfiqueTM/mini_pupper_ros.git

# Import external repos
cd mini_pupper_ros
vcs import ~/mini_pupper_ws/src < .minipupper.repos
cd ~/mini_pupper_ws

# Install rosdep dependencies
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="champ_base champ_teleop ldlidar_node ldlidar_stl_ros2 velodyne_gazebo_plugins gazebo_ros2_control"

# Build the workspace
colcon build --symlink-install

# Source it
echo "source ~/mini_pupper_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

> **Tip:** Building on a Raspberry Pi is slow.  Consider cross-compiling on
> your PC or using `colcon build --packages-select <pkg>` to build only the
> packages you need.

---

## B3. Hardware Bringup

```bash
# Set the robot model
export ROBOT_MODEL=mini_pupper_2   # or mini_pupper for v1

# Launch the full hardware bringup
ros2 launch mini_pupper_bringup bringup.launch.py hardware_connected:=true
```

### Verify hardware topics

In a **second terminal on the robot** (or SSH session):

```bash
source ~/mini_pupper_ws/install/setup.bash

# List all active topics
ros2 topic list

# Check joint states (servo positions)
ros2 topic echo /joint_states --once

# Check LiDAR
ros2 topic echo /scan --once

# Check IMU
ros2 topic echo /imu/data --once
```

**Expected results:**
- `/joint_states` publishes 12 joint positions (3 per leg x 4 legs).
- `/scan` publishes `LaserScan` messages from the LD06/LD19 LiDAR.
- `/imu/data` publishes `Imu` messages from the onboard IMU.

If `/scan` is missing, the LiDAR driver may not have started.  Check:
```bash
ros2 node list | grep ldlidar
```

If the LiDAR node is running but publishing to a different topic (e.g.
`/ldlidar_node/scan`), add a remap in the bringup launch file.

---

## B4. Test Teleoperation

### [On your PC]

Make sure your PC and the Mini Pupper are on the **same network** and using
the same `ROS_DOMAIN_ID` (default is 0).

```bash
source ~/mini_pupper_ws/install/setup.bash

# Drive the robot with keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Verify:**
- The robot responds to WASD/arrow keys.
- All four legs move correctly.
- The robot walks forward, backward, turns left, turns right.

### [On the robot]

If you prefer to test directly on the robot via SSH:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## B5. Real-World SLAM

### [On the robot] — Start SLAM

```bash
export ROBOT_MODEL=mini_pupper_2

# Make sure bringup is running (Section B3), then:
ros2 launch mini_pupper_slam slam_toolbox.launch.py use_sim_time:=false
```

### [On your PC] — Visualise and drive

```bash
source ~/mini_pupper_ws/install/setup.bash

# Open RViz to see the map being built
rviz2
# In RViz: Add displays for Map (/map), LaserScan (/scan), TF, RobotModel

# In another terminal — drive the robot around
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive the robot slowly around the room.  Watch the map build in RViz.

### [On the robot or PC] — Save the map

```bash
mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_room
```

This creates `my_room.yaml` and `my_room.pgm`.  Transfer these to your PC if
you saved them on the robot:

```bash
# [On your PC]
scp ubuntu@<robot-ip>:~/maps/my_room.* ~/maps/
```

---

## B6. Real-World Navigation

### [On the robot] — Start navigation

```bash
export ROBOT_MODEL=mini_pupper_2

# Make sure bringup is running (Section B3), then:
ros2 launch mini_pupper_navigation navigation.launch.py \
  use_sim_time:=false \
  map:=$HOME/maps/my_room.yaml
```

### [On your PC] — Send goals via RViz

```bash
rviz2
```

In RViz:
1. Click "2D Pose Estimate" and click+drag on the map to set the robot's
   initial position.
2. Click "2D Nav Goal" and click+drag to set a destination.
3. Watch the robot plan a path and navigate autonomously.

**Verify:**
- Local and global costmaps update correctly.
- The robot avoids obstacles.
- The robot reaches the goal without collisions.

---
---

# Part C — Reference

---

## C1. Known Issues and Workarounds

### C1.1 Gazebo Classic material tags in URDF

The URDF files still contain `<gazebo>` blocks with Classic material
references like:

```xml
<gazebo reference="some_link">
  <material>Gazebo/FlatBlack</material>
</gazebo>
```

Gazebo Harmonic ignores these — they won't cause crashes but the robot may
appear with default grey materials.  To fix visuals, add `<material>` tags
inside `<visual>` elements directly, or define materials in SDF format.

### C1.2 robot_localization EKF configs

The `ekf_localization.launch.py` (from champ_base) references config files at
`champ_base/config/ekf/*.yaml`.  If your champ fork's file layout changes,
update the path in the launch file.

### C1.3 Camera bridge not configured

The camera sensor is defined in the URDF but the `ros_gz_bridge` in
`main.launch.py` does not currently bridge the camera image topic.  To add it,
append this to the `gz_bridge` arguments:

```python
'/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
```

You may need to adjust the Gz topic path (use `gz topic -l | grep image`).

### C1.4 LiDAR topic naming — simulation vs hardware

- **Simulation**: LiDAR comes from `ros_gz_bridge` -> `/scan`
- **Physical hardware**: LiDAR comes from `ldlidar_node` -> `/scan`
  (or `/ldlidar_node/scan` depending on driver config)

Nav2 and SLAM expect `/scan`.  If the driver publishes to a different topic,
add a remap in the bringup launch file.

### C1.5 champ_teleop Joy dependency

```bash
sudo apt install -y ros-jazzy-joy ros-jazzy-teleop-twist-joy
```

### C1.6 Python 3.12 — removed distutils

Ubuntu 24.04 ships Python 3.12, which removed `distutils`.  If any
`setup.py` uses `from distutils.core import setup`, change it to
`from setuptools import setup`.  This project already uses `setuptools`, but
third-party dependencies (like champ) might not.

### C1.7 Network setup for PC <-> Robot communication

Both your PC and the Mini Pupper must:
- Be on the **same WiFi network** (or connected via Ethernet).
- Use the **same `ROS_DOMAIN_ID`** (default is 0, so if you haven't changed
  it, you're fine).
- Have **no firewall** blocking UDP multicast (ROS 2 DDS uses multicast for
  discovery).

Test connectivity:
```bash
# On your PC — you should see nodes from the robot
ros2 node list

# If you see nothing, try setting the same domain ID on both machines:
export ROS_DOMAIN_ID=42   # same number on PC and robot
```

---

## C2. What Was Already Fixed (Automated)

For your reference, all changes committed in the `ros2-jazzy` branch:

| File | Change |
|---|---|
| All 7 `CMakeLists.txt` | Bumped `cmake_minimum_required` to 3.16 |
| `mini_pupper_simulation/CMakeLists.txt` | Removed invalid `find_package` for runtime deps |
| `mini_pupper_description/CMakeLists.txt` | Removed invalid `find_package` for runtime deps |
| `mini_pupper_description/urdf/*/mini_pupper_description.urdf.xacro` | Replaced Gazebo Classic plugins with Harmonic-native sensors; fixed `ros2_control` plugin name |
| `mini_pupper_simulation/worlds/empty.sdf` | **New** — SDF 1.9 world file |
| `mini_pupper_simulation/worlds/mini_pupper_home.sdf` | **New** — SDF 1.9 world file with room/obstacles |
| `mini_pupper_simulation/launch/gazebo.launch.py` | Updated to use `.sdf` world files |
| `mini_pupper_simulation/launch/main.launch.py` | Added `ros_gz_bridge` node for clock, LiDAR, IMU |
| `mini_pupper_description/config/ros_control/mini_pupper_controller.yaml` | Fixed controller name (`joint_state_broadcaster`) |
| `mini_pupper_navigation/param/mini_pupper.yaml` | Full Nav2 Jazzy update (behavior_server, plugin renames) |
| `mini_pupper_slam/launch/slam.launch.py` | Fixed argument passing to cartographer |
| `mini_pupper_slam/launch/slam_toolbox.launch.py` | Fixed `PathJoinSubstitution` usage |
| `mini_pupper_driver/.../curvature_compensation.py` | Added proper `rclpy.shutdown()` |
| `mini_pupper_driver/.../nav_vel_scaler.py` | Added proper `rclpy.shutdown()` |
| `mini_pupper_driver/package.xml` | Fixed dependency types |
| `mini_pupper_music/package.xml` | Added missing dependencies |
| `.github/workflows/industrial_ci.yml` | Updated skip keys + actions version |

---

## C3. Summary Checklist

### PC Tasks

- [ ] Ubuntu 24.04 + ROS 2 Jazzy installed and sourced
- [ ] Gazebo Harmonic packages installed
- [ ] Workspace cloned and external repos imported via `vcs`
- [ ] `rosdep` dependencies installed
- [ ] Removed `planner_server_rclcpp_node` from `real_table.yaml` (Section A4)
- [ ] `champ` packages build successfully (fork and fix if needed)
- [ ] `ldlidar` driver builds successfully
- [ ] Full `colcon build` completes with zero errors
- [ ] Simulation launches — Gazebo Harmonic GUI shows world + robot
- [ ] `ros_gz_bridge` verified — `/scan`, `/imu/data`, `/clock` have data
- [ ] SLAM Toolbox works in simulation — map builds correctly
- [ ] Nav2 works in simulation — robot navigates to goals

### Robot Tasks

- [ ] Ubuntu 24.04 + ROS 2 Jazzy (ros-base) installed on the robot
- [ ] MangDang BSP packages installed (HardwareInterface, LCD, ESP32)
- [ ] Workspace cloned and built on the robot
- [ ] Hardware bringup launches — `/joint_states`, `/scan`, `/imu/data` publish
- [ ] Teleoperation works — robot responds to keyboard commands
- [ ] Real-world SLAM — map builds from actual LiDAR data
- [ ] Real-world navigation — robot navigates autonomously to goals
- [ ] Camera bridge added if camera features are needed (Section C1.3)

---

*Guide generated as part of the ROS 2 Humble -> Jazzy migration.*
*Last updated: February 2026*
