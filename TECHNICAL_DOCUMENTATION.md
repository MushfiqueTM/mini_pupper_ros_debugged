# Mini Pupper ROS 2 - Technical Documentation

## Overview

This is a comprehensive ROS 2 Humble robotics platform for the Mini Pupper quadruped robot. It provides capabilities for autonomous navigation, computer vision, multi-robot coordination, and choreographed movements. The project runs on Ubuntu 22.04 with ROS 2 Humble.

**Project Repository:** https://github.com/mangdangroboticsclub/mini_pupper_ros  
**License:** Apache-2.0  
**Supported Hardware:** Mini Pupper, Mini Pupper 2

---

## Repository Structure

### Root Level Files

| File | Description |
|------|-------------|
| `README.md` | Main project documentation with quick start guide |
| `LICENSE` | Apache-2.0 license file |
| `NOTICES.md` | OSS license notices for dependencies (champ, turtlebot3) |
| `CONTRIBUTING.md` | Contribution guidelines and code style requirements |
| `CODE_OF_CONDUCT.md` | Community standards and code of conduct |
| `.minipupper.repos` | VCS repos file for external dependencies |
| `pupper_install.sh` | Installation script for Mini Pupper (Raspberry Pi) |
| `pc_install.sh` | Installation script for PC/simulation setup |
| `Dockerfile.tracking` | Docker configuration for tracking module |
| `entrypoint.sh` | Docker entrypoint script |
| `robot.service` | Systemd service for robot startup |
| `run.sh` | Runtime script for robot service |
| `show_ip.py` | Python script to display IP on LCD at boot |
| `.flake8` | Python linting configuration |
| `mmal_service_16.1.yaml` | MMAL service configuration (Raspberry Pi camera) |

---

## ROS 2 Packages

### 1. mini_pupper_bringup
**Type:** CMake Package (`ament_cmake`)  
**Description:** Main bringup package for launching Mini Pupper robot

**Key Files:**
- `launch/bringup.launch.py` - Main launch file that orchestrates robot bringup
- `launch/hardware_interface.launch.py` - Hardware interface launch (lidar, IMU, camera)
- `launch/champ_controllers.launch.py` - CHAMP controller launch
- `launch/ekf_localization.launch.py` - Extended Kalman Filter for localization
- `launch/rviz.launch.py` - RViz visualization launch
- `config/mini_pupper.yaml` - Configuration for Mini Pupper (sensors: lidar, imu, camera)
- `config/mini_pupper_2.yaml` - Configuration for Mini Pupper 2

**ROS Dependencies:**
- `champ_base` - Core CHAMP quadruped framework
- `launch`, `launch_ros` - Launch utilities
- `rviz2` - Visualization

---

### 2. mini_pupper_interfaces
**Type:** CMake Package (`ament_cmake`)  
**Description:** Custom ROS 2 message and service definitions

**Messages (.msg):**
| Message | Description |
|---------|-------------|
| `Command.msg` | Main robot command (velocity, height, orientation, events) |
| `FleetCommand.msg` | Fleet control command (heading, velocities) |
| `Tracking.msg` | Object tracking data (confidence, position, bounding area) |
| `TrackingArray.msg` | Array of tracking messages |
| `Matrix3x4.msg` | 3x4 matrix for leg positions |
| `LineDetectionResult.msg` | Line detection output |
| `AiLineRecognitionResult.msg` | AI-based line recognition result |

**Services (.srv):**
| Service | Description |
|---------|-------------|
| `DanceCommand.srv` | Execute dance movements |
| `PlayMusic.srv` | Play audio file |
| `StopMusic.srv` | Stop audio playback |

**Build Dependencies:**
- `rosidl_default_generators` - ROS IDL code generation
- `std_msgs` - Standard ROS messages

---

### 3. mini_pupper_driver
**Type:** Python Package (`ament_python`)  
**Description:** Hardware interface drivers for Mini Pupper sensors and actuators

