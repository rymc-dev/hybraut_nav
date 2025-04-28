from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet
from rclpy.node import Node

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from hybrid_automaton.config.qos_config import QOS_PROFILE
import rclpy
from colav_interfaces.msg import Waypoints, Waypoint
from std_msgs.msg import Header
from builtin_interfaces.msg import Time

import time

rclpy.init()

pub_node = Node('pub_node')
agent_pub = pub_node.create_publisher(
    AgentUpdate,
    '/agent_update',
    QOS_PROFILE
)

obstacles_pub = pub_node.create_publisher(
    ObstaclesUpdate,
    '/obstacles_update',
    QOS_PROFILE
)

unsafe_set_pub = pub_node.create_publisher(
    UnsafeSet,
    '/unsafe_set',
    QOS_PROFILE
)

waypoints_pub = pub_node.create_publisher(
    Waypoints,
    '/hybrid_automaton/waypoints',
    QOS_PROFILE
)

while True:
    try:
        now = time.time()  # seconds since epoch as float
        sec = int(now)
        nanosec = int((now - sec) * 1e9)

        ros_time = Time()
        ros_time.sec = sec
        ros_time.nanosec = nanosec

        agent_update = AgentUpdate(header=Header(stamp=ros_time))
        obstacles_update = ObstaclesUpdate(header=Header(stamp=ros_time))
        unsafe_set_update = UnsafeSet(header=Header(stamp=ros_time))
        waypoints_update = Waypoints(waypoints=[Waypoint(), Waypoint()])

        agent_pub.publish(agent_update)
        obstacles_pub.publish(obstacles_update)
        unsafe_set_pub.publish(unsafe_set_update)
        waypoints_pub.publish(waypoints_update)
        time.sleep(0.1)

    except KeyboardInterrupt:
        break

rclpy.shutdown()
