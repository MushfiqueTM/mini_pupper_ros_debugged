# Quick Start - ROS 2 Jazzy Migration

## For Repository Maintainers (You)

```bash
# 1. Upload to GitHub
cd "c:\Users\mushf\OneDrive - The Hong Kong Polytechnic University\MangDang"
git init
git remote add origin https://github.com/mangdangroboticsclub/mini_pupper_ros.git
git add .
git commit -m "feat: ROS 2 Jazzy migration complete"
git checkout -b ros2-jazzy
git push -u origin ros2-jazzy

# 2. Create release
git tag -a v2.0.0-jazzy -m "ROS 2 Jazzy Release"
git push origin v2.0.0-jazzy
```

---

## For Mini Pupper Users

### Option 1: Fresh Install (Recommended)

```bash
# 1. Install Ubuntu 24.04
# Download from https://ubuntu.com/download/raspberry-pi

# 2. Install BSP (Board Support Package)
# See mini_pupper_bsp repository for Ubuntu 24.04 version

# 3. Clone and install
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-jazzy
cd mini_pupper_ros
./pupper_install.sh
```

### Option 2: Manual Installation

```bash
# Ubuntu 24.04 + ROS 2 Jazzy required
sudo apt update
sudo apt install -y ros-jazzy-ros-base ros-dev-tools

# Clone workspace
git clone https://github.com/mangdangroboticsclub/mini_pupper_ros.git -b ros2-jazzy ~/mini_pupper_ros
cd ~/mini_pupper_ros

# Install dependencies
sudo apt install -y ros-jazzy-xacro ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers ros-jazzy-robot-localization \
    ros-jazzy-ros-gz-sim ros-jazzy-gazebo-ros2-control \
    ros-jazzy-slam-toolbox ros-jazzy-nav2-bringup

# Build
colcon build --symlink-install
```

---

## For PC Users (Simulation)

```bash
# Ubuntu 24.04 + ROS 2 Jazzy Desktop required
wget https://raw.githubusercontent.com/mangdangroboticsclub/mini_pupper_ros/ros2-jazzy/pc_install.sh
chmod +x pc_install.sh
./pc_install.sh
```

---

## Verify Installation

```bash
# Source workspace
source install/setup.bash

# Check ROS version
ros2 --version  # Should show Jazzy

# Run simulation
ros2 launch mini_pupper_simulation main.launch.py

# Teleop control (in new terminal)
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## Key Differences from Humble

| Aspect | Humble | Jazzy |
|--------|--------|-------|
| Branch | `ros2` / `ros2-dev` | `ros2-jazzy` |
| Ubuntu | 22.04 | 24.04 |
| Gazebo | Classic | Harmonic |
| Python | 3.10 | 3.12 |
| Install script | `./pupper_install.sh` | `./pupper_install.sh` (updated) |

---

## Troubleshooting

### Issue: Package not found
```bash
# Make sure to source
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

### Issue: Gazebo doesn't open
```bash
# Check Gazebo is installed
which gz

# If not, install:
sudo apt install gz-harmonic ros-jazzy-ros-gz
```

### Issue: Permission denied on install script
```bash
chmod +x pupper_install.sh pc_install.sh
```

---

## Next Steps

1. **Test on real hardware** - Mini Pupper with Ubuntu 24.04
2. **Report issues** - Create GitHub issue if problems found
3. **Update wiki** - Once migration is stable
4. **Create pre-built image** - For easier user onboarding

---

## Documentation Links

- Full guide: `MIGRATION_JAZZY.md`
- Checklist: `MIGRATION_TODO.md`
- Changes: `MIGRATION_SUMMARY.md`
- Upload: `GITHUB_UPLOAD_GUIDE.md`
