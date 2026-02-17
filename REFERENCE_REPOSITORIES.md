# Reference Repositories for Jazzy Migration

> **These repositories were analyzed to help with our ROS 2 Jazzy migration.**

---

## Repository 1: Unitree Go2 ROS2

**URL:** https://github.com/khaledgabr77/unitree_go2_ros2

### Why It's Valuable

This is a **complete working example** of:
- ROS 2 Jazzy + CHAMP controller + Gazebo Harmonic
- Quadruped robot (same type as Mini Pupper)
- Ubuntu 24.04

### Key Reference Files

| File Path | Purpose |
|-----------|---------|
| `unitree_go2_sim/launch/unitree_go2_launch.py` | Gazebo Harmonic launch |
| `unitree_go2_description/urdf/` | URDF with gz plugins |
| `champ/` | Updated CHAMP for Jazzy |
| `config/gait/gait.yaml` | Gait parameters |

### Verified Dependencies

These packages work with ROS 2 Jazzy:

```bash
sudo apt install ros-jazzy-gazebo-ros2-control
sudo apt install ros-jazzy-xacro
sudo apt install ros-jazzy-robot-localization
sudo apt install ros-jazzy-ros2-controllers
sudo apt install ros-jazzy-ros2-control
sudo apt install ros-jazzy-velodyne
sudo apt install ros-jazzy-velodyne-description
```

### Gazebo Plugin Names Used

Based on their setup, they likely use:
- `gz_ros2_control/GazeboSimSystem` ✅
- `libgz_ros2_control.so` ✅

**Note:** If our plugins don't work, check their URDF files for exact plugin names.

---

## Repository 2: LD Robot Lidar ROS2

**URL:** https://github.com/Myzhar/ldrobot-lidar-ros2

### Why It's Valuable

- **Official ROS 2 Jazzy support**
- Modern lifecycle architecture (Nav2 style)
- Supports LD06, LD19, STL27L (our lidar models)
- Better than old `ldlidar_stl_ros2`

### Key Features

| Feature | Benefit |
|---------|---------|
| Lifecycle nodes | Proper state management |
| Lifecycle manager | Automatic activation |
| SLAM Toolbox example | Ready for navigation |
| udev rules | Proper device permissions |

### Installation (Different from Old Driver)

```bash
# 1. Clone
cd ~/ros2_ws/src
git clone https://github.com/Myzhar/ldrobot-lidar-ros2.git

# 2. Install dependencies
sudo apt install libudev-dev

# 3. Setup udev rules
cd ~/ros2_ws/src/ldrobot-lidar-ros2/scripts/
./create_udev_rules.sh

# 4. Build
cd ~/ros2_ws/
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --cmake-args=-DCMAKE_BUILD_TYPE=Release
```

### Usage (Different from Old Driver)

```bash
# Launch with lifecycle manager
ros2 launch ldlidar_node ldlidar_with_mgr.launch.py

# Or manual lifecycle
ros2 launch ldlidar_node ldlidar_bringup.launch.py
ros2 lifecycle set /ldlidar_node configure
ros2 lifecycle set /ldlidar_node activate
```

### Integration with Mini Pupper

**OLD (ldlidar_stl_ros2):**
```xml
<node pkg="ldlidar_stl_ros2" exec="ldlidar_stl_ros2_node" ...>
```

**NEW (ldrobot-lidar-ros2):**
```python
# Include in bringup launch file
include_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource([
        get_package_share_directory('ldlidar_node'),
        '/launch/ldlidar_with_mgr.launch.py'
    ])
)
```

---

## Recommendations

### 1. URDF Plugin Verification

Compare our URDF plugin names with Unitree Go2:

```bash
# Download Unitree Go2 for comparison
cd /tmp
git clone https://github.com/khaledgabr77/unitree_go2_ros2
grep -r "plugin" unitree_go2_ros2/unitree_go2_description/urdf/ | grep -i gazebo
```

### 2. Lidar Driver Migration

**Decision:** Use new `ldrobot-lidar-ros2` driver

**Pros:**
- ✅ Official Jazzy support
- ✅ Better architecture
- ✅ Active maintenance

**Cons:**
- ⚠️ Different launch interface
- ⚠️ Requires lifecycle management

**Migration Steps:**
1. Update `.minipupper.repos` ✅ Done
2. Update launch files to include `ldlidar_with_mgr.launch.py`
3. Update documentation
4. Test with hardware

### 3. Additional Dependencies to Install

Based on Unitree Go2, add to install scripts:

```bash
# Add these to pupper_install.sh and pc_install.sh
sudo apt install -y \
    ros-jazzy-gazebo-ros2-control \
    ros-jazzy-robot-localization \
    ros-jazzy-velodyne \
    ros-jazzy-velodyne-description
```

### 4. CHAMP Verification

Unitree Go2 uses CHAMP successfully on Jazzy. Our CHAMP dependency should work, but verify:

```bash
cd ~/ros2_ws/src/champ/champ
git log --oneline -5
# Check if there are Jazzy-specific commits
```

If issues arise, we can reference their `champ/` folder.

---

## Testing Checklist

Using these reference repos:

- [ ] Clone Unitree Go2 and verify it builds on Jazzy
- [ ] Launch their Gazebo sim to see working Harmonic setup
- [ ] Compare their URDF plugins with ours
- [ ] Install new lidar driver and test
- [ ] Integrate new lidar driver into Mini Pupper bringup

---

## Links

- **Unitree Go2 ROS2:** https://github.com/khaledgabr77/unitree_go2_ros2
- **LD Robot Lidar ROS2:** https://github.com/Myzhar/ldrobot-lidar-ros2
- **Original LD Lidar (old):** https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2

---

**Last Updated:** 2025-02-11
