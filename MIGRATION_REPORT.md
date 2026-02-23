# Mini Pupper ROS 2: Humble to Jazzy Migration Report

## 1. Introduction

This document describes the complete migration of the **Mini Pupper ROS 2** robotics platform from **ROS 2 Humble** (Ubuntu 22.04) to **ROS 2 Jazzy** (Ubuntu 24.04). It covers every subsystem that was modified, explains the rationale behind each change, and documents the challenges encountered during the process.

Two repositories were migrated:

| Repository | Purpose | Branch |
|---|---|---|
| [MushfiqueTM/mini_pupper_ros](https://github.com/MushfiqueTM/mini_pupper_ros) | ROS 2 packages (simulation, navigation, drivers, etc.) | `ros2-jazzy` |
| [MushfiqueTM/mini_pupper_bsp](https://github.com/MushfiqueTM/mini_pupper_bsp) | Board Support Package (hardware drivers, system config) | `main` |

---

## 2. Platform Changes Overview

| Component | Humble (Before) | Jazzy (After) |
|---|---|---|
| Ubuntu | 22.04 LTS (Jammy) | 24.04 LTS (Noble) |
| ROS 2 | Humble Hawksbill | Jazzy Jalisco |
| Python | 3.10 | 3.12 |
| Gazebo | Classic 11 (`gazebo_ros`) | Harmonic 8 (`ros_gz_sim`) |
| ros2_control plugin | `gazebo_ros2_control` | `gz_ros2_control` |
| Nav2 | Humble release | Jazzy release (major API changes) |
| CMake minimum | 3.5 | 3.16 |
| pip behavior | Unrestricted system installs | PEP 668 externally-managed environment |
| APT sources format | `/etc/apt/sources.list` | DEB822 (`/etc/apt/sources.list.d/ubuntu.sources`) |

---

## 3. Simulation: Gazebo Classic to Gazebo Harmonic

This was the largest single area of change. Gazebo Classic (version 11) is not available on Ubuntu 24.04. ROS 2 Jazzy pairs with **Gazebo Harmonic** (the modern Gazebo, formerly "Ignition Gazebo"), which is an entirely different codebase.

### 3.1 Package Dependencies

All `package.xml` and `CMakeLists.txt` files were updated:

| Humble Dependency | Jazzy Replacement |
|---|---|
| `gazebo_ros` | `ros_gz_sim` |
| `gazebo_ros_pkgs` | `ros_gz` |
| `gazebo_ros2_control` | `gz_ros2_control` |
| `gazebo_plugins` | *(removed — Harmonic uses built-in system plugins)* |

### 3.2 World Files

Gazebo Classic `.world` files (XML/SDF 1.6) were replaced with Gazebo Harmonic `.sdf` files (SDF 1.9+). Two new world files were created:

- `mini_pupper_home.sdf` — A room environment with walls and obstacles for navigation testing.
- `empty.sdf` — A minimal world for basic testing.

The old `.world` files were deleted as they are incompatible with Harmonic.

### 3.3 Launch Files

The simulation launch system was rewritten:

| Aspect | Humble | Jazzy |
|---|---|---|
| Gazebo launcher | `gazebo_ros` / `gazebo.launch.py` | `ros_gz_sim` / `gz_sim.launch.py` |
| Entity spawner | `gazebo_ros` / `spawn_entity.py` | `ros_gz_sim` / `create` |
| Sensor data bridge | Automatic via Gazebo Classic plugins | Explicit `ros_gz_bridge` / `parameter_bridge` node |

A `parameter_bridge` node was added to `main.launch.py` to bridge sensor data from Gazebo Harmonic topics to ROS 2 topics:

| ROS 2 Topic | Gazebo Topic | Data Type |
|---|---|---|
| `/clock` | `/clock` | `Clock` |
| `/scan` | `/lidar/scan` | `LaserScan` |
| `/imu/data` | `/imu/data` | `Imu` |

### 3.4 URDF Sensor Plugins

The URDF/Xacro files contained Gazebo Classic `<plugin>` blocks for sensors (LiDAR, camera, IMU). These were replaced with Gazebo Harmonic-native `<sensor>` elements:

**LiDAR** — Replaced `libgazebo_ros_ray_sensor.so` plugin with a native `<sensor type="gpu_lidar">` element.

**Depth Camera** — Replaced `libgazebo_ros_openni_kinect.so` plugin with a native `<sensor type="depth_camera">` element.

**IMU** — Replaced `libgazebo_ros_imu_sensor.so` plugin with a native `<sensor type="imu">` element.

### 3.5 ros2_control Hardware Interface

The `ros2_control` `<plugin>` tag in the URDF was updated:

| Humble | Jazzy |
|---|---|
| `gz_ros2_control/GZSimSystem` | `gz_ros2_control/GazeboSimSystem` |

This reflects the renamed hardware interface class in the Jazzy release of `gz_ros2_control`.

---

## 4. Navigation2 (Nav2) Changes

Nav2 underwent significant API changes between Humble and Jazzy. Multiple configuration and naming issues had to be resolved.

### 4.1 bt_navigator Configuration

The `bt_navigator` node in Humble used a `plugin_lib_names` list referencing behavior tree plugin shared libraries. In Jazzy, this was replaced with a `navigators` parameter:

**Humble:**
```yaml
bt_navigator:
  ros__parameters:
    plugin_lib_names:
      - nav2_compute_path_to_pose_action_bt_node
      - nav2_is_stuck_condition_bt_node
      # ... many more
```

**Jazzy:**
```yaml
bt_navigator:
  ros__parameters:
    navigators: ['navigate_to_pose', 'navigate_through_poses']
    navigate_to_pose:
      plugin: 'nav2_bt_navigator::NavigateToPoseNavigator'
    navigate_through_poses:
      plugin: 'nav2_bt_navigator::NavigateThroughPosesNavigator'
```

The `nav2_is_stuck_condition_bt_node` plugin was removed entirely in Jazzy, which caused the `bt_navigator` to fail configuration when the old format was used.

### 4.2 Plugin Name Format

All Nav2 plugin names were changed from the Humble slash format to the Jazzy double-colon format:

| Humble Format | Jazzy Format |
|---|---|
| `nav2_navfn_planner/NavfnPlanner` | `nav2_navfn_planner::NavfnPlanner` |
| `nav2_smac_planner/SmacPlanner2D` | `nav2_smac_planner::SmacPlanner2D` |
| `nav2_behaviors/Spin` | `nav2_behaviors::Spin` |
| `nav2_behaviors/BackUp` | `nav2_behaviors::BackUp` |
| `nav2_behaviors/Wait` | `nav2_behaviors::Wait` |
| `nav2_behaviors/DriveOnHeading` | `nav2_behaviors::DriveOnHeading` |

Using the old slash format causes a fatal `pluginlib` error on Jazzy since the class loader cannot resolve the plugin name.

### 4.3 recoveries_server to behavior_server

The `recoveries_server` node was renamed to `behavior_server` in Nav2 Jazzy. Parameter files and launch file references were updated accordingly.

### 4.4 New Required Nodes in Jazzy

Nav2 Jazzy introduced several new nodes that must be configured in the parameter YAML files for the navigation stack to become fully active:

| New Node | Purpose |
|---|---|
| `velocity_smoother` | Smoothes velocity commands sent to the robot |
| `smoother_server` | Provides path smoothing services |
| `route_server` | Route planning (new in Jazzy) |
| `collision_monitor` | Real-time collision avoidance |
| `docking_server` | Autonomous docking support |

The `collision_monitor` was the most critical — without its `observation_sources` parameter configured, the entire Nav2 stack would fail to activate.

### 4.5 Deprecated Parameter Blocks Removed

Nine deprecated parameter blocks were removed from `real_table.yaml`:

- `*_rclcpp_node` sections (removed in Jazzy — each node manages its own executor)
- `*_client` sections (internal implementation details no longer exposed)
- Groot v1 ZMQ monitoring parameters (replaced by Groot v2)

### 4.6 Costmap use_sim_time Fix

Both `local_costmap` and `global_costmap` in `mini_pupper.yaml` had `use_sim_time: False` hardcoded. This was changed to `use_sim_time: True` to match the simulation parameter, ensuring costmaps use Gazebo's clock rather than wall time.

---

## 5. Build System Changes

### 5.1 CMakeLists.txt

All seven `CMakeLists.txt` files were updated:
- `cmake_minimum_required` bumped from 3.5 to 3.16 (required by Jazzy).
- Removed invalid `find_package()` calls for runtime-only dependencies (`ros_gz_sim`, `ros2_control`, `ros2_controllers`). These are runtime dependencies declared in `package.xml`, not build-time CMake packages.

### 5.2 package.xml

- Replaced all Gazebo Classic dependencies with their Harmonic equivalents.
- Removed invalid `<author>` tags that violated ROS 2 `package_format3` schema (caught by `xmllint` in CI).
- Corrected dependency categories (`<build_depend>` vs `<exec_depend>` vs `<test_depend>`).

### 5.3 setup.py (Python packages)

- Removed `install_requires=['setuptools']` from all six `setup.py` files — `setuptools` is a build dependency, not an install dependency. Including it caused pip resolver conflicts on Python 3.12.
- Removed redundant `package_dir` mapping from `mini_pupper_dance/setup.py` that caused a `RuntimeError` on Python 3.12's stricter `colcon` build validation.

---

## 6. Python 3.12 Compatibility

Ubuntu 24.04 ships Python 3.12, which introduced several breaking changes:

### 6.1 distutils Removal

Python 3.12 removed the `distutils` module. Any `setup.py` file using `from distutils.core import setup` must be changed to `from setuptools import setup`. The mini_pupper packages already used setuptools, but this was verified across all files.

### 6.2 rclpy.shutdown() Handling

Multiple Python nodes were missing proper `rclpy.shutdown()` calls, or calling it unconditionally after it had already been called (e.g., on Ctrl+C). This caused `RCLError: failed to shutdown: rcl_shutdown already called` errors on exit.

**Fix applied across 6+ files:** Added `try/except/finally` blocks with a `if rclpy.ok():` guard:

```python
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
```

### 6.3 flake8 Compliance

CI runs `ament_flake8` as part of the test suite. Over 150 flake8 violations were fixed across 36+ Python files in 11 packages, including:

- Import ordering (isort / I100)
- String quoting consistency (Q000)
- Trailing commas (C812)
- Line length (E501)
- Whitespace and formatting (W291, W293, E302, etc.)
- f-string vs format() usage (C417)

---

## 7. CHAMP Quadruped Framework

The [CHAMP](https://github.com/chvmp/champ) framework provides the quadruped locomotion controller. It was not forked or modified — instead, incompatible packages were excluded.

### 7.1 Problem

The champ repository contains 8 packages. Three are needed (`champ`, `champ_base`, `champ_msgs`). Five others depend on Gazebo Classic packages that don't exist on Jazzy:

- `champ_gazebo` (depends on `gazebo_ros2_control`, `gazebo_plugins`)
- `champ_description` (depends on `velodyne_gazebo_plugins`)
- `champ_bringup`, `champ_navigation`, `champ_config`

### 7.2 Solution

`COLCON_IGNORE` marker files are placed in the five incompatible package directories. This tells `colcon` to skip them entirely. The three required packages build on Jazzy with zero code changes.

The CI workflow (`industrial_ci.yml`) handles this automatically via `BEFORE_BUILD_UPSTREAM_WORKSPACE` hooks that:
1. Create `COLCON_IGNORE` files in the broken packages.
2. Add the broken package names to `rosdep --skip-keys`.

### 7.3 libchamp Submodule

`champ_base` depends on header files from the `libchamp` library, which is a git submodule at `champ/include/champ`. After cloning, `git submodule update --init --recursive` must be run to fetch these headers. Without this step, `champ_base` fails to compile with `fatal error: champ/odometry/odometry.h: No such file or directory`.

---

## 8. Board Support Package (BSP) Migration

The BSP provides hardware-level drivers for the Mini Pupper's servos, IMU (via ESP32), LCD display, audio, fuel gauge, and GPIO configuration. The original BSP ([mangdangroboticsclub/mini_pupper_2_bsp](https://github.com/mangdangroboticsclub/mini_pupper_2_bsp)) only supports Ubuntu 22.04.

### 8.1 Changes Made

| File | Change | Reason |
|---|---|---|
| `install.sh` | Added `--break-system-packages` flag to all `pip install` commands on Noble | PEP 668 enforcement on Ubuntu 24.04 |
| `install.sh` | Guard `sed` on `/etc/apt/sources.list` | Ubuntu 24.04 uses DEB822 format; the traditional file may be empty |
| `install.sh` | `setuptools==58.2.0` → latest `setuptools` | Pinned version is incompatible with Python 3.12 |
| `install.sh` | Guard `/etc/libao.conf` edit | File may not exist on minimal installs |
| `install.sh` | Idempotent bashrc alias | Prevents duplicate entries on re-run |
| `setup.sh` | Accept `noble` codename | Was hardcoded to reject anything other than `jammy` |
| `RPiCamera/install.sh` | Skip legacy camera stack on Noble | Ubuntu 24.04 uses `libcamera` natively; `start_x=1` and `gpu_mem=128` are not needed |
| `RPiCamera/install.sh` | Idempotent `config.txt` edits | Prevents duplicate lines on re-run |
| `Python_Module/setup.cfg` | `universal = 0` | Python 2 wheel support is unnecessary |
| `README.md` | Document dual 22.04/24.04 support | Users need to know which Ubuntu version to use |

### 8.2 Unchanged Components

The following BSP components required no changes because they operate at the kernel/hardware level and are version-agnostic:

- **DKMS audio driver** (`rpi-i2s-audio`) — Builds against installed kernel headers.
- **FuelGauge** — Precompiled binary + systemd service.
- **ESP32 proxy** — C program compiled against standard libc.
- **IO_Configuration** — Copies a static `config.txt` to `/boot/firmware/`.
- **System** — Copies systemd service files and sudoers.

---

## 9. CI/CD Pipeline

### 9.1 GitHub Actions Workflow

The `industrial_ci.yml` workflow was updated to:

- Target `ROS_DISTRO: jazzy` and `ROS_REPO: main`.
- Add all unavailable Gazebo Classic packages to `ROSDEP_SKIP_KEYS`.
- Add `COLCON_IGNORE` files to incompatible champ packages before build.
- Remove `package.xml` from champ packages that would cause rosdep resolution failures.

### 9.2 Challenges

The CI pipeline exposed several issues not visible in local builds:

1. **rosdep resolution failures** — Packages like `velodyne_gazebo_plugins`, `gazebo_ros2_control`, and `gazebo_plugins` have no rosdep keys for Jazzy. Each had to be added to `--skip-keys`.

2. **package.xml schema violations** — Incorrectly placed `<author>` tags passed local builds but failed `xmllint` validation in CI.

3. **flake8 strictness** — CI runs `ament_flake8` with plugins (isort, flake8-quotes, flake8-commas) that are stricter than default flake8. This required fixing 150+ style violations.

---

## 10. Launch File Fixes

### 10.1 PathJoinSubstitution

Several launch files had incorrect `PathJoinSubstitution` usage where raw strings were used instead of proper substitution objects. These were corrected to use `FindPackageShare` and `LaunchConfiguration` properly.

### 10.2 Cartographer Argument Passing

`slam.launch.py` had an incorrect method of passing arguments to the Cartographer node. The argument format was updated to be compatible with Jazzy's launch system.

### 10.3 entrypoint.sh

The Docker entrypoint script still sourced `/opt/ros/humble/setup.bash`. This was changed to `/opt/ros/jazzy/setup.bash`.

---

## 11. Installation Script Updates

| Script | Changes |
|---|---|
| `pc_install.sh` | `ros-jazzy-gazebo-ros2-control` → `ros-jazzy-gz-ros2-control` (package was renamed) |
| `pupper_install.sh` | Same package name correction |
| `entrypoint.sh` | `humble` → `jazzy` in ROS setup source |

---

## 12. Summary of All Modified Files

### mini_pupper_ros (61+ files modified)

**Build system:** 7 `CMakeLists.txt`, 13 `package.xml`, 6 `setup.py`

**Simulation:** 2 new world files (`.sdf`), 2 deleted world files (`.world`), 2 launch files rewritten

**URDF/Xacro:** 3 URDF files (sensor plugins, ros2_control plugin name)

**Navigation:** 2 parameter YAML files (bt_navigator, plugin names, new nodes, deprecated blocks)

**Python nodes:** 6+ files (rclpy.shutdown handling)

**Code style:** 36+ Python files (flake8 compliance)

**CI/CD:** 1 workflow file

**Scripts:** 3 shell scripts (pc_install, pupper_install, entrypoint)

**Documentation:** README.md rewritten, migration guides created

### mini_pupper_bsp (5 files modified)

`install.sh`, `setup.sh`, `RPiCamera/install.sh`, `Python_Module/setup.cfg`, `README.md`

---

## 13. Challenges and Lessons Learned

### 13.1 Gazebo Harmonic Sensor Topic Discovery

Gazebo Harmonic publishes sensor data on Gazebo-internal transport topics, not directly on ROS 2 topics. An explicit `ros_gz_bridge` node must be configured to relay each sensor topic. The Gazebo topic names depend on the model name and sensor name in the SDF/URDF, making them non-obvious. The `gz topic -l` command is essential for debugging.

### 13.2 Nav2 Jazzy Breaking Changes Were Undocumented

Several Nav2 changes (plugin name format, removed `plugin_lib_names`, new required nodes like `collision_monitor`) were not prominently documented in Nav2's migration guide. They were discovered through runtime error analysis — each failing node had to be diagnosed individually by reading the error logs and consulting the Nav2 Jazzy source code.

### 13.3 PEP 668 on Ubuntu 24.04

Ubuntu 24.04 marks the system Python as "externally managed" per PEP 668. Every `pip install` without `--break-system-packages` fails with `error: externally-managed-environment`. This affected both the BSP installer and any development workflow that installs Python packages system-wide.

### 13.4 CHAMP Is Not Maintained for Jazzy

The CHAMP framework has no official Jazzy branch. However, the core locomotion packages (`champ`, `champ_base`, `champ_msgs`) compile without modification on Jazzy because they only depend on standard `rclcpp` and message packages. The solution of excluding incompatible packages via `COLCON_IGNORE` is clean and requires no upstream changes.

### 13.5 Iterative CI Debugging

The CI pipeline revealed issues in waves — fixing one rosdep failure exposed the next, fixing schema errors exposed flake8 failures, etc. A total of 8+ CI iteration cycles were needed before the pipeline passed cleanly.

---

## 14. Repositories

| Repository | URL |
|---|---|
| Mini Pupper ROS (Jazzy) | https://github.com/MushfiqueTM/mini_pupper_ros (branch: `ros2-jazzy`) |
| Mini Pupper BSP (24.04) | https://github.com/MushfiqueTM/mini_pupper_bsp (branch: `main`) |
| Original ROS (Humble) | https://github.com/mangdangroboticsclub/mini_pupper_ros (branch: `ros2`) |
| Original BSP (22.04) | https://github.com/mangdangroboticsclub/mini_pupper_2_bsp (branch: `main`) |

---

*Last updated: February 2026*
