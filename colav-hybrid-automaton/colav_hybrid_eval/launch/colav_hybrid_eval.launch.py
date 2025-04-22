from launch import LaunchDescription
from launch_ros.actions import Node

package_name = 'colav_hybrid_eval'


def generate_launch_description():
    return LaunchDescription([
        Node(
            package=package_name,
            executable='guards_node',
            output='screen',
        ),
        Node(
            package=package_name,
            executable='dynamics_node',
            output='screen',
        ),
        Node(
            package=package_name,
            executable='resets_node',
            output='screen',
        )
    ])
