#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2023 MangDang
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

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import LoadComposableNodes, Node, SetParameter
from launch_ros.descriptions import ComposableNode, ParameterFile
from launch_ros.substitutions import FindPackageShare
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    this_package = FindPackageShare('mini_pupper_navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    default_map_path = PathJoinSubstitution([this_package, 'maps', 'map.yaml'])
    nav2_param_file_path = PathJoinSubstitution(
        [this_package, 'param', 'mini_pupper.yaml'],
    )
    rviz_config_file_path = PathJoinSubstitution(
        [this_package, 'rviz', 'navigation.rviz'],
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    rviz = LaunchConfiguration('rviz')

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    rewritten_yaml = RewrittenYaml(
        source_file=nav2_param_file_path,
        root_key='',
        param_rewrites={'autostart': 'true', 'use_sim_time': use_sim_time},
        convert_types=True,
    )

    configured_params = ParameterFile(
        rewritten_yaml,
        allow_substs=True,
    )

    lifecycle_nodes = [
        'controller_server',
        'smoother_server',
        'planner_server',
        'behavior_server',
        'velocity_smoother',
        'bt_navigator',
        'waypoint_follower',
    ]

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),
        DeclareLaunchArgument('use_sim_time', default_value='False'),
        DeclareLaunchArgument('map', default_value=default_map_path),
        DeclareLaunchArgument(
            'rviz', default_value='false',
            description='Launch RViz on this machine',
        ),

        Node(
            name='nav2_container',
            package='rclcpp_components',
            executable='component_container_isolated',
            parameters=[configured_params, {'autostart': True}],
            arguments=['--ros-args', '--log-level', 'info'],
            remappings=remappings,
            output='screen',
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup_dir, 'launch', 'localization_launch.py'),
            ),
            launch_arguments={
                'map': map_yaml,
                'use_sim_time': use_sim_time,
                'autostart': 'true',
                'params_file': rewritten_yaml,
                'use_composition': 'True',
                'container_name': 'nav2_container',
            }.items(),
        ),

        GroupAction(actions=[
            SetParameter('use_sim_time', use_sim_time),
            LoadComposableNodes(
                target_container='nav2_container',
                composable_node_descriptions=[
                    ComposableNode(
                        package='nav2_controller',
                        plugin='nav2_controller::ControllerServer',
                        name='controller_server',
                        parameters=[configured_params],
                        remappings=remappings + [('cmd_vel', 'cmd_vel_nav')],
                    ),
                    ComposableNode(
                        package='nav2_smoother',
                        plugin='nav2_smoother::SmootherServer',
                        name='smoother_server',
                        parameters=[configured_params],
                        remappings=remappings,
                    ),
                    ComposableNode(
                        package='nav2_planner',
                        plugin='nav2_planner::PlannerServer',
                        name='planner_server',
                        parameters=[configured_params],
                        remappings=remappings,
                    ),
                    ComposableNode(
                        package='nav2_behaviors',
                        plugin='behavior_server::BehaviorServer',
                        name='behavior_server',
                        parameters=[configured_params],
                        remappings=remappings + [('cmd_vel', 'cmd_vel_nav')],
                    ),
                    ComposableNode(
                        package='nav2_bt_navigator',
                        plugin='nav2_bt_navigator::BtNavigator',
                        name='bt_navigator',
                        parameters=[configured_params],
                        remappings=remappings,
                    ),
                    ComposableNode(
                        package='nav2_waypoint_follower',
                        plugin='nav2_waypoint_follower::WaypointFollower',
                        name='waypoint_follower',
                        parameters=[configured_params],
                        remappings=remappings,
                    ),
                    ComposableNode(
                        package='nav2_velocity_smoother',
                        plugin='nav2_velocity_smoother::VelocitySmoother',
                        name='velocity_smoother',
                        parameters=[configured_params],
                        remappings=remappings + [
                            ('cmd_vel', 'cmd_vel_nav'),
                            ('cmd_vel_smoothed', 'cmd_vel'),
                        ],
                    ),
                    ComposableNode(
                        package='nav2_lifecycle_manager',
                        plugin='nav2_lifecycle_manager::LifecycleManager',
                        name='lifecycle_manager_navigation',
                        parameters=[{
                            'autostart': True,
                            'node_names': lifecycle_nodes,
                        }],
                    ),
                ],
            ),
        ]),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            condition=IfCondition(rviz),
            arguments=['-d', rviz_config_file_path],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen',
        ),
    ])
