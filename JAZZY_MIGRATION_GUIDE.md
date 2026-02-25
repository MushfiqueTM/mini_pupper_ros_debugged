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
4. [Build the Workspace (PC)](#a4-build-the-workspace-pc)
5. [Test Simulation — Gazebo Harmonic](#a5-test-simulation--gazebo-harmonic)
6. [Verify ros_gz_bridge Topics](#a6-verify-ros_gz_bridge-topics)
7. [Test SLAM in Simulation](#a7-test-slam-in-simulation)
8. [Test Navigation in Simulation](#a8-test-navigation-in-simulation)

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

# IMPORTANT: Initialize the champ submodule (libchamp headers)
# vcs import does not init submodules, so this must be done manually.
# The submodule lives at champ/champ/include/champ (pointing to libchamp).
cd ~/mini_pupper_ws/src/champ/champ
git submodule update --init --recursive

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

### A3a. CHAMP framework — disable Gazebo Classic packages

After comparing the original `mangdangroboticsclub/champ` (ros2 branch) with
[khaledgabr77/unitree_go2_ros2](https://github.com/khaledgabr77/unitree_go2_ros2)
(which already works on Jazzy), the core champ packages (`champ`, `champ_base`,
`champ_msgs`) compile on Jazzy **with zero code changes**.

The problem is that the champ repo also ships 5 packages with Gazebo Classic
dependencies that don't exist on Jazzy.  We don't need any of them — Mini Pupper
uses its own simulation setup.  The fix is to add `COLCON_IGNORE` marker files
so colcon skips them entirely.

**Run this after `vcs import` (Section A2):**

```bash
# Add COLCON_IGNORE to the 5 broken champ packages
for pkg in champ_gazebo champ_description champ_bringup champ_navigation champ_config; do
  touch ~/mini_pupper_ws/src/champ/champ/$pkg/COLCON_IGNORE
done
```

This tells colcon to completely ignore those directories.  The packages you
actually need (`champ`, `champ_base`, `champ_msgs`) will build normally.

**Verify it worked:**

```bash
cd ~/mini_pupper_ws
colcon list --packages-select champ champ_base champ_msgs
# Should list exactly these 3 packages

colcon list --packages-select champ_gazebo 2>&1
# Should show an error or empty — the package is now ignored
```

> **Note:** The CI workflow (`industrial_ci.yml`) already handles this
> automatically via the `BEFORE_BUILD_UPSTREAM_WORKSPACE` hook.

> **Optional permanent fix:** Fork `mangdangroboticsclub/champ` to your own
> GitHub, remove the 5 broken packages (or add COLCON_IGNORE files), and
> update `.minipupper.repos` to point to your fork.

### A3b. LiDAR driver (Myzhar ldrobot-lidar-ros2)

The `devel` branch builds on Jazzy with no code changes.  **No manual
configuration is needed** — `mini_pupper_driver` ships its own `ldlidar.yaml`
(configured for LD06, `lidar_link` frame, `/dev/ldlidar` port) and loads it
at launch time, bypassing the upstream defaults.

### A3b-2. EKF configuration

**No manual configuration is needed** — `mini_pupper_bringup` ships its own
corrected EKF config files (`config/ekf/*.yaml`) with:
- Fixed `imu0_config` (fuses angular velocity + linear acceleration, not linear velocity)
- Reduced frequencies (15–20 Hz) suitable for Raspberry Pi

### A3c. Cartographer availability

```bash
apt-cache search ros-jazzy-cartographer
```

- **If available**: `sudo apt install -y ros-jazzy-cartographer-ros`
- **If NOT available**: Use **SLAM Toolbox** instead — it's already configured
  in `slam_toolbox.launch.py` and is a proven Nav2-compatible alternative.
  Skip Cartographer entirely.

---

## A4. Build the Workspace (PC)

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash

# Install rosdep dependencies (skip packages not available for Jazzy)
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="champ_base champ_teleop champ_description champ_gazebo ldlidar_node ldlidar_stl_ros2 gazebo_plugins gazebo_ros gazebo_ros_pkgs gazebo_ros2_control velodyne_gazebo_plugins"

# Build incrementally — start with core packages to catch errors early
colcon build --symlink-install --packages-up-to mini_pupper_description

# If that succeeds, build everything
colcon build --symlink-install

# Source the workspace
source install/setup.bash

# Add to .bashrc so it's sourced automatically in every new terminal
echo "source ~/mini_pupper_ws/install/setup.bash" >> ~/.bashrc
```

### Troubleshooting build failures

| Error pattern | Likely cause | Fix |
|---|---|---|
| `Cannot locate rosdep definition for [velodyne_gazebo_plugins]` | Gazebo Classic dep in champ | Add to `--skip-keys` (already done above) |
| `Cannot locate rosdep definition for [gazebo_ros2_control]` | Gazebo Classic dep in champ | Add to `--skip-keys` (already done above) |
| `find_package(gazebo_ros) FAILED` | champ_gazebo building | Add COLCON_IGNORE — see Section A3a |
| `Could not find package champ_base` | champ didn't compile | Check COLCON_IGNORE didn't hit champ_base |
| `CMake Error: cmake_minimum_required 3.16` | Old CMake | `sudo apt install cmake` |
| `fatal error: gz/sim/...` | Missing Gazebo dev headers | `sudo apt install libgz-sim8-dev` |
| `No module named 'MangDang'` | Hardware-only BSP package | Expected on PC — only needed on robot |
| Python `SyntaxError` in setup.py | Python 3.12 removed distutils | Change to `from setuptools import setup` |

---

## A5. Test Simulation — Gazebo Harmonic

### A5a. Launch the simulation

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

### A5b. Verify the robot loaded correctly

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

## A6. Verify ros_gz_bridge Topics

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

## A7. Test SLAM in Simulation

### SLAM Toolbox (recommended)

Each terminal needs the environment sourced. Open three separate terminals:

```bash
# Terminal 1 — Launch the simulation
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROBOT_MODEL=mini_pupper_2
ros2 launch mini_pupper_simulation main.launch.py
```

```bash
# Terminal 2 — Launch SLAM
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROBOT_MODEL=mini_pupper_2
ros2 launch mini_pupper_slam slam.launch.py use_sim_time:=true
```

```bash
# Terminal 3 — Teleoperate the robot (drive it around to build the map)
source /opt/ros/jazzy/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Teleop keys:** `i`=forward, `,`=backward, `j`=turn left, `l`=turn right,
`k`=stop, `q`/`z`=increase/decrease speed.

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

## A8. Test Navigation in Simulation

```bash
# Terminal 1 — Launch the simulation
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROBOT_MODEL=mini_pupper_2
ros2 launch mini_pupper_simulation main.launch.py
```

```bash
# Terminal 2 — Launch Navigation (use the map you saved in A7)
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch mini_pupper_navigation navigation.launch.py \
  use_sim_time:=true \
  map:=$HOME/maps/sim_map.yaml
```

**Verify:**
- Nav2 nodes start without errors.
- Both `lifecycle_manager_localization` and `lifecycle_manager_navigation`
  report "Managed nodes are active" in the terminal.
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

### MangDang BSP (Board Support Packages)

The hardware driver nodes (`servo_interface`, `imu_interface`,
`display_interface`) import MangDang-specific Python packages:
- `MangDang.mini_pupper.HardwareInterface` (servos)
- `MangDang.mini_pupper.ESP32Interface` (IMU via ESP32)
- `MangDang.LCD.ST7789` (LCD display)

**If you are using MangDang's pre-built ROS image** (recommended for Humble),
these packages are already pre-installed — no action needed.

**For Ubuntu 24.04 (Jazzy) fresh installs**, you need the patched BSP that
supports Noble / Python 3.12.  We maintain a fork with the necessary fixes:

```bash
cd ~
git clone https://github.com/MushfiqueTM/mini_pupper_bsp.git mini_pupper_bsp
cd mini_pupper_bsp
./install.sh
sudo reboot
```

The patched BSP handles:
- PEP 668 (`--break-system-packages`) for pip on Ubuntu 24.04
- DEB822 apt sources format (Noble uses `/etc/apt/sources.list.d/ubuntu.sources`)
- Latest setuptools (instead of pinned 58.2.0 which breaks on Python 3.12)
- libcamera-native camera support (skips legacy `start_x=1` / `gpu_mem=128`)

After reboot, verify the BSP installed correctly:
```bash
python3 -c "from MangDang.mini_pupper.HardwareInterface import HardwareInterface; print('BSP OK')"
calibrate  # should open the servo calibration tool
```

> **Note:** The original upstream BSP
> (<https://github.com/mangdangroboticsclub/mini_pupper_2_bsp>) targets
> Ubuntu 22.04 / Python 3.10 only.  Our fork adds Ubuntu 24.04 support
> while remaining backward-compatible with 22.04.

---

## B2. Robot Workspace Setup & Build

```bash
mkdir -p ~/mini_pupper_ws/src && cd ~/mini_pupper_ws/src

# Clone your fork
git clone -b ros2-jazzy https://github.com/MushfiqueTM/mini_pupper_ros.git

# Import external repos
cd mini_pupper_ros
vcs import ~/mini_pupper_ws/src < .minipupper.repos

# Initialize champ submodule (libchamp headers)
cd ~/mini_pupper_ws/src/champ/champ
git submodule update --init --recursive

# Disable broken Gazebo Classic champ packages (same as Section A3a)
for pkg in champ_gazebo champ_description champ_bringup champ_navigation champ_config; do
  touch ~/mini_pupper_ws/src/champ/champ/$pkg/COLCON_IGNORE
done
```

> **Pre-configured:** LiDAR config (LD06, `lidar_link`, `/dev/ldlidar`) and
> EKF config (corrected IMU fusion, reduced frequencies for Raspberry Pi) are
> already included in `mini_pupper_ros`.  No manual edits to upstream repos
> are needed.

Now continue with rosdep and building:

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash

# Install rosdep dependencies
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="champ_base champ_teleop champ_description champ_gazebo ldlidar_node ldlidar_stl_ros2 gazebo_plugins gazebo_ros gazebo_ros_pkgs gazebo_ros2_control velodyne_gazebo_plugins"

# Build the workspace
colcon build --symlink-install

# Source the workspace
source install/setup.bash

# Add to .bashrc so it's sourced automatically in every new terminal
echo "source ~/mini_pupper_ws/install/setup.bash" >> ~/.bashrc
```

> **Tip:** Building on a Raspberry Pi is slow.  Consider cross-compiling on
> your PC or using `colcon build --packages-select <pkg>` to build only the
> packages you need.

---

## B3. Hardware Bringup

> **Pre-configured:** The ESP32 proxy service fix (`Type=simple` + socket
> permissions) is already included in the
> [mini_pupper_bsp](https://github.com/MushfiqueTM/mini_pupper_bsp) repo.
> If you installed the BSP from our fork (Section B1), no manual service
> file edits are needed.
>
> You can verify it's working with:
> ```bash
> sudo systemctl status esp32-proxy
> # Should show: active (running)
> ```

### Launch the hardware bringup

Make sure to kill any leftover ROS processes from previous runs first:

```bash
# Kill any zombie ROS/DDS processes from previous runs
sudo killall -9 component_container_isolated lifecycle_manager ros2 2>/dev/null

cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# Set the robot model
export ROBOT_MODEL=mini_pupper_2   # or mini_pupper for v1

# Launch the full hardware bringup
ros2 launch mini_pupper_bringup bringup.launch.py hardware_connected:=true
```

### Verify hardware topics

In a **second terminal on the robot** (or SSH session):

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

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

> **Note:** You may see `ekf_node: Failed to meet update rate!` warnings in
> the bringup terminal.  This is **benign** on the Raspberry Pi — the CPU
> occasionally cannot sustain the target EKF frequency under full load, but it
> does not affect robot operation.

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
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# Drive the robot with keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Teleop keys:** `i`=forward, `,`=backward, `j`=turn left, `l`=turn right,
`k`=stop, `q`/`z`=increase/decrease speed.

**Verify:**
- The robot responds to keyboard commands.
- All four legs move correctly.
- The robot walks forward, backward, turns left, turns right.

### [On the robot]

If you prefer to test directly on the robot via SSH:

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## B5. Real-World SLAM

### [On the robot] — Start SLAM

Open a **second SSH terminal** to the robot (keep bringup running in the first):

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROBOT_MODEL=mini_pupper_2

# Make sure bringup is running (Section B3), then:
ros2 launch mini_pupper_slam slam_toolbox.launch.py use_sim_time:=false
```

### [On your PC] — Visualise and drive

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# Open RViz to see the map being built
rviz2
# In RViz: Add displays for Map (/map), LaserScan (/scan), TF, RobotModel
```

```bash
# In another terminal on your PC — drive the robot around
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive the robot slowly around the room.  Watch the map build in RViz.

### [On the robot or PC] — Save the map

```bash
source /opt/ros/jazzy/setup.bash

mkdir -p ~/maps
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_room
```

This creates `my_room.yaml` and `my_room.pgm`.  Transfer these to your PC if
you saved them on the robot:

```bash
# [On your PC]
scp mushfiquetm@<robot-ip>:~/maps/my_room.* ~/maps/
```

---

## B6. Real-World Navigation

### [On the robot] — Start navigation

Open a **second SSH terminal** to the robot (keep bringup running in the first):

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROBOT_MODEL=mini_pupper_2

# Make sure bringup is running (Section B3), then:
ros2 launch mini_pupper_navigation navigation.launch.py \
  use_sim_time:=false \
  map:=$HOME/maps/my_room.yaml
```

### [On your PC] — Send goals via RViz

```bash
cd ~/mini_pupper_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

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

**Early migration (code structure, build system, Gazebo, CI):**

| File | Change |
|---|---|
| All 7 `CMakeLists.txt` | Bumped `cmake_minimum_required` to 3.16 |
| `mini_pupper_simulation/CMakeLists.txt` | Removed invalid `find_package` for runtime deps |
| `mini_pupper_description/CMakeLists.txt` | Removed invalid `find_package` for runtime deps |
| `mini_pupper_description/urdf/*/mini_pupper_description.urdf.xacro` | Replaced Gazebo Classic plugins with Harmonic-native sensors |
| `mini_pupper_simulation/worlds/empty.sdf` | **New** — SDF 1.9 world file |
| `mini_pupper_simulation/worlds/mini_pupper_home.sdf` | **New** — SDF 1.9 world file with room/obstacles |
| `mini_pupper_simulation/launch/gazebo.launch.py` | Updated to use `.sdf` world files |
| `mini_pupper_simulation/launch/main.launch.py` | Added `ros_gz_bridge` node for clock, LiDAR, IMU |
| `mini_pupper_description/config/ros_control/mini_pupper_controller.yaml` | Fixed controller name (`joint_state_broadcaster`) |
| `mini_pupper_slam/launch/slam.launch.py` | Fixed argument passing to cartographer |
| `mini_pupper_slam/launch/slam_toolbox.launch.py` | Fixed `PathJoinSubstitution` usage |
| `mini_pupper_driver/.../curvature_compensation.py` | Added proper `rclpy.shutdown()` |
| `mini_pupper_driver/.../nav_vel_scaler.py` | Added proper `rclpy.shutdown()` |
| `mini_pupper_driver/package.xml` | Fixed dependency types |
| `mini_pupper_music/package.xml` | Added missing dependencies |
| `.github/workflows/industrial_ci.yml` | Updated skip keys + actions version |
| Multiple `package.xml` files | Removed invalid `<author>` tags for schema compliance |
| 36+ Python files across 11 packages | Fixed flake8 code style (Q000, C812, I100, E501, etc.) |

**Final audit fixes (latest commit):**

| File | Change |
|---|---|
| `entrypoint.sh` | `source /opt/ros/humble/setup.bash` → `source /opt/ros/jazzy/setup.bash` |
| `pc_install.sh` | `ros-jazzy-gazebo-ros2-control` → `ros-jazzy-gz-ros2-control` |
| `pupper_install.sh` | Same package name fix (in comment) |
| `mini_pupper_description/urdf/mini_pupper/mini_pupper_description.urdf.xacro` | `gz_ros2_control/GZSimSystem` → `gz_ros2_control/GazeboSimSystem` |
| `mini_pupper_description/urdf/mini_pupper_2/mini_pupper_description.urdf.xacro` | Same plugin name fix |
| `mini_pupper_description/urdf/mini_pupper/d435.urdf.xacro` | Replaced Gazebo Classic `libgazebo_ros_openni_kinect.so` with Harmonic `depth_camera` sensor |
| `stanford_controller/.../stanford_controller_node.py` | Added `rclpy.shutdown()` |
| `stanford_controller/.../twist_to_command_node.py` | Added `rclpy.shutdown()` |
| `mini_pupper_recognition/.../line_detection_node.py` | Added `try/except/finally` with `rclpy.shutdown()` |
| `mini_pupper_recognition/.../cloud_line_recognition_node.py` | Added `try/except/finally` with `rclpy.shutdown()` |
| `mini_pupper_navigation/param/real_table.yaml` | Removed 9 deprecated `*_rclcpp_node`/`*_client` blocks + Groot v1 ZMQ params |
| `mini_pupper_navigation/param/mini_pupper.yaml` | Fixed `use_sim_time: False` → `True` in both costmap sections |
| `mini_pupper_simulation/worlds/empty.world` | **Deleted** — dead Gazebo Classic file |
| `mini_pupper_simulation/worlds/mini_pupper_home.world` | **Deleted** — dead Gazebo Classic file |
| 6 `setup.py` files | `install_requires=['setuptools']` → `install_requires=[]` |
| `QUICK_START.md`, `REFERENCE_REPOSITORIES.md` | Fixed wrong `ros-jazzy-gazebo-ros2-control` package name |

**Nav2 Jazzy runtime fixes (navigation activation):**

| File | Change |
|---|---|
| `mini_pupper_navigation/param/mini_pupper.yaml` | Replaced Humble-era `plugin_lib_names` with Jazzy `navigators` config for `bt_navigator` |
| `mini_pupper_navigation/param/real_table.yaml` | Same `bt_navigator` fix |
| `mini_pupper_navigation/param/mini_pupper.yaml` | Fixed plugin names from slash format (`/`) to Jazzy double-colon format (`::`) |
| `mini_pupper_navigation/param/real_table.yaml` | Same plugin name format fix |
| `mini_pupper_navigation/param/mini_pupper.yaml` | Added missing Jazzy nodes: `velocity_smoother`, `smoother_server`, `route_server`, `collision_monitor`, `docking_server` |
| `mini_pupper_navigation/param/mini_pupper.yaml` | Added `lifecycle_manager_localization` and `lifecycle_manager_navigation` with `autostart: true` |

---

## C3. Summary Checklist

### PC Tasks

- [ ] Ubuntu 24.04 + ROS 2 Jazzy installed and sourced
- [ ] Gazebo Harmonic packages installed
- [ ] Workspace cloned and external repos imported via `vcs`
- [ ] `rosdep` dependencies installed
- [ ] **COLCON_IGNORE** added to broken champ packages (Section A3a)
- [ ] `champ`, `champ_base`, `champ_msgs` build successfully
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
