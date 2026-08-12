#!/usr/bin/env python3
"""
Risk Node for HybrautNav Navigation Stack computes the real-time risk
envelope (unsafe set) around the agent from tracked obstacles, using
riskenv's CPA / indices-of-interest geometry, and republishes it for the
tactical layer's hybrid automaton to route around.

Subscribes (time-synchronised):
    /agent_state      (colav_interfaces/AgentState)
    /obstacles_state  (colav_interfaces/ObstaclesState)

Publishes:
    /hybraut_nav/riskenv (geometry_msgs/PolygonStamped) - risk envelope
    hull vertices, matching the contract hybraut_nav_tactical/tactical_node.py
    already subscribes to.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from message_filters import ApproximateTimeSynchronizer, Subscriber

from riskenv import create_unsafe_set, Agent, Obstacle, heading_from_quaternion

from colav_interfaces.msg import AgentState, ObstaclesState
from geometry_msgs.msg import PolygonStamped, Point32
from std_msgs.msg import Header

from hybraut_nav.qos.world_state_qos import world_state_qos


class RiskEnvelopeNode(Node):
    """Wraps `riskenv.create_unsafe_set()` as a ROS2 node: fuses the agent's
    state with tracked obstacles (static and dynamic) and republishes the
    resulting risk envelope as the `riskenv` auxiliary input the tactical
    layer's COLAV automaton evaluates its guards against."""

    def __init__(
        self,
        node_name: str = 'risk_node',
        namespace: str = 'hybraut_nav',
        dt_global_update_tolerance: float = 0.5,
    ) -> None:
        super().__init__(node_name, namespace=namespace)
        self.get_logger().info(f"starting {namespace}/{node_name}")

        self.declare_parameter(
            'dsf',
            10.0,
            ParameterDescriptor(
                name='dsf',
                type=ParameterType.PARAMETER_DOUBLE,
                description='Distance Safety Factor (metres). '
                        'Proximity threshold used across riskenv\'s I1/I2/I3 '
                        'indices-of-interest filters. '
                        f'(default: {10.0})'
            )
        )
        self.declare_parameter(
            'time_of_interest',
            15.0,
            ParameterDescriptor(
                name='time_of_interest',
                type=ParameterType.PARAMETER_DOUBLE,
                description='Horizon (seconds) for riskenv\'s I3 (TCPA-based) filter. '
                        f'(default: {15.0})'
            )
        )

        self.riskenv_pub = self.create_publisher(
            PolygonStamped,
            '/hybraut_nav/riskenv',
            qos_profile_system_default,
        )

        self.agent_sub = Subscriber(self, AgentState, '/agent_state', qos_profile=world_state_qos)
        self.obstacles_sub = Subscriber(self, ObstaclesState, '/obstacles_state', qos_profile=world_state_qos)

        # synchronised: the riskenv envelope is only recomputed once both
        # /agent_state and /obstacles_state have a fresh, matched-up pair.
        self.sync = ApproximateTimeSynchronizer(
            [self.agent_sub, self.obstacles_sub],
            queue_size=10,
            slop=dt_global_update_tolerance
        )
        self.sync.registerCallback(self.sync_callback)

        self.last_update_time = self.get_clock().now()
        self.timeout_tolerance = dt_global_update_tolerance * 2  # extra margin
        self.timer = self.create_timer(0.1, self.check_for_timeout)

    """ === synchronised state callback === """

    def sync_callback(self, agent_msg: AgentState, obstacles_msg: ObstaclesState):
        self.last_update_time = self.get_clock().now()
        self.process_data(agent_msg, obstacles_msg)

    def check_for_timeout(self):
        """Warns if a synchronised agent/obstacles update hasn't landed within tolerance."""
        elapsed = (self.get_clock().now() - self.last_update_time).nanoseconds * 1e-9

        if elapsed > self.timeout_tolerance:
            self.get_logger().warn(f"No synchronised agent/obstacles update received in {elapsed:.2f} seconds!")
            self.last_update_time = self.get_clock().now()  # reset to avoid spamming

    """ === riskenv pipeline === """

    def process_data(self, agent_msg: AgentState, obstacles_msg: ObstaclesState):
        agent = self._extract_agent(agent_msg)
        obstacles = self._extract_obstacles(obstacles_msg)

        riskenv_vertices = create_unsafe_set(
            agent=agent,
            obstacles=obstacles,
            dsf=self.get_parameter('dsf').value,
            time_of_interest=self.get_parameter('time_of_interest').value,
        )

        self._publish_riskenv(riskenv_vertices)

    def _extract_agent(self, agent_msg: AgentState) -> Agent:
        return Agent(
            position=(agent_msg.pose.position.x, agent_msg.pose.position.y),
            heading=heading_from_quaternion(
                agent_msg.pose.orientation.x,
                agent_msg.pose.orientation.y,
                agent_msg.pose.orientation.z,
                agent_msg.pose.orientation.w,
            ),
            speed=agent_msg.velocity,
            yaw_rate=agent_msg.yaw_rate,
            safety_radius=agent_msg.safety_radius,
        )

    def _extract_obstacles(self, obstacles_msg: ObstaclesState) -> list:
        """riskenv has no notion of static vs dynamic - both are folded into
        a single flat list of Obstacle, with static obstacles given zero
        speed/yaw_rate and their inflation radius standing in for
        safety_radius."""
        obstacles = [
            Obstacle(
                position=(dynamic.pose.position.x, dynamic.pose.position.y),
                heading=heading_from_quaternion(
                    dynamic.pose.orientation.x,
                    dynamic.pose.orientation.y,
                    dynamic.pose.orientation.z,
                    dynamic.pose.orientation.w,
                ),
                speed=dynamic.velocity,
                yaw_rate=dynamic.yaw_rate,
                safety_radius=dynamic.safety_radius,
                tag=dynamic.tag,
            )
            for dynamic in obstacles_msg.dynamic_obstacles
        ]

        obstacles += [
            Obstacle(
                position=(static.pose.position.x, static.pose.position.y),
                heading=heading_from_quaternion(
                    static.pose.orientation.x,
                    static.pose.orientation.y,
                    static.pose.orientation.z,
                    static.pose.orientation.w,
                ),
                speed=0.0,
                yaw_rate=0.0,
                safety_radius=static.geometry.inflation_radius,
                tag=static.tag,
            )
            for static in obstacles_msg.static_obstacles
        ]

        return obstacles

    """ === publishing === """

    def _publish_riskenv(self, riskenv_vertices: list):
        msg = PolygonStamped()
        msg.header = Header(
            stamp=self.get_clock().now().to_msg(),
            frame_id='map',
        )
        msg.polygon.points = [
            Point32(x=float(vertex[0]), y=float(vertex[1]), z=0.0)
            for vertex in riskenv_vertices
        ]
        self.riskenv_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RiskEnvelopeNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
