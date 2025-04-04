from launch import LaunchDescription
from launch_ros.actions import Node

package_name = 'colav_hybrid_chart'

def generate_launch_description():
    return LaunchDescription([
        Node(
            package=package_name,
            executable='colav_hybrid_chart_node',
            name='colav_hybrid_chart',
            output='screen',
        ),
    ])