**ROS Nodes (Entry Points):**
| Node | Script | Description |
|------|--------|-------------|
| `servo_interface` | `servo_interface.py` | Controls 12 servo motors via HardwareInterface |
| `display_interface` | `display_interface.py` | LCD display interface (ST7789) |
| `imu_interface` | `imu_interface.py` | IMU data publisher via ESP32 interface |
| `curvature_compensation` | `curvature_compensation.py` | Terrain curvature compensation |
| `nav_vel_scaler` | `nav_vel_scaler.py` | Navigation velocity scaling |

**Key Topics:**
- Subscribers: `joint_group_effort_controller/joint_trajectory` (JointTrajectory)
- Publishers: `imu/data` (Imu), `mini_pupper_lcd/image_raw` (Image)

**Dependencies:**
- `rclpy` - ROS 2 Python client library
- `sensor_msgs`, `trajectory_msgs` - ROS message types
- `cv_bridge` - OpenCV-ROS bridge
- `MangDang` - Mini Pupper BSP library

---

### 4. mini_pupper_description
**Type:** CMake Package (`ament_cmake`)  
**Description:** URDF models and robot description

**Contents:**
- `urdf/mini_pupper/` - URDF for Mini Pupper (original)
- `urdf/mini_pupper_2/` - URDF for Mini Pupper 2
- `meshes/` - 3D mesh files (.stl) for both robot variants
- `config/champ/` - CHAMP configuration files
- `config/ros_control/` - ROS Control configuration
- `rviz/` - RViz configuration files
- `src/stanford_joint_trajectory_publisher.cpp` - Joint trajectory publisher
- `src/stanford_state_publisher.cpp` - Robot state publisher

**Launch Files:**
- `mini_pupper_description.launch.py` - Load URDF and start state publisher
- `stanford_visualization.launch.py` - Stanford controller visualization

**Dependencies:**
- `robot_state_publisher`, `joint_state_publisher` - TF publishers
- `urdf`, `xacro` - URDF processing
- `tf2_ros`, `tf2_geometry_msgs`, `tf2_sensor_msgs` - TF transformations

---

### 5. stanford_controller
**Type:** Python Package (`ament_python`)  
**Description:** Stanford quadruped controller for gait generation and locomotion

**Core Modules:**
| Module | Description |
|--------|-------------|
| `stanford_controller_node.py` | Main controller node |
| `twist_to_command_node.py` | Convert Twist to Command messages |
| `gait_controller.py` | Gait pattern generation |
| `swing_controller.py` | Swing leg trajectory control |
| `stance_controller.py` | Stance leg control |
| `Kinematics.py` | Inverse kinematics for 4 legs |
| `Utilities.py` | Helper functions |
| `State.py` | Robot state definitions |
| `Config.py` | Controller configuration |

**ROS Nodes:**
| Node | Entry Point | Description |
|------|-------------|-------------|
| `stanford_controller_node` | `stanford_controller_node:main` | Main locomotion controller |
| `twist_to_command_node` | `twist_to_command_node:main` | Twist to Command converter |

**Key Topics:**
- Subscribers: `robot_command` (Command), `imu/data` (Imu)
- Publishers: `joint_group_effort_controller/joint_trajectory` (JointTrajectory), `state_log` (String)

**Dependencies:**
- `rclpy`, `sensor_msgs`, `trajectory_msgs`
- `mini_pupper_interfaces` - Custom messages
- `transforms3d`, `numpy` - Math libraries

---

### 6. mini_pupper_tracking
**Type:** Python Package (`ament_python`)  
**Description:** Computer vision-based person/object tracking using YOLO11

**ROS Nodes:**
| Node | Entry Point | Description |
|------|-------------|-------------|
| `main` | `main:main` | Main tracking node with Flask web interface |
| `movement_node` | `movement_node:main` | Movement controller for tracking |
| `camera_visualisation_node` | `camera_visualisation_node:main` | Camera visualization |
| `webcam_node` | `webcam_node:main` | Webcam driver node |

**Key Topics:**
- Publishers: `tracking_array` (TrackingArray)
- Subscribers: `/tracking_array` (TrackingArray), `imu/data_filtered_madgwick` (Imu)
- Publishes to: `/robot_command` (Command)

