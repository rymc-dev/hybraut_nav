#!/usr/bin/env python3
"""
Strategic + tactical + immediate layers, no `risk_envelope_node`.

Adds `strategy_node` (global path planning) on top of the
`hybraut_nav_tactical_immediate.launch.py` pairing. As with that file, the
risk envelope still needs to be fed in separately (`fake_riskenv_publisher`
or `risk_envelope_node` - see docs/turtlebot3_demo.md and
docs/turtlebot3_dynamic_obstacles_demo.md); this configuration just adds
strategic-layer waypoints/path planning to the mix.

`strategy_node` checks each waypoint is reachable and drives `tactical_node`
(via its `execute_mission` action) through them one leg at a time, in order.
It needs `/map` and `/agent_state` feeding in separately - see
docs/turtlebot3_demo.md#strategic-driven-demo for the full setup (map/agent
bridges) - then send it the ordered list of goal waypoints for the whole
mission:
    ros2 action send_goal /hybraut_nav/strategy_node/navigate_to_goal \
        hybraut_nav/action/NavigateToGoal \
        "{goal_waypoints: [{position: {x: 3.0, y: 2.0}}]}" --feedback

Cancel an in-progress mission early with `ros2 action cancel` (or Ctrl-C the
send_goal call above).
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
        description="Launch RViz with rviz/strategic_tactical_immediate.rviz "
                     "alongside strategy_node + tactical_node + "
                     "immediate_node. Set to 'false' to skip it."
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
    constant_velocity_arg = DeclareLaunchArgument(
        'constant_velocity', default_value='2.0',
        description='colav_automaton constant_velocity (m/s) - the target '
                     'speed its own internal reference dynamics '
                     '(flow_los_heading / constant_heading_dynamics) '
                     'integrate toward. Real commanded speed comes from '
                     "immediate_node's own desired_velocity below, not from "
                     'this - the two are independent params, but a caller '
                     'driving a real vessel should pass the same value to '
                     'both (see hybraut_nav_colreg_sim.launch.py for an '
                     "example) so tactical_node's own reference trajectory - "
                     'published on /hybraut_nav/continous_dynamics and drawn '
                     "in rviz - doesn't silently lag the vessel's real speed."
    )
    k_theta_arg = DeclareLaunchArgument(
        'k_theta', default_value='1.0',
        description='colav_automaton k_theta - proportional gain on LOS '
                     'heading error in flow_los_heading (theta_dot = '
                     'k_theta * e_theta on the reference trajectory). Higher '
                     'tracks a moving LOS bearing more tightly; the reference '
                     'is a stable first-order response for any positive gain '
                     '(no overshoot), so this mainly trades reference lag '
                     'against how eagerly it reacts to a freshly-generated '
                     'COLAV detour waypoint.'
    )
    k_v_arg = DeclareLaunchArgument(
        'k_v', default_value='1.0',
        description='colav_automaton k_v - proportional gain driving the '
                     "reference trajectory's internal speed state toward "
                     'constant_velocity (or toward 0, while in Fallback). '
                     'Only affects that internal reference value, not real '
                     'commanded speed - see constant_velocity above.'
    )
    desired_velocity_arg = DeclareLaunchArgument(
        'desired_velocity', default_value='7.2',
        description='immediate_node desired_velocity (m/s) - the real, '
                     'constant linear speed commanded on /cmd_vel whenever '
                     'the tactical layer is active. This is what actually '
                     'drives the vessel; see constant_velocity above for the '
                     'note on keeping the two in step.'
    )
    fallback_timeout_arg = DeclareLaunchArgument(
        'fallback_timeout', default_value='30.0',
        description='colav_automaton fallback_timeout (s) - how long the '
                     'automaton may idle in Fallback (braking/holding '
                     "heading, waiting for safe_conditions_guard) before "
                     'the leg is reported as failed. See tactical_node.py\'s '
                     'own fallback_timeout param description.'
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config', default_value=PathJoinSubstitution(
            [FindPackageShare(package_name), 'rviz', 'strategic_tactical_immediate.rviz']),
        description='Path to the rviz config to load alongside strategy_node '
                     '+ tactical_node + immediate_node. Defaults to this '
                     'package\'s own strategic_tactical_immediate.rviz - '
                     'override for callers (e.g. other packages\' launch '
                     'files) that want their own view instead.'
    )

    strategy_node = Node(
        package=package_name,
        executable='strategy_node',
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
            'constant_velocity': LaunchConfiguration('constant_velocity'),
            'k_theta': LaunchConfiguration('k_theta'),
            'k_v': LaunchConfiguration('k_v'),
            'fallback_timeout': LaunchConfiguration('fallback_timeout'),
        }]
    )
    immediate_node = Node(
        package=package_name,
        executable='immediate_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'desired_velocity': LaunchConfiguration('desired_velocity'),
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
        constant_velocity_arg,
        k_theta_arg,
        k_v_arg,
        desired_velocity_arg,
        fallback_timeout_arg,
        rviz_arg,
        rviz_config_arg,
        strategy_node,
        tactical_node,
        immediate_node,
        rviz_node,
    ])
