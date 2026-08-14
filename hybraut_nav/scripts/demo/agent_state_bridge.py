#!/usr/bin/env python3
"""
agent_state_bridge

Republishes the ego robot's `/odom` as `colav_interfaces/msg/AgentState` on
`/agent_state` - the input `risk_envelope_node` actually expects, which a
bare TurtleBot3 sim never produces on its own. Pairs with
`obstacles_state_bridge` (dynamic obstacle side) to let the real
risk_envelope_node -> tactical_node pipeline run end-to-end against live
Gazebo state, instead of `fake_riskenv_publisher`'s synthetic polygon.
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from nav_msgs.msg import Odometry
from colav_interfaces.msg import AgentState


class AgentStateBridge(Node):

    def __init__(self):
        super().__init__('agent_state_bridge')

        self.declare_parameter(
            'agent_tag', 'ego',
            ParameterDescriptor(description="Tag stamped into AgentState.agent_tag. (default: 'ego')",
                                 type=ParameterType.PARAMETER_STRING)
        )
        self.declare_parameter(
            'beam', 0.3,
            ParameterDescriptor(description='Agent width (m). (default: 0.3)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'loa', 0.3,
            ParameterDescriptor(description='Agent length overall (m). (default: 0.3)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'safety_radius', 0.5,
            ParameterDescriptor(description='Agent safety perimeter radius (m) - keep in sync '
                                             "with tactical_node's safety_radius param. (default: 0.5)",
                                 type=ParameterType.PARAMETER_DOUBLE)
        )

        self._agent_state_pub = self.create_publisher(
            AgentState,
            '/agent_state',
            qos_profile_system_default,
        )
        self._odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self._odom_cb,
            qos_profile_system_default,
        )

        self.get_logger().info('agent_state_bridge up - republishing /odom as /agent_state')

    def _odom_cb(self, msg: Odometry):
        agent_state = AgentState()
        agent_state.header = msg.header
        agent_state.agent_tag = self.get_parameter('agent_tag').value
        agent_state.pose = msg.pose.pose
        agent_state.velocity = math.hypot(msg.twist.twist.linear.x, msg.twist.twist.linear.y)
        agent_state.acceleration = 0.0
        agent_state.yaw_rate = msg.twist.twist.angular.z
        agent_state.beam = self.get_parameter('beam').value
        agent_state.loa = self.get_parameter('loa').value
        agent_state.safety_radius = self.get_parameter('safety_radius').value

        self._agent_state_pub.publish(agent_state)


def main(args=None):
    rclpy.init(args=args)
    node = AgentStateBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
