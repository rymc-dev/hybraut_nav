import rclpy
from rclpy.node import Node
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.qos_config import QOS_PROFILE
from colav_interfaces.msg import Waypoint, Waypoints
from geometry_msgs.msg import Point32

rclpy.init()
pub_node = Node('pub_node')
publisher = pub_node.create_publisher(
    Waypoints,
    '/hybrid_automaton/waypoints',
    qos_profile=QOS_PROFILE
)

waypoints = Waypoints(
    waypoints = [
        Waypoint(
            position=Point32(x=float(10), y=float(10), z=float(0.2)),
            acceptance_radius=float(20)
        ),  
        Waypoint(
            position=Point32(x=float(20), y=float(50), z=float(0.2)),
            acceptance_radius=float(20)
        ),          
    ]
)

publisher.publish(waypoints)

rclpy.shutdown()