**Key Features:**
- YOLO11-based object detection (model: `models/yolo11n.onnx`)
- PID control for yaw and pitch tracking
- Flask web interface on port 5000
- Multi-object tracking with MOTPY

**Dependencies:**
- `rclpy`, `sensor_msgs`, `cv_bridge`, `geometry_msgs`, `visualization_msgs`
- `mini_pupper_interfaces` - Custom messages
- `tf_transformations` - Quaternion transformations
- `imu_filter_madgwick` - IMU orientation filter
- External: `opencv-python`, `onnxruntime`, `motpy`, `flask`

**Configuration:**
- `config/tracking_params.yaml` - Tracking parameters
- `config/movement_params.yaml` - Movement control parameters

---

### 7. mini_pupper_navigation
**Type:** CMake Package (`ament_cmake`)  
**Description:** Autonomous navigation using Nav2 stack

**Launch Files:**
- `navigation.launch.py` - Main navigation launch
- `navigation_smacplanner.launch.py` - Navigation with SMAC planner

**Configuration:**
- `param/mini_pupper.yaml` - Nav2 parameters
- `param/real_table.yaml` - Real-world navigation parameters
- `maps/map.pgm`, `map.yaml` - Pre-built map files
- `rviz/navigation.rviz` - RViz configuration

**Key Dependencies:**
- `navigation2`, `nav2_bringup` - Nav2 navigation stack
- `nav2_smac_planner` - SMAC path planner
- `nav2_regulated_pure_pursuit_controller` - Path following controller
- `nav2_velocity_smoother`, `nav2_smoother` - Velocity smoothing
- `cartographer_ros` - SLAM (via slam package)
- `imu_tools` - IMU filtering

---

### 8. mini_pupper_slam
**Type:** CMake Package (`ament_cmake`)  
**Description:** SLAM (Simultaneous Localization and Mapping) using Cartographer and SLAM Toolbox

**Launch Files:**
- `slam.launch.py` - Cartographer SLAM launch
- `slam_toolbox.launch.py` - SLAM Toolbox launch

**Configuration:**
- `config/slam.lua` - Cartographer configuration
- `config/real_table.yaml` - Real-world SLAM parameters
- `rviz/slam.rviz` - RViz configuration for SLAM

**Dependencies:**
- `cartographer_ros` - Google's Cartographer SLAM
- `slam_toolbox` - ROS 2 SLAM toolbox

---

### 9. mini_pupper_simulation
**Type:** CMake Package (`ament_cmake`)  
**Description:** Gazebo simulation environment

**Launch Files:**
- `main.launch.py` - Main simulation launch
- `gazebo.launch.py` - Gazebo world launch
- `ros2_controller.launch.py` - ROS 2 control launch

**Worlds:**
- `worlds/empty.world` - Empty world
- `worlds/mini_pupper_home.world` - Home environment

**Configuration:**
- `config/gazebo_params.yaml` - Gazebo parameters

**Dependencies:**
- `gazebo_ros`, `gazebo_ros_pkgs` - Gazebo ROS integration
- `gazebo_plugins` - Gazebo plugins
- `ros2_control`, `ros2_controllers`, `gazebo_ros2_control` - ROS 2 control

---

### 10. mini_pupper_dance
**Type:** Python Package (`ament_python`)  
**Description:** Choreographed dance sequences with audio synchronization

**ROS Nodes:**
| Node | Entry Point | Description |
|------|-------------|-------------|
| `service` | `dance_server:main` | Dance command service server |
| `client` | `dance_client:main` | Dance command client |
| `pose_controller` | `pose_controller:main` | Pose control node |
| `mini_pupper_dance` | `new_dance.mini_pupper_dance:main` | New dance system |

**Key Modules:**
- `dance_server.py` - ROS service for dance commands
- `dance_client.py` - Client for sending dance commands
- `episode.py` - Dance episode management
- `pose_controller.py` - Pose control during dancing
- `math_operations.py` - Quaternion math utilities

