#!/usr/bin/env python3
"""
mover_random_walk

Drives one `simple_mover` (see worlds/models/simple_mover/model.sdf) with a
random-walk velocity pattern: every `step_period` seconds, picks a new random
forward speed and turn rate and publishes it once on `/<mover_name>/cmd_vel`.
gz-sim's VelocityControl system holds the last commanded velocity
indefinitely (no watchdog/timeout), so a single publish per step is enough -
no need for a high-rate carrier publish.

One instance per mover, distinguished by the `mover_name` parameter (also
used to build its cmd_vel topic - must match the name the mover was spawned
with, see hybraut_nav/scripts/demo/dynamic_obstacles.py).
"""

import random

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from geometry_msgs.msg import Twist


class MoverRandomWalk(Node):

    def __init__(self):
        super().__init__('mover_random_walk')

        self.declare_parameter(
            'mover_name',
            '',
            ParameterDescriptor(
                description='Name of the mover this instance drives (must match its '
                            'spawned model name / bridged cmd_vel topic). Required.',
                type=ParameterType.PARAMETER_STRING
            )
        )
        self.declare_parameter(
            'step_period',
            3.0,
            ParameterDescriptor(
                description='Seconds between picking a new random velocity. (default: 3.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'linear_speed_max',
            0.3,
            ParameterDescriptor(
                description='Max forward speed (m/s) - sampled uniformly in [0, max], '
                            'forward-only to keep the walk from constantly reversing into '
                            'things. (default: 0.3)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'angular_speed_max',
            0.6,
            ParameterDescriptor(
                description='Max turn rate (rad/s) - sampled uniformly in [-max, max]. '
                            '(default: 0.6)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'seed',
            -1,
            ParameterDescriptor(
                description='RNG seed for reproducible walks. -1 (default) leaves the RNG '
                            'unseeded.',
                type=ParameterType.PARAMETER_INTEGER
            )
        )

        mover_name = self.get_parameter('mover_name').value
        if not mover_name:
            raise ValueError("mover_random_walk requires a non-empty 'mover_name' parameter")

        seed = self.get_parameter('seed').value
        self._rng = random.Random(seed if seed >= 0 else None)

        self._cmd_vel_pub = self.create_publisher(
            Twist,
            f'/{mover_name}/cmd_vel',
            qos_profile_system_default,
        )
        self._timer = self.create_timer(
            self.get_parameter('step_period').value,
            self._step_cb,
        )

        self.get_logger().info(f"mover_random_walk driving '{mover_name}' on /{mover_name}/cmd_vel")
        self._step_cb()  # pick + publish an initial velocity immediately

    def _step_cb(self):
        linear_max = self.get_parameter('linear_speed_max').value
        angular_max = self.get_parameter('angular_speed_max').value

        twist = Twist()
        twist.linear.x = self._rng.uniform(0.0, linear_max)
        twist.angular.z = self._rng.uniform(-angular_max, angular_max)
        self._cmd_vel_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = MoverRandomWalk()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
