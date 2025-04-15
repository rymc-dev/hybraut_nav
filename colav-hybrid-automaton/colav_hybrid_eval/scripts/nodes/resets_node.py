#!/usr/bin/python3
"""
"""
from rclpy.node import Node
from utils.resets import (
    reset_CRUISE_to_T2LOS,
    reset_WAYPOINT_REACHED_to_CRUISE
)

class HAResetsNode(Node):
    def __init__(
        self,
        name: str = 'resets_node',
        namespace: str = 'hybrid_automaton'
    ):
        super().__init__(name, namespace=namespace)
        