#!/usr/bin/env python3
"""
Full stack: `risk_envelope_node` + `strategy_node` + `tactical_node` +
`immediate_node` - the "risk assessment" configuration, i.e.
`hybraut_nav_strategic_tactical_immediate.launch.py` plus the real risk
layer.

`risk_envelope_node` needs `/agent_state`/`/obstacles_state` publishers to do
anything (see `hybraut_nav_dynamic_obstacles.launch.py`'s
`agent_state_bridge`/`obstacles_state_bridge`, or a `hybraut_nav`-based
sim) - launching it here alone will just sit warning "No synchronised
agent/obstacles update received" until something publishes those. Do not
also run `hybraut_nav_dynamic_obstacles.launch.py` alongside this file - both
bring up their own `risk_envelope_node` and would collide (duplicate node
name, both publishing `/hybraut_nav/riskenv`).

`strategy_node` plans a global route and drives `tactical_node` (via its
`execute_mission` action) one leg at a time. It needs `/map` and
`/agent_state` feeding in separately - see
docs/turtlebot3_demo.md#strategic-driven-demo for the full setup (map/agent
bridges) - then send it one long-range goal for the whole mission:
    ros2 action send_goal /hybraut_nav/strategy_node/navigate_to_goal \
        hybraut_nav/action/NavigateToGoal \
        "{goal_waypoint: {position: {x: 3.0, y: 2.0}}}" --feedback

Cancel an in-progress mission early with `ros2 action cancel` (or Ctrl-C the
send_goal call above).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

package_name = 'hybraut_nav'


def generate_launch_description():
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use /clock (sim time) instead of the wall clock - '
                     'required whenever Gazebo is the time source '
                     '(robot_state_publisher / ros_gz_bridge stamp /tf off '
                     '/clock), otherwise message stamps drift arbitrarily '
                     'from the TF buffer and TF-synchronised consumers '
                     '(e.g. rviz displays, message_filters) silently stop '
                     'updating. Doubly true with moving obstacles - see '
                     'turtlebot3_dynamic_obstacles_demo.md.'
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
    dt_global_update_tolerance_arg = DeclareLaunchArgument(
        'dt_global_update_tolerance', default_value='0.5',
        description='risk_envelope_node ApproximateTimeSynchronizer slop '
                     '(s) between /agent_state and /obstacles_state - '
                     'independently-timed bridges rarely land within the '
                     'default even with matching clocks, headroom to 2.0 '
                     'is a reasonable starting point.'
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

    risk_envelope_node = Node(
        package=package_name,
        executable='risk_envelope_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'dt_global_update_tolerance': LaunchConfiguration('dt_global_update_tolerance'),
        }]
    )
    strategy_node = Node(
        package=package_name,
        executable='strategy_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
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

    return LaunchDescription([
        use_sim_time_arg,
        safety_radius_arg,
        acceptance_radius_arg,
        los_distance_threshold_arg,
        dt_global_update_tolerance_arg,
        lateral_offset_distance_arg,
        longitudinal_offset_distance_arg,
        risk_envelope_node,
        strategy_node,
        immediate_node,
        tactical_node,
    ])
