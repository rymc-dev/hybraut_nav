# !/usr/bin/env python
""" 
A launch file for hybraut ROS2
"""

from launch import LaunchDescription
from launch_ros.actions import Node

package_name = 'hybraut_nav'


def generate_launch_description():

    risk_envelope_node= Node(
        package=package_name,
        executable='risk_envelope_node',
        output='screen',
        parameters=[{
            
        }]
    )
    strategy_node = Node(
        package=package_name,
        executable='strategy_node',
        output='screen',
        parameters=[{
            
        }]
    )
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
        risk_envelope_node,
        strategy_node,
        immediate_node,
        tactical_node
    ])
