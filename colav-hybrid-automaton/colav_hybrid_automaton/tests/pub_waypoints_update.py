import rclpy
from rclpy.node import Node
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from hybrid_automaton.config.qos_config import QOS_PROFILE
from colav_interfaces.msg import Waypoint, Waypoints
from geometry_msgs.msg import Point32

rclpy.init()
pub_node = Node('pub_node')
publisher = pub_node.create_publisher(
    Waypoints,
    '/hybrid_automaton/state/waypoints',
    qos_profile=QOS_PROFILE
)

waypoints = Waypoints(
    waypoints = [
        Waypoint(
            position=Point32(x=1019.995, y=1015.666, z=0.0),
            acceptance_radius=20.0
        )    
    ]
)

publisher.publish(waypoints)

rclpy.shutdown()
