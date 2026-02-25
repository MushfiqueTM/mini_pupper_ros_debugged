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

Uses the upstream ldrobot-lidar-ros2 driver (ldlidar_node) with lifecycle
management. Serial port, model, and frame_id are configured in
ldlidar_node/params/ldlidar.yaml (set to /dev/ldlidar, LD06, lidar_link).
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        LogInfo(msg='Launching ldlidar_node with lifecycle manager (upstream driver)'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare('ldlidar_node'),
                '/launch/ldlidar_with_mgr.launch.py',
            ]),
        ),
    ])
