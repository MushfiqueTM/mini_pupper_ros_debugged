[![ROS2 VERSION](https://img.shields.io/badge/ROS-ROS%202%20Jazzy-brightgreen)](http://docs.ros.org/en/jazzy/index.html)
&nbsp;
[![Ubuntu VERSION](https://img.shields.io/badge/Ubuntu-24.04-green)](https://ubuntu.com/)
&nbsp;
[![LICENSE](https://img.shields.io/badge/license-Apache--2.0-informational)](https://github.com/mangdangroboticsclub/mini_pupper_ros/blob/ros2/LICENSE)
&nbsp;
[![Build Status](https://github.com/mangdangroboticsclub/mini_pupper_ros/actions/workflows/industrial_ci.yml/badge.svg)](https://github.com/mangdangroboticsclub/mini_pupper_ros/actions/workflows/industrial_ci.yml)
&nbsp;
[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://minipupperdocs.readthedocs.io/en/latest/)
&nbsp;
[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FLeggedRobot)](https://twitter.com/LeggedRobot)

# Mini Pupper ROS 2 Jazzy

> **⚠️ MIGRATION NOTICE:** This branch has been migrated from ROS 2 Humble to ROS 2 Jazzy. Ubuntu 24.04 is now required.

<p align="left">
  <img src="imgs/mini_pupper_2.jpg" alt="Mini Pupper 2" width="480"/>
</p>

A comprehensive ROS 2 robotics platform for autonomous navigation, computer vision, and multi-robot coordination. Built for research, education, and development on Ubuntu 24.04 with ROS 2 Jazzy.

## Key Capabilities

<p align="left">
  <img src="imgs/mini_pupper_navigation_480_12.gif" alt="Navigation Demo" width="480"/>
</p>

### SLAM & Autonomous Navigation
Real-time mapping and path planning with ROS 2 Nav2 stack integration.  
**[Documentation](mini_pupper_navigation/README.md)**

### Computer Vision Tracking
YOLO11-powered person detection and following with multi-object tracking.  
**[Documentation](mini_pupper_tracking/README.md)**

### Multi-Robot Fleet Management
Centralized command and control for coordinated multi-robot operations.  
**[Documentation](mini_pupper_fleet/README.md)**

### Choreographed Movement System
Programmable dance sequences with audio synchronization capabilities.  
**[Documentation](mini_pupper_dance/README.md)**

## Quick Start

### Prerequisites

- **OS:** Ubuntu 24.04 LTS (Noble Numbat) - REQUIRED
- **ROS 2:** Jazzy Jalisco
- **Hardware:** Mini Pupper or Mini Pupper 2

> **Note:** If you need ROS 2 Humble support (Ubuntu 22.04), please use the `ros2-humble` branch.

### Pre-built Images
Flash the ready-to-use image containing Ubuntu 24.04, ROS 2 Jazzy, and all Mini Pupper packages:
- **Mini Pupper 2**: [Jazzy pre-built image - Coming Soon]
- **Mini Pupper**: [Jazzy pre-built image - Coming Soon]

### Test Basic Movement
```bash
# Terminal 1 (SSH to robot)
source ~/ros2_ws/install/setup.bash
ros2 launch mini_pupper_bringup bringup.launch.py
```
```bash

# Terminal 2 (PC or robot)
source ~/ros2_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Note**: Refer to the [Detailed Setup Guide](docs/detailed-setup-guide.md) for network configuration, PC setup, troubleshooting, and full BSP manual installation as an alternative to the pre-built image.

For comprehensive documentation, visit our [online guide](https://minipupperdocs.readthedocs.io/en/latest/).

## Migration from Humble to Jazzy

See [MIGRATION_JAZZY.md](MIGRATION_JAZZY.md) for detailed migration instructions if you're upgrading from a Humble-based system.

## Contributing
Contributions are welcome.
Whether it's reporting a bug, suggesting a new feature, or submitting a pull request, we'd love your help in improving the **Mini Pupper ROS 2 project**.  

- Read our [CONTRIBUTING.md](CONTRIBUTING.md) guide to get started.  
- Explore or work on [open issues](https://github.com/mangdangroboticsclub/mini_pupper_ros/issues).  

## License

```
Copyright 2022-2025 MangDang

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
