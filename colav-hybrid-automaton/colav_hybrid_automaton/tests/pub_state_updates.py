from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, Waypoints
from rclpy.node import Node

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from hybrid_automaton.config.qos_config import QOS_PROFILE
import rclpy
from std_msgs.msg import Header
from builtin_interfaces.msg import Time

import time

rclpy.init()

pub_node = Node('pub_node')
agent_pub = pub_node.create_publisher(
    AgentUpdate,
    '/state/agent',
    QOS_PROFILE
)

obstacles_pub = pub_node.create_publisher(
    ObstaclesUpdate,
    '/state/obstacles',
    QOS_PROFILE
)

unsafe_set_pub = pub_node.create_publisher(
    UnsafeSet,
    '/state/unsafe_set',
    QOS_PROFILE
)

waypoints_pub = pub_node.create_publisher(
    Waypoints,
    '/hybrid_automaton/state/waypoints',
    QOS_PROFILE
)

from geometry_msgs.msg import Point32

# waypoints_update = Waypoints(waypoints=[Waypoint(position=Point32(x=0.0, y=0.0), acceptance_radius = 20.0), Waypoint(position=Point32(x=100.0, y=100.9), acceptance_radius=10.0)])
waypoints_update = Waypoints(waypoints=[Waypoint(position=Point32(x=0.0, y=100.9), acceptance_radius=0.0)])
# waypoints_update = Waypoints(waypoints=[Waypoint(position=Point32(x=0.0, y=0.0), acceptance_radius = 20.0) , Waypoint(position=Point32(x=100.0, y=100.0))])


while True:
    try:
        now = time.time()  # seconds since epoch as float
        sec = int(now)
        nanosec = int((now - sec) * 1e9)

        ros_time = Time()
        ros_time.sec = sec
        ros_time.nanosec = nanosec
        from geometry_msgs.msg import Pose
        from geometry_msgs.msg import Point
        from geometry_msgs.msg import Quaternion
        agent_update = AgentUpdate(header=Header(stamp=ros_time), velocity=2.0)
        obstacles_update = ObstaclesUpdate(header=Header(stamp=ros_time))
        unsafe_set_update = UnsafeSet(header=Header(stamp=ros_time))
    
        waypoints_pub.publish(waypoints_update)
        agent_pub.publish(agent_update)
        obstacles_pub.publish(obstacles_update)
        unsafe_set_pub.publish(unsafe_set_update)

        time.sleep(0.1)
    except KeyboardInterrupt:
        pass

rclpy.shutdown()
