# !/usr/bin/env python
""" 
A launch file for hybraut ROS2
"""

from launch import LaunchDescription
from launch_ros.actions import Node

package_name = 'hybraut_nav'


def generate_launch_description():

    immediate_node = Node(
        package=package_name,
        executable='immediate_node',
        output='screen',
        parameters=[{
        }]
    )
    tactical_node = Node(
        package=package_name,
        executable='tactical_node',
        output='screen',
        parameters=[{
        }]
    )

    return LaunchDescription([
        immediate_node,
        tactical_node
    ])