# !/usr/bin/env python3

""" 
This Node is Layer 3 of the HybrautNav Navigation Stack
This layer produces the low-level actuator commands for the controller or execution 
layer.

- It closes the HybrautNav navigation stack for fast control loops
- enforces safety limits
- interfaces with hardware (rudder, thrusters)
- and allows Layer 2 to stay physics agnostic
"""

import rclpy
from rclpy.node import Node


class ControllerNode(Node):
    ... 