**Services:**
- `dance_command` (DanceCommand) - Execute dance movements

**Topics:**
- Publishers: `cmd_vel` (Twist), `reference_body_pose` (Pose)

**Dependencies:**
- `rclpy`, `geometry_msgs`
- `mini_pupper_interfaces` - Custom services

---

### 11. mini_pupper_music
**Type:** Python Package (`ament_python`)  
**Description:** Audio playback service for music/sounds

**ROS Nodes:**
| Node | Entry Point | Description |
|------|-------------|-------------|
| `music_service` | `music_server:main` - not in setup.py, referenced in launch | Music playback service |

**Services:**
- `play_music` (PlayMusic) - Play audio file
- `stop_music` (StopMusic) - Stop playback

**Audio Files:**
- `audio/robot1.mp3`, `robot1.wav` - Sample audio files

**Dependencies:**
- `std_srvs` - Standard services

---

### 12. mini_pupper_recognition
**Type:** Python Package (`ament_python`)  
**Description:** Computer vision for line detection and AI-based recognition

**Launch Files:**
- `recognition.launch.py` - Main recognition launch
- `cloud_line_demo.launch.py` - Cloud-based line detection demo

**Key Modules:**
- `line_detection.py` - Line detection algorithms
- `line_detection_node.py` - ROS node for line detection
- `ai_line_recognition.py` - AI-based line recognition
- `ai_line_recognition_node.py` - ROS node for AI recognition

**Topics:**
- Publishers: `line_detection_result` (LineDetectionResult), `ai_line_recognition_result` (AiLineRecognitionResult)

**Dependencies:**
- `rclpy`, `std_msgs`, `sensor_msgs`, `cv_bridge`

---

### 13. mini_pupper_fleet
**Type:** CMake Package (`ament_cmake`)  
**Description:** Multi-robot fleet management and coordination

**ROS Nodes (C++):**
| Node | Source File | Description |
|------|-------------|-------------|
| `fleet_controller_node` | `fleet_controller_node.cpp` | Fleet command controller |
| `imu_ekf_node` | `imu_ekf_node.cpp` | IMU Extended Kalman Filter |
| `robot_behaviour_node` | `robot_behaviour_node.cpp` | Robot behavior management |

**Key Topics:**
- Subscribers: `/cmd_vel` (Twist)
- Publishers: `/fleet_command` (FleetCommand)

**Dependencies:**
- `rclcpp` - ROS 2 C++ client library
- `sensor_msgs`, `geometry_msgs`
- `tf2` - Transform library
- `mini_pupper_interfaces` - Custom messages
- `eigen` - Linear algebra library

---

## External Dependencies (from .minipupper.repos)

| Repository | URL | Branch | Description |
|------------|-----|--------|-------------|
| `champ/champ` | https://github.com/mangdangroboticsclub/champ.git | ros2 | CHAMP quadruped framework |
| `champ/champ_teleop` | https://github.com/chvmp/champ_teleop.git | ros2 | Teleoperation for CHAMP |
| `ldlidar_stl_ros` | https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2.git | master | LD-LiDAR driver |

---

## ROS 2 System Architecture

### Core Control Flow
```
cmd_vel (Twist)
    ↓
twist_to_command_node → robot_command (Command)
    ↓
stanford_controller_node → joint_trajectory (JointTrajectory)
    ↓
servo_interface → HardwareInterface → Motors
```

### Sensor Flow
```
IMU:    imu_interface → imu/data (Imu) → ekf_localization → imu/data_filtered_madgwick
Lidar:  ldlidar → /scan → slam/navigation
Camera: v4l2_camera → /image_raw → tracking/recognition
Display: /mini_pupper_lcd/image_raw → display_interface → LCD
```

### Navigation Flow
```
/scan + imu/data → cartographer/slam_toolbox → /map
/map + /scan + imu/data → nav2 → /cmd_vel
```

