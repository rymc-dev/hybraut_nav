#!/usr/bin/env python3
"""
Risk Node for HybrautNav Navigation Stack computes the real-time risk
envelope (unsafe set) around the agent from tracked obstacles, using
riskenv's CPA / indices-of-interest geometry, and republishes it for the
tactical layer's hybrid automaton to route around.

Subscribes (time-synchronised):
    /odom             (nav_msgs/Odometry)
    /obstacles_state  (hybraut_nav/ObstaclesState)

Publishes:
    /hybraut_nav/riskenv (geometry_msgs/PolygonStamped) - risk envelope
    hull vertices, matching the contract hybraut_nav_tactical/tactical_node.py
    already subscribes to.
    /hybraut_nav/maneuver_bias (hybraut_nav/ManeuverBias) - COLREGs-informed
    avoidance-side bias, from colav_automaton.classification.classify_unsafe_set_obstacles()
    over the same agent/obstacles/dsf/time_of_interest used to build the
    unsafe region above - tactical_node.py feeds this into the automaton's
    'maneuver_bias' auxiliary state to steer generate_new_virtual_waypoint's
    side selection.
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from message_filters import ApproximateTimeSynchronizer, Subscriber

from riskenv import create_unsafe_set, Agent, Obstacle, heading_from_quaternion
from colav_automaton.classification import classify_unsafe_set_obstacles, Maneuver

from nav_msgs.msg import Odometry
from hybraut_nav.msg import ObstaclesState, ManeuverBias
from geometry_msgs.msg import PolygonStamped, Point32, Point
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray

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
    ) -> None:
        super().__init__(node_name, namespace=namespace)
        self.get_logger().info(f"starting {namespace}/{node_name}")

        self.declare_parameter(
            'dt_global_update_tolerance',
            0.5,
            ParameterDescriptor(
                name='dt_global_update_tolerance',
                type=ParameterType.PARAMETER_DOUBLE,
                description='ApproximateTimeSynchronizer slop (seconds) between '
                        '/odom and /obstacles_state header.stamps - also used '
                        '(x2) as the check_for_timeout watchdog threshold. Independent '
                        'bridges/publishers rarely stamp perfectly in step even when '
                        'both correctly use sim time, so this may need headroom above '
                        'the two streams\' actual publish-latency gap. '
                        f'(default: {0.5})'
            )
        )
        self.declare_parameter(
            'dsf',
            200.0,
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
            100.0,
            ParameterDescriptor(
                name='time_of_interest',
                type=ParameterType.PARAMETER_DOUBLE,
                description='Horizon (seconds) for riskenv\'s I3 (TCPA-based) filter. '
                        f'(default: {20.0})'
            )
        )
        self.declare_parameter(
            'safety_radius',
            15.0,
            ParameterDescriptor(
                name='safety_radius',
                type=ParameterType.PARAMETER_DOUBLE,
                description='Agent safety perimeter radius (m) - /odom carries no '
                        'such field, so this stands in for it. '
                        f'(default: {0.5})'
            )
        )

        self.riskenv_pub = self.create_publisher(
            PolygonStamped,
            '/hybraut_nav/riskenv',
            qos_profile_system_default,
        )
        # RViz-friendly mirror of the same hull: PolygonStamped alone renders
        # as a thin, fixed-color outline with no fill, so this republishes it
        # as a filled + outlined Marker pair (see _publish_riskenv_marker).
        self.riskenv_marker_pub = self.create_publisher(
            MarkerArray,
            '/hybraut_nav/riskenv_markers',
            qos_profile_system_default,
        )
        self.maneuver_bias_pub = self.create_publisher(
            ManeuverBias,
            '/hybraut_nav/maneuver_bias',
            qos_profile_system_default,
        )

        self.agent_sub = Subscriber(self, Odometry, '/odom', qos_profile=world_state_qos)
        self.obstacles_sub = Subscriber(self, ObstaclesState, '/obstacles_state', qos_profile=world_state_qos)

        dt_global_update_tolerance = self.get_parameter('dt_global_update_tolerance').value

        # synchronised: the riskenv envelope is only recomputed once both
        # /odom and /obstacles_state have a fresh, matched-up pair.
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

    def sync_callback(self, agent_msg: Odometry, obstacles_msg: ObstaclesState):
        self.last_update_time = self.get_clock().now()
        self.process_data(agent_msg, obstacles_msg)

    def check_for_timeout(self):
        """Warns if a synchronised agent/obstacles update hasn't landed within tolerance."""
        elapsed = (self.get_clock().now() - self.last_update_time).nanoseconds * 1e-9

        if elapsed > self.timeout_tolerance:
            self.get_logger().warn(f"No synchronised agent/obstacles update received in {elapsed:.2f} seconds!")
            self.last_update_time = self.get_clock().now()  # reset to avoid spamming

    """ === riskenv pipeline === """

    def process_data(self, agent_msg: Odometry, obstacles_msg: ObstaclesState):
        agent = self._extract_agent(agent_msg)
        obstacles = self._extract_obstacles(obstacles_msg)
        dsf = self.get_parameter('dsf').value
        time_of_interest = self.get_parameter('time_of_interest').value

        riskenv_vertices = create_unsafe_set(
            agent=agent,
            obstacles=obstacles,
            dsf=dsf,
            time_of_interest=time_of_interest,
        )

        # dsf/time_of_interest must match create_unsafe_set's above so the
        # maneuver bias stays scoped to exactly the obstacles the unsafe
        # region above represents - see classify_unsafe_set_obstacles's
        # docstring.
        maneuver = classify_unsafe_set_obstacles(
            agent=agent,
            obstacles=obstacles,
            dsf=dsf,
            time_of_interest=time_of_interest,
        )

        self._publish_riskenv(riskenv_vertices)
        self._publish_maneuver_bias(maneuver)

    def _extract_agent(self, agent_msg: Odometry) -> Agent:
        return Agent(
            position=(agent_msg.pose.pose.position.x, agent_msg.pose.pose.position.y),
            heading=heading_from_quaternion(
                agent_msg.pose.pose.orientation.x,
                agent_msg.pose.pose.orientation.y,
                agent_msg.pose.pose.orientation.z,
                agent_msg.pose.pose.orientation.w,
            ),
            speed=math.hypot(agent_msg.twist.twist.linear.x, agent_msg.twist.twist.linear.y),
            yaw_rate=agent_msg.twist.twist.angular.z,
            safety_radius=self.get_parameter('safety_radius').value,
        )

    def _extract_obstacles(self, obstacles_msg: ObstaclesState) -> list:
        """riskenv has no notion of static vs dynamic - both are folded into
        a single flat list of Obstacle, with static obstacles given zero
        speed/yaw_rate and their inflation radius standing in for
        safety_radius.

        riskenv.Obstacle has a single free-text `tag` field, which
        colav_automaton.classification.normalize_vessel_type() keyword-matches
        expecting AIS-style vessel-*type* text (e.g. "fishing", "tanker") for
        Rule 18 right-of-way weighting - so it's fed from each obstacle's
        `type` (classification), not `tag` (its identifier/name), falling
        back to `tag` only if `type` was left blank."""
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
                tag=dynamic.type or dynamic.tag,
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
                tag=static.type or static.tag,
            )
            for static in obstacles_msg.static_obstacles
        ]

        return obstacles

    """ === publishing === """

    def _publish_riskenv(self, riskenv_vertices: list):
        stamp = self.get_clock().now().to_msg()

        msg = PolygonStamped()
        msg.header = Header(stamp=stamp, frame_id='odom')
        msg.polygon.points = [
            Point32(x=float(vertex[0]), y=float(vertex[1]), z=0.0)
            for vertex in riskenv_vertices
        ]
        self.riskenv_pub.publish(msg)

        self._publish_riskenv_marker(riskenv_vertices, stamp)

    def _publish_riskenv_marker(self, riskenv_vertices: list, stamp):
        """Republishes the risk envelope hull as a filled TRIANGLE_LIST plus
        a LINE_STRIP outline, so it's clearly visible in RViz next to the
        tactical layer's waypoint markers (tactical_node's
        waypoint_markers/virtual_waypoint_markers). Fan-triangulated from
        vertex 0, which only tiles a *convex* polygon correctly - safe here
        because create_unsafe_set returns a convex hull."""
        if len(riskenv_vertices) < 3:
            # nothing to draw (or too few vertices for a hull) - clear
            # whatever was there from the previous, non-empty envelope.
            clear = Marker()
            clear.header.frame_id = 'odom'
            clear.header.stamp = stamp
            clear.ns = 'riskenv'
            clear.action = Marker.DELETEALL
            self.riskenv_marker_pub.publish(MarkerArray(markers=[clear]))
            return

        points = [Point(x=float(v[0]), y=float(v[1]), z=0.0) for v in riskenv_vertices]

        fill = Marker()
        fill.header.frame_id = 'odom'
        fill.header.stamp = stamp
        fill.ns = 'riskenv'
        fill.id = 0
        fill.type = Marker.TRIANGLE_LIST
        fill.action = Marker.ADD
        fill.pose.orientation.w = 1.0
        fill.scale.x = fill.scale.y = fill.scale.z = 1.0  # ignored by TRIANGLE_LIST, must stay nonzero
        fill.color.r, fill.color.g, fill.color.b, fill.color.a = (1.0, 0.0, 0.0, 0.35)
        for i in range(1, len(points) - 1):
            fill.points.extend([points[0], points[i], points[i + 1]])

        outline = Marker()
        outline.header.frame_id = 'odom'
        outline.header.stamp = stamp
        outline.ns = 'riskenv'
        outline.id = 1
        outline.type = Marker.LINE_STRIP
        outline.action = Marker.ADD
        outline.pose.orientation.w = 1.0
        outline.scale.x = 0.15  # line width (m)
        outline.color.r, outline.color.g, outline.color.b, outline.color.a = (1.0, 0.0, 0.0, 0.9)
        outline.points = points + [points[0]]  # close the loop

        self.riskenv_marker_pub.publish(MarkerArray(markers=[fill, outline]))

    def _publish_maneuver_bias(self, maneuver: Maneuver):
        msg = ManeuverBias()
        msg.header = Header(stamp=self.get_clock().now().to_msg(), frame_id='odom')
        msg.side = maneuver.side
        msg.urgency = float(maneuver.urgency)
        msg.give_way = maneuver.give_way
        msg.encounter = maneuver.encounter.value
        msg.reason = maneuver.reason
        self.maneuver_bias_pub.publish(msg)


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
