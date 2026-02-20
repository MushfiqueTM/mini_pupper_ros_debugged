#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2024-2025 MangDang
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
ROS 2 Controllers launch file for Mini Pupper simulation.

Updated for ROS 2 Jazzy compatibility.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Note: In Jazzy, the spawner may need --controller-manager-timeout
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager-timeout', '30',
        ],
        output='screen',
    )

    joint_group_effort_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_group_effort_controller',
            '--controller-manager-timeout', '30',
        ],
        output='screen',
    )

    return LaunchDescription([
        joint_state_broadcaster_spawner,
        joint_group_effort_controller_spawner,
    ])
