# ROS 2 Humble to Jazzy Migration Guide

> **⚠️ CRITICAL WARNING:** This migration requires **Ubuntu 24.04 (Noble Numbat)**. ROS 2 Jazzy does NOT work on Ubuntu 22.04.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [System Requirements](#system-requirements)
4. [Migration Steps](#migration-steps)
5. [Package Changes Summary](#package-changes-summary)
6. [Breaking Changes](#breaking-changes)
7. [Gazebo Migration (Critical)](#gazebo-migration-critical)
8. [Troubleshooting](#troubleshooting)
9. [Verification Checklist](#verification-checklist)

---

## Overview

This guide documents the complete migration of Mini Pupper ROS from **ROS 2 Humble** (Ubuntu 22.04) to **ROS 2 Jazzy** (Ubuntu 24.04).

### Key Changes at a Glance

| Component | Humble | Jazzy |
|-----------|--------|-------|
| Ubuntu Version | 22.04 (Jammy) | 24.04 (Noble) |
| ROS Distribution | Humble Hawksbill | Jazzy Jalisco |
| Python Version | 3.10 | 3.12 |
| Gazebo Version | Gazebo Classic (11) | Gazebo Harmonic (gz) |
| Gazebo ROS Package | `gazebo_ros` | `ros_gz_sim` |

---

## Prerequisites

### Hardware Requirements

- **Mini Pupper or Mini Pupper 2** with Raspberry Pi 4
- **SD Card:** Minimum 64GB (fresh install recommended)
- **PC:** For simulation and remote control (Ubuntu 24.04)

### Software Requirements

- **Ubuntu 24.04 LTS (Noble Numbat)** - REQUIRED
- **Internet connection** for downloading packages
- **BSP (Board Support Package)** for Mini Pupper must be installed first

---

## System Requirements

### IMPORTANT: You MUST Upgrade to Ubuntu 24.04

ROS 2 Jazzy **cannot** run on Ubuntu 22.04. You have two options:

#### Option 1: Fresh Install (Recommended)

1. Download Ubuntu 24.04 Server for Raspberry Pi
2. Flash to SD card using Raspberry Pi Imager or BalenaEtcher
3. Install BSP for Mini Pupper first
4. Then follow installation steps below

#### Option 2: In-Place Upgrade (Not Recommended for Raspberry Pi)

```bash
# WARNING: This may break your system. Fresh install is preferred.
sudo do-release-upgrade -d
```

---

## Migration Steps

### Step 1: Backup Your Data

Before starting, backup any important data:

```bash
# Backup your ROS workspace
cd ~
tar -czf ros2_ws_backup_$(date +%Y%m%d).tar.gz ros2_ws/

# Backup your maps and configurations
cp -r ~/ros2_ws/src/mini_pupper_ros/mini_pupper_navigation/maps ~/maps_backup
cp -r ~/.bashrc ~/.bashrc.backup
```

### Step 2: Install Ubuntu 24.04

#### For Raspberry Pi (Mini Pupper):

1. Download Ubuntu 24.04 Server for Raspberry Pi:
   ```bash
   # From Ubuntu official website
   wget https://cdimage.ubuntu.com/ubuntu-server/noble/daily-preinstalled/current/noble-preinstalled-server-arm64+raspi.img.xz
   ```

2. Flash to SD card using Raspberry Pi Imager or `dd`:
   ```bash
   # Using dd (replace sdX with your SD card device)
   xzcat noble-preinstalled-server-arm64+raspi.img.xz | sudo dd of=/dev/sdX bs=4M status=progress
   ```

3. Boot the Raspberry Pi and complete initial setup

#### For PC:

1. Download Ubuntu 24.04 Desktop from https://ubuntu.com/download
2. Create bootable USB using Rufus (Windows) or BalenaEtcher
3. Install Ubuntu 24.04

### Step 3: Install BSP (Board Support Package)

**For Mini Pupper 2:**
```bash
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_2_bsp.git
cd mini_pupper_2_bsp
./install.sh
```

**For Mini Pupper (Original):**
```bash
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_bsp.git
cd mini_pupper_bsp
./install.sh
```

### Step 4: Install ROS 2 Jazzy and Mini Pupper Packages

#### On Mini Pupper (Raspberry Pi):

```bash
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-dev mini_pupper_ros
cd mini_pupper_ros
./pupper_install.sh
```

**Note:** The script will automatically:
- Check for Ubuntu 24.04
- Install ROS 2 Jazzy
- Install all dependencies
- Build the workspace

#### On PC:

```bash
cd ~
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-dev mini_pupper_ros
cd mini_pupper_ros
./pc_install.sh
```

### Step 5: Update Environment Variables

Edit your `.bashrc` file:

```bash
nano ~/.bashrc
```

Add or update these lines at the end:

```bash
# ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash

# ROS Domain ID (must match between PC and robot)
export ROS_DOMAIN_ID=42

# Robot Model
export ROBOT_MODEL=mini_pupper_2  # or mini_pupper

# Python path for Jazzy (Python 3.12)
export PYTHONPATH=$PYTHONPATH:~/ros2_ws/install/lib/python3.12/site-packages
```

Apply the changes:

```bash
source ~/.bashrc
```

### Step 6: Verify Installation

```bash
# Check ROS 2 version
ros2 --version

# Check Ubuntu version
lsb_release -a
# Should show: Ubuntu 24.04

# Test basic ROS 2 functionality
ros2 run demo_nodes_cpp talker
# In another terminal:
ros2 run demo_nodes_cpp listener
```

---

## Package Changes Summary

### All Packages Updated

| Package | Old Version | New Version | Changes |
|---------|-------------|-------------|---------|
| mini_pupper_bringup | 0.1.0 | 0.2.0 | Added ros_gz dependencies |
| mini_pupper_interfaces | 0.0.0 | 1.0.0 | Added builtin_interfaces dep |
| mini_pupper_driver | 0.0.1 | 1.0.0 | Added Python 3.12 support |
| mini_pupper_description | 0.2.0 | 1.0.0 | Added Gazebo Harmonic deps |
| stanford_controller | 1.0.0 | 2.0.0 | Added tf_transformations dep |
| mini_pupper_tracking | 0.0.0 | 1.0.0 | Updated for Jazzy |
| mini_pupper_navigation | 0.1.0 | 1.0.0 | Added slam_toolbox dep |
| mini_pupper_slam | 1.0.0 | 1.1.0 | Updated for Jazzy |
| mini_pupper_simulation | 1.0.0 | 2.0.0 | **Gazebo Harmonic migration** |
| mini_pupper_dance | 0.0.0 | 1.0.0 | Updated for Jazzy |
| mini_pupper_music | 1.0.0 | 1.1.0 | Updated for Jazzy |
| mini_pupper_recognition | 0.0.1 | 1.0.0 | Updated for Jazzy |
| mini_pupper_fleet | 0.0.1 | 1.0.0 | Added tf2_geometry_msgs dep |

---

## Breaking Changes

### 1. Gazebo Migration (CRITICAL)

**OLD (Humble):**
```xml
<!-- package.xml -->
<exec_depend>gazebo_ros</exec_depend>
<exec_depend>gazebo_ros_pkgs</exec_depend>
<exec_depend>gazebo_ros2_control</exec_depend>
```

**NEW (Jazzy):**
```xml
<!-- package.xml -->
<exec_depend>ros_gz</exec_depend>
<exec_depend>ros_gz_sim</exec_depend>
<exec_depend>gz_ros2_control</exec_depend>
```

**OLD Launch File (Humble):**
```python
from launch_ros.substitutions import FindPackageShare

gazebo_launch_path = PathJoinSubstitution([
    FindPackageShare('gazebo_ros'),
    'launch',
    'gazebo.launch.py'
])

spawn_entity = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    ...
)
```

**NEW Launch File (Jazzy):**
```python
gz_sim_launch_path = PathJoinSubstitution([
    FindPackageShare('ros_gz_sim'),
    'launch',
    'gz_sim.launch.py'
])

spawn_entity = Node(
    package='ros_gz_sim',
    executable='create',
    ...
)
```

### 2. Package Names Changed

| Old Package (Humble) | New Package (Jazzy) |
|---------------------|---------------------|
| ros-humble-* | ros-jazzy-* |
| gazebo_ros | ros_gz_sim |
| gazebo_ros2_control | gz_ros2_control |
| gazebo_plugins | gz_plugins |

### 3. Python Version Change

**OLD (Python 3.10):**
```bash
pip3 install simple_pid
```

**NEW (Python 3.12):**
```bash
pip3 install simple_pid --break-system-packages
# OR use venv (recommended)
```

### 4. Installation Scripts

**OLD (Humble):**
```bash
~/ros2_setup_scripts_ubuntu/ros2-humble-ros-base-main.sh
```

**NEW (Jazzy):**
```bash
~/ros2_setup_scripts_ubuntu/ros2-jazzy-ros-base-main.sh
```

### 5. Ubuntu Version Check

**OLD (Humble):**
```bash
if [[ $UBUNTU_CODENAME != 'jammy' ]]
```

**NEW (Jazzy):**
```bash
if [[ $UBUNTU_CODENAME != 'noble' ]]
```

---

## Gazebo Migration (Critical)

### What Changed?

ROS 2 Jazzy uses **Gazebo Harmonic** (formerly Ignition Gazebo), which is completely different from Gazebo Classic used in Humble.

### Key Differences

1. **Package Names:**
   - Gazebo Classic: `gazebo_ros`, `gazebo_ros_pkgs`
   - Gazebo Harmonic: `ros_gz_sim`, `ros_gz_bridge`

2. **Spawn Entity:**
   - Old: `gazebo_ros spawn_entity.py`
   - New: `ros_gz_sim create`

3. **Launch Files:**
   - Old: `gazebo_ros.launch.py`
   - New: `gz_sim.launch.py`

4. **World Files:**
   - Both use SDF format, but Gazebo Harmonic uses SDF 1.10+
   - Some plugins may not be compatible

### Running Simulation

**OLD (Humble):**
```bash
ros2 launch mini_pupper_simulation main.launch.py
```

**NEW (Jazzy):**
```bash
# Same command, but internally uses Gazebo Harmonic
ros2 launch mini_pupper_simulation main.launch.py
```

### Known Issues

1. **Contact Sensor:** The `champ_gazebo` contact sensor may not work with Gazebo Harmonic yet. A workaround is implemented that skips this feature.

2. **World Files:** Some complex world files may need manual conversion. Basic worlds should work as-is.

---

## Troubleshooting

### Issue 1: Wrong Ubuntu Version

**Error:**
```
Ubuntu 24.04 LTS (Noble Numbat) is required
You are using Ubuntu 22.04.4 LTS
```

**Solution:** You must upgrade to Ubuntu 24.04. See [System Requirements](#system-requirements).

### Issue 2: Missing Gazebo Packages

**Error:**
```
Package 'gazebo_ros' not found
```

**Solution:** Install Gazebo Harmonic packages:
```bash
sudo apt install ros-jazzy-ros-gz ros-jazzy-gz-ros2-control
```

### Issue 3: Python Package Installation Failures

**Error:**
```
error: externally-managed-environment
```

**Solution:** Use `--break-system-packages` flag or create a virtual environment:
```bash
# Option 1: Use flag (for system-wide install)
pip3 install simple_pid --break-system-packages

# Option 2: Use venv (recommended for development)
python3 -m venv ~/ros2_venv
source ~/ros2_venv/bin/activate
pip install simple_pid
```

### Issue 4: rosdep Failures

**Error:**
```
rosdep install: failed to detect OS
```

**Solution:** Update rosdep:
```bash
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro=jazzy
```

### Issue 5: Build Failures

**Error:**
```
CMake Error: Could not find a package configuration file provided by "gazebo_ros"
```

**Solution:** Clean and rebuild:
```bash
cd ~/ros2_ws
rm -rf build/ install/ log/
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

### Issue 6: Import Errors in Python

**Error:**
```
ModuleNotFoundError: No module named 'mini_pupper_interfaces'
```

**Solution:** Source the workspace and check PYTHONPATH:
```bash
source ~/ros2_ws/install/setup.bash
echo $PYTHONPATH
```

---

## Verification Checklist

### Basic System Check

- [ ] Ubuntu 24.04 is installed (`lsb_release -a`)
- [ ] ROS 2 Jazzy is installed (`ros2 --version`)
- [ ] Workspace is built successfully (`colcon build`)
- [ ] Environment is sourced (`echo $ROS_DISTRO` should show "jazzy")

### Hardware Check (Mini Pupper)

- [ ] BSP is installed correctly
- [ ] Servos respond to commands
- [ ] LCD display works
- [ ] IMU publishes data
- [ ] LiDAR works (if equipped)
- [ ] Camera works (if equipped)

### Simulation Check (PC)

- [ ] Gazebo Harmonic launches (`ros2 launch mini_pupper_simulation main.launch.py`)
- [ ] Robot model loads correctly
- [ ] Teleop works (`ros2 run teleop_twist_keyboard teleop_twist_keyboard`)
- [ ] RViz displays robot model

### Navigation Check

- [ ] SLAM works (`ros2 launch mini_pupper_slam slam.launch.py`)
- [ ] Map can be saved (`ros2 run nav2_map_server map_saver_cli -f ~/map`)
- [ ] Navigation stack launches (`ros2 launch mini_pupper_navigation navigation.launch.py`)

### Advanced Features

- [ ] Tracking works (`ros2 launch mini_pupper_tracking tracking.launch.py`)
- [ ] Dance mode works (`ros2 launch mini_pupper_dance dance.launch.py`)
- [ ] Music plays (`ros2 service call /play_music mini_pupper_interfaces/srv/PlayMusic`)

---

## Additional Resources

- [ROS 2 Jazzy Documentation](https://docs.ros.org/en/jazzy/)
- [Gazebo Harmonic Documentation](https://gazebosim.org/docs/harmonic/)
- [Ubuntu 24.04 Release Notes](https://discourse.ubuntu.com/t/noble-numbat-release-notes/39890)
- [Mini Pupper Documentation](https://minipupperdocs.readthedocs.io/)

---

## Support

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/mangdangroboticsclub/mini_pupper_ros/issues)
2. Join the [Discord Community](https://discord.gg/xJdt3dHBVw)
3. Create a new issue with:
   - Ubuntu version (`lsb_release -a`)
   - ROS version (`echo $ROS_DISTRO`)
   - Error messages (full traceback)
   - Steps to reproduce

---

**Last Updated:** 2025-02-11

**Migration Version:** 1.0.0

**Maintainer:** MangDang (fae@mangdang.net)
