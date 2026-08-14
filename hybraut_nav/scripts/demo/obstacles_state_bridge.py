#!/usr/bin/env python3
"""
obstacles_state_bridge

Aggregates each dynamic-obstacle mover's bridged `/<mover_name>/odom` into a
single `colav_interfaces/msg/ObstaclesState` on `/obstacles_state` - the
input `risk_envelope_node` actually expects. Pairs with `agent_state_bridge`
(ego side). `static_obstacles` is left empty - only dynamic movers are
modelled by this demo, see worlds/models/simple_mover.
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from std_msgs.msg import Header
from nav_msgs.msg import Odometry
from colav_interfaces.msg import ObstaclesState, DynamicObstacleState, DynamicObstacleGeometry


class ObstaclesStateBridge(Node):

    def __init__(self):
        super().__init__('obstacles_state_bridge')

        self.declare_parameter(
            'mover_names', [''],
            ParameterDescriptor(description='Names of the dynamic-obstacle movers to track - '
                                             "each subscribed on /<mover_name>/odom. Required.",
                                 type=ParameterType.PARAMETER_STRING_ARRAY)
        )
        self.declare_parameter(
            'publish_rate', 10.0,
            ParameterDescriptor(description='Rate (Hz) to publish the aggregated ObstaclesState. '
                                             '(default: 10.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'beam', 0.3,
            ParameterDescriptor(description='Obstacle width (m). (default: 0.3)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'loa', 0.3,
            ParameterDescriptor(description='Obstacle length overall (m). (default: 0.3)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'safety_radius', 0.3,
            ParameterDescriptor(description='Obstacle safety perimeter radius (m). (default: 0.3)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )

        mover_names = [name for name in self.get_parameter('mover_names').value if name]
        if not mover_names:
            raise ValueError("obstacles_state_bridge requires a non-empty 'mover_names' parameter")

        self._latest_odom = {}
        self._subs = [
            self.create_subscription(
                Odometry,
                f'/{mover_name}/odom',
                self._make_odom_cb(mover_name),
                qos_profile_system_default,
            )
            for mover_name in mover_names
        ]

        self._obstacles_state_pub = self.create_publisher(
            ObstaclesState,
            '/obstacles_state',
            qos_profile_system_default,
        )
        self._timer = self.create_timer(
            1.0 / self.get_parameter('publish_rate').value,
            self._publish_cb,
        )

        self.get_logger().info(
            f'obstacles_state_bridge up - tracking {mover_names} -> /obstacles_state'
        )

    def _make_odom_cb(self, mover_name: str):
        def _cb(msg: Odometry):
            self._latest_odom[mover_name] = msg
        return _cb

    def _publish_cb(self):
        beam = self.get_parameter('beam').value
        loa = self.get_parameter('loa').value
        safety_radius = self.get_parameter('safety_radius').value

        obstacles_state = ObstaclesState()
        obstacles_state.header = Header(stamp=self.get_clock().now().to_msg(), frame_id='odom')
        obstacles_state.static_obstacles = []
        obstacles_state.dynamic_obstacles = [
            DynamicObstacleState(
                tag=mover_name,
                type='dynamic',
                pose=odom.pose.pose,
                velocity=math.hypot(odom.twist.twist.linear.x, odom.twist.twist.linear.y),
                acceleration=0.0,
                yaw_rate=odom.twist.twist.angular.z,
                geometry=DynamicObstacleGeometry(loa=loa, beam=beam),
                safety_radius=safety_radius,
            )
            for mover_name, odom in self._latest_odom.items()
        ]

        self._obstacles_state_pub.publish(obstacles_state)


def main(args=None):
    rclpy.init(args=args)
    node = ObstaclesStateBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
