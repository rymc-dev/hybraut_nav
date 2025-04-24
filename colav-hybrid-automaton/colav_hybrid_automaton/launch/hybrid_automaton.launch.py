from launch import LaunchDescription
from launch_ros.actions import Node

pkg_name = 'colav_hybrid_automaton'


def generate_launch_description():

    guards_node = Node(
        package=pkg_name,
        executable='guards_node',
        output='screen',
    )

    dynamics_node =  Node(
        package=pkg_name,
        executable='dynamics_node',
        output='screen',
    )

    resets_node = Node(
        package=pkg_name,
        executable='resets_node',
        output='screen'
    )
    
    chart_node = Node(
        package=pkg_name,
        executable='chart_node',
        output='screen'
    )

    return LaunchDescription([
        guards_node,
        dynamics_node,
        resets_node,
        chart_node
    ])
