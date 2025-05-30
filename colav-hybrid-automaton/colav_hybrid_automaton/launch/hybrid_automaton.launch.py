from launch import LaunchDescription
from launch_ros.actions import Node

pkg_name = 'colav_hybrid_automaton'


def generate_launch_description():

    lifecycle_node = Node(
        package=pkg_name,
        executable='lifecycle_node',
        output='screen',
    )
    mission_control_node = Node(
        package=pkg_name,
        executable='mission_control_node',
        output='screen',
    )

    return LaunchDescription([
        lifecycle_node,
        mission_control_node
    ])
