#!/usr/bin/env python3
"""
Tactical layer alone - `tactical_node` with no `immediate_node` (no
guidance/control) and no `strategy_node` (no global path planning).

Useful for exercising the COLAV automaton's discrete-mode transitions in
isolation - e.g. driving it with `fake_riskenv_publisher` or the real
`risk_envelope_node` and watching `/hybraut_nav/tactical_node/automaton_state`
without also having to stand up the control loop.

`tactical_node` exposes an action server - once it's up, send it a waypoint
directly (no strategy_node here to dispatch one for you):
    ros2 action send_goal /hybraut_nav/tactical_node/execute_mission \
        hybraut_nav/action/ExecuteMission \
        "{goal_waypoint: {position: {x: 5.0, y: 5.0}}}" --feedback

See docs/turtlebot3_demo.md and docs/turtlebot3_dynamic_obstacles_demo.md.
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
        description="Launch RViz with rviz/tactical_node.rviz alongside "
                     "tactical_node. Set to 'false' to skip it (e.g. "
                     "running headless or with your own RViz instance)."
    )
    safety_radius_arg = DeclareLaunchArgument(
        'safety_radius', default_value='0.5',
        description='colav_automaton safety_radius (m). Vessel-scale '
                     'default is 30.0 - override for smaller platforms '
                     '(e.g. a TurtleBot3).'
    )
    acceptance_radius_arg = DeclareLaunchArgument(
        'acceptance_radius', default_value='0.3',
        description='colav_automaton acceptance_radius (m).'
    )
    los_distance_threshold_arg = DeclareLaunchArgument(
        'los_distance_threshold', default_value='3.0',
        description='colav_automaton los_distance_threshold (m).'
    )
    lateral_offset_distance_arg = DeclareLaunchArgument(
        'lateral_offset_distance', default_value='1.0',
        description='colav_automaton lateral_offset_distance (m) - how far '
                     'off to the side of the unsafe region generate_new_'
                     'virtual_waypoint places its detour waypoint. '
                     'Vessel-scale default is 100.0 - left at that on a '
                     'TB3-scale room, every detour lands ~100m away and is '
                     'never reached, so the automaton just keeps stacking '
                     'new ones on top each Cruise cycle. Override for the '
                     'platform in use.'
    )
    longitudinal_offset_distance_arg = DeclareLaunchArgument(
        'longitudinal_offset_distance', default_value='1.0',
        description='colav_automaton longitudinal_offset_distance (m). Not '
                     'currently read by generate_new_virtual_waypoint, but '
                     'still vessel-scale (100.0) by default and accepted by '
                     'ColavAutomaton - kept in step with lateral_offset_distance.'
    )

    tactical_node = Node(
        package=package_name,
        executable='tactical_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'safety_radius': LaunchConfiguration('safety_radius'),
            'acceptance_radius': LaunchConfiguration('acceptance_radius'),
            'los_distance_threshold': LaunchConfiguration('los_distance_threshold'),
            'lateral_offset_distance': LaunchConfiguration('lateral_offset_distance'),
            'longitudinal_offset_distance': LaunchConfiguration('longitudinal_offset_distance'),
        }]
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', PathJoinSubstitution(
            [FindPackageShare(package_name), 'rviz', 'tactical_node.rviz'])],
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        use_sim_time_arg,
        safety_radius_arg,
        acceptance_radius_arg,
        los_distance_threshold_arg,
        lateral_offset_distance_arg,
        longitudinal_offset_distance_arg,
        rviz_arg,
        tactical_node,
        rviz_node,
    ])
