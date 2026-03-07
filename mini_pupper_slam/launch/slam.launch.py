#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2022-2023 MangDang
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

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    slam_package = FindPackageShare('mini_pupper_slam')

    slam_toolbox_launch_path = PathJoinSubstitution([slam_package, 'launch', 'slam_toolbox.launch.py'])
    rviz_config_file_path = PathJoinSubstitution([slam_package, 'rviz', 'slam.rviz'])

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_launch_arg = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='False',
        description='Use simulation (Gazebo) clock if true',
    )

    rviz = LaunchConfiguration('rviz')
    rviz_launch_arg = DeclareLaunchArgument(
        name='rviz',
        default_value='False',
        description='Launch RViz2 (set to True on PC with display)',
    )

    return LaunchDescription([
        use_sim_time_launch_arg,
        rviz_launch_arg,
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(slam_toolbox_launch_path),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'rviz': 'False',
            }.items(),
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=[
                '-d', rviz_config_file_path,
            ],
            parameters=[
                {'use_sim_time': use_sim_time},
            ],
            output='screen',
            condition=IfCondition(rviz),
        ),
    ])
