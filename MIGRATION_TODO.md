# ROS 2 Jazzy Migration - Manual TODO List

> **This document lists everything YOU need to do yourself** that I couldn't automate.

---

## 🔴 CRITICAL - Must Do Before First Build

### 1. Check/Update External Dependencies (`.minipupper.repos`)

**File:** `.minipupper.repos`

The external repositories may not have Jazzy branches yet. You need to verify:

```yaml
repositories:
  champ/champ:
    type: git
    url: https://github.com/mangdangroboticsclub/champ.git
    version: ros2  # <-- CHECK: May need 'jazzy' branch
  
  champ/champ_teleop:
    type: git
    url: https://github.com/chvmp/champ_teleop.git
    version: ros2  # <-- CHECK: May need Jazzy branch
  
  ldlidar_stl_ros:
    type: git
    url: https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2.git
    version: master  # <-- CHECK: Verify Jazzy compatibility
```

**What you need to do:**
1. Visit each repository on GitHub
2. Check if they have a `jazzy` or `ros2-jazzy` branch
3. If yes, update the `version` field in `.minipupper.repos`
4. If no, try building with `ros2` branch and report issues

---

### 2. Install BSP (Board Support Package) for Ubuntu 24.04

**I cannot do this for you - it requires hardware access.**

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

**Note:** The BSP may need updates for Ubuntu 24.04. Check the repository issues.

---

### 3. Verify Gazebo Harmonic Plugin Names

**Files:** 
- `mini_pupper_description/urdf/mini_pupper_2/mini_pupper_description.urdf.xacro`
- `mini_pupper_description/urdf/mini_pupper/mini_pupper_description.urdf.xacro`

I updated the plugin names, but **you need to verify they work** with your Gazebo Harmonic installation:

```xml
<!-- I CHANGED this: -->
<plugin>gz_ros2_control/GazeboSimSystem</plugin>
<plugin filename="libgz_ros2_control.so" name="gz_ros2_control">

<!-- If build fails, try these alternatives: -->
<plugin>gz_ros2_control/GzSystem</plugin>
<plugin filename="libgz_ros2_control-system.so" name="gz_ros2_control">
```

**How to verify:**
```bash
# After installing Gazebo Harmonic, check available plugins
apt list --installed | grep gz-ros2-control
dpkg -L ros-jazzy-gz-ros2-control | grep .so
```

---

## 🟡 IMPORTANT - Test and Verify

### 4. Test Build Process

```bash
cd ~/ros2_ws

# Clean previous builds
rm -rf build/ install/ log/

# Source ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# Import dependencies
vcs import < src/mini_pupper_ros/.minipupper.repos --recursive

# Install dependencies
rosdep install --from-paths src --ignore-src -r -y --rosdistro=jazzy

# Build
 colcon build --symlink-install
```

**If build fails:**
- Check which package fails
- Look for missing dependencies
- Check Gazebo Harmonic plugin compatibility

---

### 5. Update Launch Files if Needed

**Files to check:**
- `mini_pupper_bringup/launch/*.launch.py`
- `mini_pupper_driver/launch/*.launch.py`

**Look for:**
- References to `gazebo_ros` (should be `ros_gz_sim`)
- References to `gazebo_ros2_control` (should be `gz_ros2_control`)
- Old package names that need updating

---

### 6. World Files for Gazebo Harmonic

**Files:**
- `mini_pupper_simulation/worlds/empty.world`
- `mini_pupper_simulation/worlds/mini_pupper_home.world`

**Check for:**
- Old Gazebo Classic-specific plugins
- Material references that may not work in Harmonic
- SDF version compatibility

**Test with:**
```bash
ros2 launch mini_pupper_simulation gazebo.launch.py
```

---

## 🟢 NICE TO HAVE - Polish

### 7. Update Package READMEs

Several packages have `README.md` files that may reference ROS 2 Humble:

```bash
# Find all README files
grep -r "Humble\|humble\|22.04" --include="README.md" .

# Update them to reference Jazzy/Ubuntu 24.04
```

---

### 8. Create Pre-built Image Instructions

The documentation references pre-built images that don't exist yet for Jazzy:

**Files to update:**
- `README.md`
- `docs/detailed-setup-guide.md`

**Add note:**
```markdown
> **Pre-built images for ROS 2 Jazzy are coming soon!** 
> For now, please follow the manual installation instructions below.
```

---

### 9. Test All Functionality

Create a test checklist:

#### Basic Movement
- [ ] `ros2 launch mini_pupper_bringup bringup.launch.py`
- [ ] Teleop with keyboard: `ros2 run teleop_twist_keyboard teleop_twist_keyboard`
- [ ] Teleop with joystick: `ros2 launch teleop_twist_joy teleop-launch.py`

