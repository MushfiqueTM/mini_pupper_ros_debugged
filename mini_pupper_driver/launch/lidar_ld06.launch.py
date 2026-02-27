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
LD06/LD19 LiDAR Launch File for Mini Pupper (ROS 2 Jazzy).

Self-contained launch that uses the ldrobot-lidar-ros2 composable component
with Mini Pupper's own config (mini_pupper_driver/config/ldlidar.yaml).
This avoids depending on upstream default settings that don't match
Mini Pupper's hardware (LD06 model, lidar_link frame, /dev/ldlidar port).
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import LogInfo
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    lidar_config_path = os.path.join(
        get_package_share_directory('mini_pupper_driver'),
        'config',
        'ldlidar.yaml',
    )

    ldlidar_container = ComposableNodeContainer(
        name='ldlidar_container',
        namespace='/',
        package='rclcpp_components',
        executable='component_container_isolated',
        composable_node_descriptions=[
            ComposableNode(
                package='ldlidar_component',
                plugin='ldlidar::LdLidarComponent',
                name='ldlidar_node',
                namespace='/',
                parameters=[lidar_config_path],
            ),
        ],
        output='screen',
    )

    ldlidar_lifecycle_mgr = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['ldlidar_node'],
            'bond_timeout': 0.0,
        }],
    )

    return LaunchDescription([
        LogInfo(msg='Launching ldlidar_node for Mini Pupper (LD06)'),
        ldlidar_container,
        ldlidar_lifecycle_mgr,
    ])
