#!/usr/bin/env python3
"""
fake_riskenv_publisher

Standalone demo/test node that stands in for `risk_envelope_node` when
there's no `/agent_state` + `/obstacles_state` source available (e.g. a bare
TurtleBot3 Gazebo sim). It publishes directly onto `/hybraut_nav/riskenv`
(the same `geometry_msgs/PolygonStamped` contract `tactical_node.py` already
subscribes to), so you can exercise the ColavAutomaton's discrete-mode
transitions (Cruise -> Transition_to_LOS -> Fallback -> Cruise) on demand,
without needing a real obstacle-detection pipeline.

Reacts to `tactical_node`'s `/hybraut_nav/tactical_node/automaton_state`
rather than blindly toggling on a fixed timer - a fixed toggle races the
agent's actual closing speed on the obstacle, so it's a coin flip whether
Transition_to_LOS gets any visible run time before the obstacle disappears
again. Instead it runs a small explicit cycle:
  - IDLE: no obstacle published. Waits `cooldown_period` seconds (a clean,
    guaranteed window to observe Cruise / Transition_to_LOS with no unsafe
    region in play) before placing the next one.
  - ACTIVE: a small square unsafe-region polygon is published `obstacle_offset`
    metres ahead of the agent's current heading (read from /odom). Clears
    back to IDLE as soon as `automaton_state` reports 'Fallback' (i.e.
    unsafe_conditions_guard actually fired), or after `max_active_duration`
    seconds as a safety net (e.g. if tactical_node isn't running/publishing
    that topic at all, so this doesn't hang forever).

NOTE: colav_automaton's default `safety_radius`/`acceptance_radius`/
`los_distance_threshold` are vessel-scale (metres in the tens). For a
TurtleBot3-scale demo, launch tactical_node with those overridden to
something sane for the room size, e.g.:
    ros2 run hybraut_nav tactical_node --ros-args \\
        -p safety_radius:=0.5 -p acceptance_radius:=0.3 -p los_distance_threshold:=3.0
"""

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from nav_msgs.msg import Odometry
from geometry_msgs.msg import PolygonStamped, Point32
from std_msgs.msg import Header, String

from hybraut_nav_utils import quaternion_to_heading

FALLBACK_STATE_NAME = 'Fallback'


class FakeRiskenvPublisher(Node):

    def __init__(self):
        super().__init__('fake_riskenv_publisher', namespace='hybraut_nav')

        self.declare_parameter(
            'tick_period',
            1.0,
            ParameterDescriptor(
                description='How often (s) to check whether to place/clear the fake '
                            'unsafe region. (default: 1.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'cooldown_period',
            5.0,
            ParameterDescriptor(
                description='Seconds to leave no unsafe region published after clearing '
                            '(and before the first one), giving Cruise/Transition_to_LOS a '
                            'guaranteed clean window. (default: 5.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'max_active_duration',
            25.0,
            ParameterDescriptor(
                description='Safety-net: force-clear the obstacle after this many seconds '
                            "even if 'Fallback' was never observed on automaton_state (e.g. "
                            'tactical_node not running). (default: 25.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'obstacle_offset',
            200.0,
            ParameterDescriptor(
                description='Distance (m) ahead of the agent, along its current heading, '
                            'to centre the fake obstacle - keep this well outside '
                            "tactical_node's safety_radius so it doesn't trip "
                            'unsafe_conditions_guard the instant it is placed. (default: 2.0)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'obstacle_halfwidth',
            100,
            ParameterDescriptor(
                description='Half-width (m) of the square fake obstacle polygon. '
                            '(default: 0.4)',
                type=ParameterType.PARAMETER_DOUBLE
            )
        )
        self.declare_parameter(
            'frame_id',
            'odom',
            ParameterDescriptor(
                description='frame_id stamped on the published polygon (cosmetic only - '
                            'tactical_node only reads the vertex list). (default: odom)',
                type=ParameterType.PARAMETER_STRING
            )
        )

        self._x = 0.0
        self._y = 0.0
        self._yaw = 0.0

        self._obstacle_active = False
        self._latest_automaton_state = None
        now = time.monotonic()
        self._obstacle_placed_time = now
        # start in IDLE, counting down cooldown_period before the first placement
        self._obstacle_cleared_time = now

        self._riskenv_pub = self.create_publisher(
            PolygonStamped,
            '/hybraut_nav/riskenv',
            qos_profile_system_default,
        )
        self._odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self._odom_cb,
            qos_profile_system_default,
        )
        self._automaton_state_sub = self.create_subscription(
            String,
            '/hybraut_nav/tactical_node/automaton_state',
            self._automaton_state_cb,
            qos_profile_system_default,
        )
        self._timer = self.create_timer(
            self.get_parameter('tick_period').value,
            self._tick_cb,
        )

        self.get_logger().info(
            'fake_riskenv_publisher up - will place a fake unsafe region ahead of the '
            'agent, clearing it once automaton_state reports Fallback (or after '
            f"{self.get_parameter('max_active_duration').value}s as a safety net)"
        )

    def _odom_cb(self, msg: Odometry):
        self._x = msg.pose.pose.position.x
        self._y = msg.pose.pose.position.y
        orientation = msg.pose.pose.orientation
        self._yaw = quaternion_to_heading(
            orientation.x, orientation.y, orientation.z, orientation.w
        )

    def _automaton_state_cb(self, msg: String):
        self._latest_automaton_state = msg.data

    def _tick_cb(self):
        now = time.monotonic()

        if self._obstacle_active:
            reached_fallback = self._latest_automaton_state == FALLBACK_STATE_NAME
            timed_out = (now - self._obstacle_placed_time) >= self.get_parameter('max_active_duration').value

            if reached_fallback or timed_out:
                reason = 'Fallback observed' if reached_fallback else 'max_active_duration reached'
                self._clear_obstacle(reason)
                self._obstacle_cleared_time = now
        else:
            if (now - self._obstacle_cleared_time) >= self.get_parameter('cooldown_period').value:
                self._place_obstacle()
                self._obstacle_placed_time = now

    def _place_obstacle(self):
        offset = self.get_parameter('obstacle_offset').value
        half = self.get_parameter('obstacle_halfwidth').value
        cx = self._x + offset * math.cos(self._yaw)
        cy = self._y + offset * math.sin(self._yaw)

        msg = PolygonStamped()
        msg.header = Header(
            stamp=self.get_clock().now().to_msg(),
            frame_id=self.get_parameter('frame_id').value,
        )
        msg.polygon.points = [
            Point32(x=cx - half, y=cy - half, z=0.0),
            Point32(x=cx + half, y=cy - half, z=0.0),
            Point32(x=cx + half, y=cy + half, z=0.0),
            Point32(x=cx - half, y=cy + half, z=0.0),
        ]
        self._riskenv_pub.publish(msg)
        self._obstacle_active = True
        self._latest_automaton_state = None
        self.get_logger().info(f'riskenv: placed fake unsafe region at ({cx:.2f}, {cy:.2f})')

    def _clear_obstacle(self, reason: str):
        msg = PolygonStamped()
        msg.header = Header(
            stamp=self.get_clock().now().to_msg(),
            frame_id=self.get_parameter('frame_id').value,
        )
        msg.polygon.points = []
        self._riskenv_pub.publish(msg)
        self._obstacle_active = False
        self.get_logger().info(f'riskenv: cleared unsafe region ({reason})')


def main(args=None):
    rclpy.init(args=args)
    node = FakeRiskenvPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
