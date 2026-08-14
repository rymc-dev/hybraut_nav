#!/usr/bin/env python3
"""
Spawns N `simple_mover` dynamic obstacles into an already-running Gazebo
world, bridges their cmd_vel/odometry, drives each with a random walk, and
brings up agent_state_bridge + obstacles_state_bridge + risk_envelope_node
so the *real* risk_envelope_node -> tactical_node pipeline runs against live
obstacle state, instead of fake_riskenv_publisher's synthetic polygon.

Run AFTER the sim is already up, e.g.:
    export TURTLEBOT3_MODEL=waffle
    ros2 launch turtlebot3_gazebo empty_world.launch.py
    ros2 launch hybraut_nav hybraut_nav_dynamic_obstacles.launch.py

tactical_node/immediate_node are launched separately (see
docs/turtlebot3_demo.md) - this file only adds the dynamic-obstacle side.

See docs/turtlebot3_dynamic_obstacles_demo.md for the full walkthrough.
"""

import math
import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

package_name = 'hybraut_nav'

# fixed, distinguishable colours per mover (RGB), cycled if num_movers > 3
MOVER_COLORS = [
    (0.8, 0.1, 0.1),
    (0.1, 0.6, 0.9),
    (0.9, 0.7, 0.1),
]

SPAWN_RADIUS = 2.5


def generate_launch_description():
    num_movers = int(os.environ.get('HYBRAUT_NAV_NUM_MOVERS', '3'))

    sdf_template_path = os.path.join(
        get_package_share_directory(package_name),
        'worlds', 'models', 'simple_mover', 'model.sdf'
    )
    with open(sdf_template_path, 'r') as f:
        sdf_template = f.read()

    mover_names = [f'mover_{i + 1}' for i in range(num_movers)]

    spawn_actions = []
    bridge_lines = []
    for i, name in enumerate(mover_names):
        angle = 2 * math.pi * i / num_movers
        x = SPAWN_RADIUS * math.cos(angle)
        y = SPAWN_RADIUS * math.sin(angle)
        r, g, b = MOVER_COLORS[i % len(MOVER_COLORS)]

        rendered_sdf = sdf_template.format(name=name, x=x, y=y, r=r, g=g, b=b)

        spawn_actions.append(Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', name, '-string', rendered_sdf, '-z', '0.1'],
            output='screen',
        ))

        bridge_lines.append({
            'ros_topic_name': f'{name}/odom',
            'gz_topic_name': f'/model/{name}/odometry',
            'ros_type_name': 'nav_msgs/msg/Odometry',
            'gz_type_name': 'gz.msgs.Odometry',
            'direction': 'GZ_TO_ROS',
        })
        bridge_lines.append({
            'ros_topic_name': f'{name}/cmd_vel',
            'gz_topic_name': f'/model/{name}/cmd_vel',
            'ros_type_name': 'geometry_msgs/msg/Twist',
            'gz_type_name': 'gz.msgs.Twist',
            'direction': 'ROS_TO_GZ',
        })

    # ros_gz_bridge/parameter_bridge's config_file needs to exist on disk for
    # the life of the bridge process - written once here at launch-generation
    # time, not cleaned up automatically (harmless, small, in /tmp).
    bridge_config = tempfile.NamedTemporaryFile(
        mode='w', suffix='_hybraut_nav_movers_bridge.yaml', delete=False
    )
    for entry in bridge_lines:
        bridge_config.write(
            f"- ros_topic_name: \"{entry['ros_topic_name']}\"\n"
            f"  gz_topic_name: \"{entry['gz_topic_name']}\"\n"
            f"  ros_type_name: \"{entry['ros_type_name']}\"\n"
            f"  gz_type_name: \"{entry['gz_type_name']}\"\n"
            f"  direction: {entry['direction']}\n\n"
        )
    bridge_config.close()

    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_config.name}'],
        output='screen',
    )

    # use_sim_time matters here specifically because risk_envelope_node's
    # ApproximateTimeSynchronizer matches /agent_state <-> /obstacles_state by
    # header.stamp - if either bridge stamps its messages off the wall clock
    # instead of /clock (sim time), the two streams' stamps drift apart
    # indefinitely and never fall within the sync slop window, so
    # risk_envelope_node silently never fires.
    walker_nodes = [
        Node(
            package=package_name,
            executable='mover_random_walk',
            name=f'mover_random_walk_{name}',
            parameters=[{'mover_name': name, 'use_sim_time': True}],
            output='screen',
        )
        for name in mover_names
    ]

    agent_state_bridge_node = Node(
        package=package_name,
        executable='agent_state_bridge',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )
    obstacles_state_bridge_node = Node(
        package=package_name,
        executable='obstacles_state_bridge',
        parameters=[{'mover_names': mover_names, 'use_sim_time': True}],
        output='screen',
    )
    risk_envelope_node = Node(
        package=package_name,
        executable='risk_envelope_node',
        # dt_global_update_tolerance headroom: agent_state_bridge stamps from
        # the ego /odom sample time, obstacles_state_bridge stamps at its own
        # publish time - independently-timed streams rarely land within the
        # 0.5s default even when both correctly use sim time.
        parameters=[{'use_sim_time': True, 'dt_global_update_tolerance': 2.0}],
        output='screen',
    )

    return LaunchDescription([
        *spawn_actions,
        bridge_node,
        *walker_nodes,
        agent_state_bridge_node,
        obstacles_state_bridge_node,
        risk_envelope_node,
    ])
