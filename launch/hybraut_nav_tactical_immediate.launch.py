#!/usr/bin/env python3
"""
Tactical + immediate layers, no `strategy_node`.

This is the pairing used by the TurtleBot3 demos (`docs/turtlebot3_demo.md`,
`docs/turtlebot3_dynamic_obstacles_demo.md`): `tactical_node` tracks whatever
waypoint it's sent and `immediate_node` tracks the resulting reference
dynamics, with the risk envelope fed in separately by either
`fake_riskenv_publisher` (base demo) or `risk_envelope_node` +
`hybraut_nav_dynamic_obstacles.launch.py` (moving-obstacles demo).

After launch:
    # no strategy_node here to dispatch waypoints for you - send one
    # directly (repeat for each leg of the demo route, e.g. (5, 5) then (0, 0)):
    ros2 action send_goal /hybraut_nav/tactical_node/execute_mission \
        hybraut_nav/action/ExecuteMission \
        "{goal_waypoint: {position: {x: 5.0, y: 5.0}}}" --feedback

For the moving-obstacles demo, launch this with `use_sim_time:=true` and
alongside `hybraut_nav_dynamic_obstacles.launch.py` - see
docs/turtlebot3_dynamic_obstacles_demo.md for the full walkthrough and why
`use_sim_time` matters here.
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
        description="Launch RViz with rviz/tactical_immediate.rviz "
                     "alongside tactical_node + immediate_node. Set to "
                     "'false' to skip it."
    )
    safety_radius_arg = DeclareLaunchArgument(
        'safety_radius', default_value='0.5',
        description='colav_automaton safety_radius (m). Vessel-scale '
                     'default is 30.0 - override for smaller platforms '
                     '(e.g. a TurtleBot3). Use 1.5 for the moving-obstacles '
                     'demo, whose movers spawn ~2.5m out.'
    )
    acceptance_radius_arg = DeclareLaunchArgument(
        'acceptance_radius', default_value='0.3',
        description='colav_automaton acceptance_radius (m).'
    )
    los_distance_threshold_arg = DeclareLaunchArgument(
        'los_distance_threshold', default_value='3.0',
        description='colav_automaton los_distance_threshold (m). Use 5.0 '
                     'for the moving-obstacles demo.'
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
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config', default_value=PathJoinSubstitution(
            [FindPackageShare(package_name), 'rviz', 'tactical_immediate.rviz']),
        description='Path to the rviz config to load alongside tactical_node '
                     '+ immediate_node. Defaults to this package\'s own '
                     'tactical_immediate.rviz - override for callers (e.g. '
                     'other packages\' launch files) that want their own '
                     'view instead.'
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
    immediate_node = Node(
        package=package_name,
        executable='immediate_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }]
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
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
        rviz_config_arg,
        tactical_node,
        immediate_node,
        rviz_node,
    ])
