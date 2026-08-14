#!/usr/bin/env python3
"""
Immediate layer alone - `immediate_node` with no `tactical_node` (no
reference dynamics) and no `strategy_node` (no global path planning).

`immediate_node` has no manual activation step - its control loop always
runs, but it only ever commands real motion while
`/hybraut_nav/continous_dynamics` is actively being published to (see the
module docstring in `immediate_node.py`). With nothing publishing that
topic here, it just holds an explicit stop. Feed it a fake setpoint
directly to exercise the guidance/control loop and its `/cmd_vel` output in
isolation, e.g. to sanity-check a new controller against the robot before
wiring the rest of the stack back in:
    ros2 topic pub /hybraut_nav/continous_dynamics std_msgs/msg/Float64MultiArray \
        "{data: [0.0, 0.0, 0.5, 0.0, 0.0]}" -r 20

See docs/turtlebot3_demo.md.
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
        description="Launch RViz with rviz/immediate_node.rviz alongside "
                     "immediate_node. Set to 'false' to skip it."
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
        arguments=['-d', PathJoinSubstitution(
            [FindPackageShare(package_name), 'rviz', 'immediate_node.rviz'])],
        output='screen',
        condition=IfCondition(LaunchConfiguration('rviz')),
    )

    return LaunchDescription([
        use_sim_time_arg,
        rviz_arg,
        immediate_node,
        rviz_node,
    ])