#### Simulation
- [ ] `ros2 launch mini_pupper_simulation main.launch.py`
- [ ] Robot spawns without errors
- [ ] RViz shows robot model
- [ ] Can control robot in Gazebo

#### SLAM
- [ ] `ros2 launch mini_pupper_slam slam.launch.py`
- [ ] Can create map
- [ ] `ros2 run nav2_map_server map_saver_cli -f ~/map`

#### Navigation
- [ ] `ros2 launch mini_pupper_navigation navigation.launch.py`
- [ ] Can set nav goals

#### Advanced Features
- [ ] Tracking: `ros2 launch mini_pupper_tracking tracking.launch.py`
- [ ] Dance: `ros2 launch mini_pupper_dance dance.launch.py`
- [ ] Recognition: `ros2 launch mini_pupper_recognition recognition.launch.py`

---

## 🔧 TROUBLESHOOTING - Common Issues

### Issue 1: Gazebo Plugins Not Found

**Error:**
```
[ERROR] [gz_ros2_control]: Failed to create system plugin
```

**Solution:**
Check actual plugin names installed:
```bash
# Find all gz_ros2_control plugins
find /opt/ros/jazzy -name "*gz_ros2_control*" -type f

# Check correct plugin name
strings /opt/ros/jazzy/lib/libgz_ros2_control.so | grep -i system
```

### Issue 2: External Dependencies Fail

**Error:**
```
Could not find a package configuration file provided by "champ"
```

**Solution:**
```bash
# Check if champ has Jazzy branch
cd ~/ros2_ws/src/champ/champ
git branch -a | grep -i jazzy

# If exists, checkout that branch
git checkout jazzy  # or ros2-jazzy
```

### Issue 3: Python Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'mini_pupper_interfaces'
```

**Solution:**
```bash
# Rebuild with symlink install
cd ~/ros2_ws
colcon build --symlink-install --packages-select mini_pupper_interfaces

# Source workspace
source install/setup.bash
```

### Issue 4: Camera/Image Topics Not Working

**Error:**
Camera image topics not publishing in Gazebo.

**Solution:**
Gazebo Harmonic uses different camera plugin names. Update URDF:
```xml
<!-- Old (Gazebo Classic) -->
<plugin name="camera_controller" filename="libgazebo_ros_camera.so">

<!-- New (Gazebo Harmonic) - may need: -->
<plugin name="camera_controller" filename="libgz_ros2_camera.so">
```

---

## 📋 BEFORE YOU START - Checklist

- [ ] Installed Ubuntu 24.04 on Mini Pupper
- [ ] Installed Ubuntu 24.04 on PC (for simulation)
- [ ] Installed BSP on Mini Pupper
- [ ] Cloned this repository
- [ ] Checked external dependency branches (champ, etc.)
- [ ] Verified Gazebo Harmonic installation
- [ ] Backed up any important data

---

## 📞 NEED HELP?

If you encounter issues:

1. **Check GitHub Issues:**
   - https://github.com/mangdangroboticsclub/mini_pupper_ros/issues
   - Look for `jazzy` or `migration` labels

2. **Join Discord:**
   - https://discord.gg/xJdt3dHBVw

3. **Create New Issue with:**
   - Ubuntu version: `lsb_release -a`
   - ROS version: `echo $ROS_DISTRO`
   - Error message (full traceback)
   - What you were trying to do
   - Steps to reproduce

---

## ✅ VERIFICATION SCRIPT

Save this as `verify_jazzy_migration.sh` and run it:

```bash
#!/bin/bash

echo "=== ROS 2 Jazzy Migration Verification ==="
echo

echo "1. Checking Ubuntu version..."
lsb_release -a | grep "Description"

echo
echo "2. Checking ROS 2 version..."
echo "ROS_DISTRO: $ROS_DISTRO"

echo
echo "3. Checking Python version..."
python3 --version

echo
echo "4. Checking Gazebo version..."
gz sim --version 2>/dev/null || echo "Gazebo Harmonic not found"

echo
echo "5. Checking key ROS packages..."
dpkg -l | grep -E "ros-jazzy-(gz-ros2-control|ros-gz|navigation2)" | awk '{print $2, $3}'

echo
echo "6. Checking workspace..."
if [ -d ~/ros2_ws ]; then
    echo "Workspace exists: ~/ros2_ws"
    ls ~/ros2_ws/src/ | head -5
else
    echo "WARNING: Workspace not found at ~/ros2_ws"
fi

echo
echo "=== Verification Complete ==="
```

---

**Last Updated:** 2025-02-11  
**Migration Version:** 1.0.0