### Tracking Flow
```
/image_raw → TrackingNode (YOLO11) → /tracking_array
/tracking_array → MovementNode → /robot_command
/imu/data_filtered_madgwick → MovementNode (yaw/pitch control)
```

---

## Configuration Files

### Sensor Configuration (mini_pupper_bringup/config/)
```yaml
sensors:
  lidar: true/false    # Enable LD-LiDAR
  imu: true/false      # Enable IMU
  camera: true/false   # Enable Raspberry Pi Camera
ports: 
  lidar: '/dev/ttyUSB0'  # or '/dev/ttyAMA1'
```

### Environment Variables
```bash
export ROS_DOMAIN_ID=42           # ROS 2 domain for multi-robot
export ROBOT_MODEL=mini_pupper_2  # or mini_pupper
```

---

## Installation Scripts

### pupper_install.sh
- Runs on Raspberry Pi (Ubuntu 22.04)
- Installs ROS 2 Humble
- Clones and builds workspace
- Sets up systemd service for auto-start
- Disables heavy packages (gazebo, cartographer) on Pi

### pc_install.sh
- Runs on PC (Ubuntu 22.04)
- Installs ROS 2 Humble with full desktop
- Includes simulation and navigation packages
- Installs RViz2 and visualization tools

---

## Docker Support

### Dockerfile.tracking
Base image: `ros:humble-ros-base`

Includes:
- ROS 2 Humble base
- Tracking dependencies (OpenCV, ONNX Runtime, MOTPY, Flask)
- Mini Pupper packages: tracking, interfaces, stanford_controller

Exposed port: 5000 (Flask web interface)

---

## CI/CD

### GitHub Actions (.github/workflows/)

**industrial_ci.yml:**
- Triggers on push/PR (ignores .md files)
- Uses industrial_ci for ROS 2 Humble
- Tests with repos file: `.minipupper.repos`

**lint.yml:**
- Code style checking
- Runs ament_flake8, ament_pep257 for Python

---

## Code Style Guidelines

### Python
- `ament_flake8` - PEP 8 compliance
- `ament_pep257` - Docstring conventions

### C++
- `ament_clang_format` - Code formatting
- `ament_uncrustify` - Style enforcement
- `ament_cpplint` - Google C++ style

### Testing
```bash
colcon test --packages-select-regex "mini_pupper*"
colcon test-result --verbose
```

---

## Hardware Requirements

### Mini Pupper (Original)
- Raspberry Pi 4
- 12x PWM servos
- LD-LiDAR (optional)
- MPU6050/ESP32 IMU (optional)
- Raspberry Pi Camera (optional)
- ST7789 LCD display

### Mini Pupper 2
- Raspberry Pi 4
- 12x PWM servos
- ESP32 for IMU and servo control
- LD-LiDAR (optional)
- Raspberry Pi Camera (optional)
- ST7789 LCD display

---

## Communication Interfaces

### I2C
- LCD Display (ST7789)
- ESP32 (on Mini Pupper 2)

### Serial
- LiDAR (/dev/ttyUSB0 or /dev/ttyAMA1)

### SPI
- Servo controller (PCA9685)

### CSI
- Raspberry Pi Camera

---

## Quick Launch Commands

```bash
# Robot bringup (on Mini Pupper)
ros2 launch mini_pupper_bringup bringup.launch.py

# Teleoperation
ros2 run teleop_twist_keyboard teleop_twist_keyboard
ros2 launch teleop_twist_joy teleop-launch.py

# SLAM
ros2 launch mini_pupper_slam slam_toolbox.launch.py

# Navigation
ros2 launch mini_pupper_navigation navigation.launch.py map:=~/map.yaml

# Tracking
ros2 launch mini_pupper_tracking tracking.launch.py

# Simulation
ros2 launch mini_pupper_simulation main.launch.py

# Dance
ros2 launch mini_pupper_dance dance.launch.py
```

---

## License Summary

- **mini_pupper_ros:** Apache-2.0
- **champ:** BSD-3-Clause and Apache-2.0
- **turtlebot3 (reference):** Apache-2.0

---

*Document generated on 2026-02-11*
