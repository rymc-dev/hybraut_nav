from launch import LaunchDescription
from launch_ros.actions import Node

eval_pkg = 'colav_hybrid_eval'
chart_pkg = 'colav_hybrid_chart'

def generate_launch_description():
    return LaunchDescription([
        Node(
            package=eval_pkg,
            executable='guards_node',
            output='screen',
        ),
        Node(
            package=eval_pkg,
            executable='dynamics_node',
            output='screen',
        ),
        Node(
            package=chart_pkg,
            executable='colav_hybrid_chart_node',
            output='screen'
        )
    ])