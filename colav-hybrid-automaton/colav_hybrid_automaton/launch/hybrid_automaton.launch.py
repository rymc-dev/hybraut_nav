from launch import LaunchDescription
from launch_ros.actions import Node

pkg_name = 'colav_hybrid_automaton'


def generate_launch_description():

    automaton_node = Node(
        package=pkg_name,
        executable='automaton',
        output='screen',
    )
    automaton_mission_manager_node = Node(
        package=pkg_name,
        executable='automaton_mission_manager',
        output='screen',
    )

    return LaunchDescription([
        automaton_node,
        automaton_mission_manager_node
    ])
