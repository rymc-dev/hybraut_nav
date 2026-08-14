#!/usr/bin/env python3
"""
Strategic layer alone - `strategy_node` with no `tactical_node` and no
`immediate_node`.

Useful for exercising the global planner (A*/Dijkstra/RRT/RRT*) and its
`/map`/`planner/plan`/`planner/goal_pose` topics in isolation. Without
`tactical_node` up, a `navigate_to_goal` goal will fail once it tries to
dispatch the first leg (`tactical_node/execute_mission` action server
unavailable) - this configuration is for inspecting planning/map behaviour
on its own, not for running a full mission (see
`hybraut_nav_strategic_tactical_immediate.launch.py` for that).

Two live inputs `strategy_node` needs that a bare TB3 sim doesn't produce on
its own - see docs/turtlebot3_demo.md's "Strategic-driven demo" section:
    ros2 run hybraut_nav agent_state_bridge &
    ros2 run hybraut_nav fake_map_publisher
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

package_name = 'hybraut_nav'


def generate_launch_description():
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use /clock (sim time) instead of the wall clock - '
                     'required whenever Gazebo is the time source '
                     '(robot_state_publisher stamps /tf off /clock), '
                     'otherwise message stamps drift arbitrarily from the '
                     'TF buffer and TF-synchronised consumers (e.g. rviz '
                     'displays, message_filters) silently stop updating. '
                     'Doubly true with moving obstacles - see '
                     'turtlebot3_dynamic_obstacles_demo.md.'
    )
    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description="Launch RViz with rviz/strategy_node.rviz alongside "
                     "strategy_node. Set to 'false' to skip it."
    )

    strategy_node = Node(
        package=package_name,
        executable='strategy_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }]
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', PathJoinSubstitution(
            [FindPackageShare(package_name), 'rviz', 'strategy_node.rviz'])],
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        use_sim_time_arg,
        rviz_arg,
        strategy_node,
        rviz_node,
    ])
