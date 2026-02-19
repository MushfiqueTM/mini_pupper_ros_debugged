#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2022-2025 MangDang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
LD06/LD19 LiDAR Launch File for ROS 2 Jazzy.

This launch file supports:
- LD06 LiDAR (default)
- LD19 LiDAR (use lidar_model:=LD19)

And TWO lidar driver options:

OPTION 1: Old driver (ldlidar_stl_ros2) - Legacy, may not work on Jazzy
  Package: ldlidar_stl_ros2
  Repo: https://github.com/ldrobotSensorTeam/ldlidar_stl_ros2.git

OPTION 2: NEW driver (ldrobot-lidar-ros2) - RECOMMENDED for Jazzy
  Package: ldlidar_node
  Repo: https://github.com/Myzhar/ldrobot-lidar-ros2.git (devel branch)
  Features: Lifecycle architecture, Nav2 integration, supports LD06/LD19

Default: Uses new driver (Option 2) with LD06 model for Jazzy compatibility

Usage:
  ros2 launch mini_pupper_driver lidar_ld06.launch.py
  ros2 launch mini_pupper_driver lidar_ld06.launch.py lidar_model:=LD19
  ros2 launch mini_pupper_driver lidar_ld06.launch.py lidar_port:=/dev/ttyUSB1
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    lidar_port = LaunchConfiguration("lidar_port")
    lidar_model = LaunchConfiguration("lidar_model")
    use_legacy_driver = LaunchConfiguration("use_legacy_driver")

    lidar_port_launch_arg = DeclareLaunchArgument(
        name='lidar_port',
        default_value='/dev/ttyUSB0',
        description='The serial port for the lidar sensor'
    )

    lidar_model_launch_arg = DeclareLaunchArgument(
        name='lidar_model',
        default_value='LD06',
        description='LiDAR model: LD06 or LD19',
        choices=['LD06', 'LD19']
    )

    use_legacy_launch_arg = DeclareLaunchArgument(
        name='use_legacy_driver',
        default_value='false',
        description='Use legacy ldlidar_stl_ros2 driver instead of new ldlidar_node'
    )

    # OPTION 1: Legacy driver (old) - Use with use_legacy_driver:=true
    # Note: Legacy driver may not support LD19 properly
    legacy_lidar_node = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        name='LD06',
        output='screen',
        condition=IfCondition(use_legacy_driver),
        parameters=[
            {'product_name': 'LDLiDAR_LD06'},  # Legacy driver only supports LD06
            {'topic_name': 'scan'},
            {'frame_id': 'lidar_link'},
            {'port_name': lidar_port},
            {'port_baudrate': 230400},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
            {'angle_crop_min': 135.0},
            {'angle_crop_max': 225.0}
        ],
    )

    # OPTION 2: New driver (recommended) - Default for Jazzy
    # Uses lifecycle manager for proper state management
    # Supports both LD06 and LD19 models
    # Note: The devel branch supports both Humble and Jazzy
    new_lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('ldlidar_node'),
            '/launch/ldlidar_with_mgr.launch.py'
        ]),
        launch_arguments={
            'serial_port': lidar_port,
            'lidar_model': lidar_model,  # Supports LD06 or LD19
        }.items(),
        condition=UnlessCondition(use_legacy_driver),
    )

    return LaunchDescription([
        lidar_port_launch_arg,
        lidar_model_launch_arg,
        use_legacy_launch_arg,
        LogInfo(msg=['Using lidar port: ', lidar_port]),
        LogInfo(msg=['Using lidar model: ', lidar_model]),
        LogInfo(msg=['Using legacy driver: ', use_legacy_driver]),

        # Launch appropriate driver based on use_legacy_driver parameter
        legacy_lidar_node,
        new_lidar_launch,
    ])
