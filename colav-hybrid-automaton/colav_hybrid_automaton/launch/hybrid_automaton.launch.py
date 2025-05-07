from launch import LaunchDescription
from launch_ros.actions import Node

pkg_name = 'colav_hybrid_automaton'


def generate_launch_description():

    dynamic_feedback_node = Node(
        package=pkg_name,
        executable='dynamic_feedback_node',
        output='screen',
    )

    transition_evaluation_node =  Node(
        package=pkg_name,
        executable='transition_evaluation_node',
        output='screen',
    )

    transition_engine_node = Node(
        package=pkg_name,
        executable='transition_engine_node',
        output='screen'
    )
    
    lifecycle_manager_node = Node(
        package=pkg_name,
        executable='lifecycle_manager_node',
        output='screen'
    )

    return LaunchDescription([
        dynamic_feedback_node,
        transition_evaluation_node,
        transition_engine_node,
        lifecycle_manager_node
    ])
