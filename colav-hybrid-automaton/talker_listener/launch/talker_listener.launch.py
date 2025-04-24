from launch import LaunchDescription
from launch_ros.actions import Node

package = 'talker_listener'
TOPIC = 'chatter'

def generate_launch_description():
    talker = Node(
        package=package,
        executable="talker_node",
        name="talker_node",
        parameters=[{
            "topic": TOPIC
        }]
    )
    listener = Node(
        package=package,
        executable='listener_node',
        name='listener_node',
        parameters=[{
            "topic": TOPIC
        }]
    )

    return LaunchDescription([
        talker,
        listener
    ])