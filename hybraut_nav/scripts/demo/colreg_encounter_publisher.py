#!/usr/bin/env python3
"""
colreg_encounter_publisher

Standalone demo node that cycles a live TurtleBot3 through the classic
COLREG encounter geometries - head-on (Rule 14), crossing as give-way and as
stand-on vessel (Rule 15), and overtaking in both directions (Rule 13) -
against a single virtual obstacle it simulates internally (no Gazebo mover,
bridges, or `/agent_state`/`/obstacles_state` source required).

Unlike `fake_riskenv_publisher` (a fixed square dropped ahead of the agent),
this drives the *real* `riskenv.create_unsafe_set()` geometry each tick from
the agent's live `/odom` and the virtual obstacle's own kinematics, and
republishes the resulting hull on `/hybraut_nav/riskenv` (the same
`geometry_msgs/PolygonStamped` contract `tactical_node.py` subscribes to) -
so the automaton's discrete-mode transitions are driven by genuine,
evolving unsafe sets rather than a synthetic placeholder.

Cycle, per encounter in `encounter_sequence`:
  - COOLDOWN: no obstacle published, for `cooldown_period` seconds - a clean
    window to observe Cruise/Transition_to_LOS with no unsafe region in play.
  - ENGAGED: the virtual obstacle is placed relative to a fixed anchor pose
    (`spawn_offset_distance` ahead of the agent's *start* pose - its pose at
    the first `/odom` message, not wherever it currently is) per the
    encounter's bearing/heading/speed, then integrated forward every tick;
    `riskenv.create_unsafe_set()` is recomputed each tick from the live agent
    + virtual obstacle and republished. Clears back to COOLDOWN as soon as
    `automaton_state` reports 'Fallback' (unsafe_conditions_guard fired), or
    after `engagement_duration` seconds as a safety net, then advances to the
    next encounter in sequence.

Also runs an `ExecuteMission` action client: once `tactical_node`'s
`execute_mission` server is up, it auto-sends one mission goal waypoint
`goal_behind_distance` past the encounter anchor (along the agent's start
heading), so the agent drives on its own through the whole staged encounter
zone for the life of the demo, without an operator having to
`ros2 action send_goal` it manually (set `send_goal_waypoint:=false` to
disable and drive the agent yourself instead).

Encounter geometries (agent-relative bearing, 0 = dead ahead, +ve = to port,
-ve = to starboard, matching REP103's x-forward/y-left body frame):
  - head_on:            obstacle ahead, reciprocal course, closing.
  - crossing_give_way:  obstacle on your starboard bow, closing - you are
                         the give-way vessel (Rule 15).
  - crossing_stand_on:  obstacle on your port bow, closing - you are the
                         stand-on vessel (Rule 15).
  - overtaking:         slower obstacle ahead, same course - you overtake it
                         (Rule 13).
  - being_overtaken:    faster obstacle astern, same course - it overtakes
                         you (Rule 13).

Every obstacle holds the straight-line course/speed computed once at
engagement start (its "encounter path") - it does not re-aim at the agent's
live position, so a genuine avoidance manoeuvre actually resolves the
encounter instead of the obstacle re-locking onto wherever the agent goes.

Publishes:
    /hybraut_nav/riskenv (geometry_msgs/PolygonStamped) - real unsafe-set
        hull, matching risk_envelope_node's contract.
    /hybraut_nav/riskenv_markers (visualization_msgs/MarkerArray) - filled +
        outlined hull, same style as risk_envelope_node.
    /hybraut_nav/colreg_encounter_markers (visualization_msgs/MarkerArray) -
        the virtual obstacle's body + a text label naming the active
        encounter, since there's no real Gazebo model to look at.

NOTE: matches the vessel-scale-vs-TB3-scale caveat in
docs/turtlebot3_demo.md - defaults below are TB3-room scale, not
`colav_automaton`'s vessel-scale defaults.
"""

import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType

from nav_msgs.msg import Odometry
from geometry_msgs.msg import PolygonStamped, Point32, Point
from std_msgs.msg import Header, String
from visualization_msgs.msg import Marker, MarkerArray

from riskenv import create_unsafe_set, Agent, Obstacle

from hybraut_nav_utils import quaternion_to_heading
from hybraut_nav.action import ExecuteMission
from hybraut_nav.msg import Waypoint

FALLBACK_STATE_NAME = 'Fallback'

# fixed, distinguishable colour per encounter type (RGB)
ENCOUNTER_COLORS = {
    'head_on': (0.9, 0.2, 0.2),
    'crossing_give_way': (0.95, 0.6, 0.1),
    'crossing_stand_on': (0.2, 0.6, 0.95),
    'overtaking': (0.6, 0.2, 0.9),
    'being_overtaken': (0.2, 0.85, 0.4),
}

ENCOUNTER_LABELS = {
    'head_on': 'HEAD-ON (Rule 14) - reciprocal course',
    'crossing_give_way': 'CROSSING (Rule 15) - obstacle to starboard, you give way',
    'crossing_stand_on': 'CROSSING (Rule 15) - obstacle to port, you stand on',
    'overtaking': 'OVERTAKING (Rule 13) - you overtake a slower obstacle ahead',
    'being_overtaken': 'OVERTAKING (Rule 13) - a faster obstacle overtakes you from astern',
}

DEFAULT_SEQUENCE = [
    'head_on',
    'crossing_give_way',
    'crossing_stand_on',
    'overtaking',
    'being_overtaken',
]


class ColregEncounterPublisher(Node):

    def __init__(self):
        super().__init__('colreg_encounter_publisher', namespace='hybraut_nav')

        self.declare_parameter(
            'encounter_sequence',
            DEFAULT_SEQUENCE,
            ParameterDescriptor(
                description='Ordered, repeating cycle of encounter types. Each must be one '
                            f'of {sorted(ENCOUNTER_LABELS)}. (default: {DEFAULT_SEQUENCE})',
                type=ParameterType.PARAMETER_STRING_ARRAY,
            )
        )
        self.declare_parameter(
            'tick_period', 0.2,
            ParameterDescriptor(description='Control-loop period (s): steps the virtual '
                                             'obstacle forward and recomputes/republishes the '
                                             'unsafe set. (default: 0.2)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'cooldown_period', 5.0,
            ParameterDescriptor(description='Seconds with no unsafe region published between '
                                             'encounters (and before the first one). '
                                             '(default: 5.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'engagement_duration', 40.0,
            ParameterDescriptor(description="Safety-net: force-clear an encounter after this "
                                             "many seconds even if 'Fallback' was never observed "
                                             '(e.g. tactical_node not running). (default: 40.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'clear_on_fallback', True,
            ParameterDescriptor(description="End an encounter as soon as automaton_state "
                                             "reports 'Fallback', rather than always running the "
                                             'full engagement_duration. (default: True)',
                                 type=ParameterType.PARAMETER_BOOL)
        )
        self.declare_parameter(
            'initial_range', 3.0,
            ParameterDescriptor(description='Range (m) from the agent at which the virtual '
                                             'obstacle is placed for head_on/crossing_*/'
                                             'being_overtaken. Keep well outside dsf so it '
                                             "doesn't trip unsafe_conditions_guard the instant "
                                             'it spawns. (default: 3.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'overtaking_range_scale', 1.6,
            ParameterDescriptor(description='Multiplier on initial_range for the overtaking '
                                             'obstacle (spawned further ahead, since the agent '
                                             'has to close the gap on speed differential alone). '
                                             '(default: 1.6)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'crossing_bearing_deg', 55.0,
            ParameterDescriptor(description='Bearing (deg, off dead-ahead) at which crossing '
                                             'obstacles are placed - within the classic 6-112.5 '
                                             'deg crossing sector. (default: 55.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'obstacle_speed', 0.3,
            ParameterDescriptor(description='Speed (m/s) for the closing encounters '
                                             '(head_on/crossing_*). (default: 0.3)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'overtaking_slow_speed', 0.12,
            ParameterDescriptor(description="Speed (m/s) of the obstacle in 'overtaking' - must "
                                             'stay below the agent\'s cruising speed or it never '
                                             'gets caught. (default: 0.12)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'overtaking_fast_speed', 0.45,
            ParameterDescriptor(description="Speed (m/s) of the obstacle in 'being_overtaken' - "
                                             "must exceed the agent's cruising speed or it never "
                                             'catches up. (default: 0.45)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'agent_safety_radius', 0.5,
            ParameterDescriptor(description="Agent safety radius (m) fed into riskenv - keep in "
                                             "sync with tactical_node's safety_radius param. "
                                             '(default: 0.5)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'obstacle_safety_radius', 0.35,
            ParameterDescriptor(description='Virtual obstacle safety radius (m) fed into '
                                             'riskenv. (default: 0.35)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'dsf', 2.5,
            ParameterDescriptor(description='Distance Safety Factor (m) - riskenv proximity '
                                             'threshold, TB3-room scale. (default: 2.5)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'time_of_interest', 15.0,
            ParameterDescriptor(description="Horizon (s) for riskenv's TCPA-based I3 filter. "
                                             '(default: 15.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'spawn_offset_distance', 2.0,
            ParameterDescriptor(description='Distance (m) ahead of the agent\'s *start* pose '
                                             '(captured on the first /odom message) at which '
                                             'every encounter is anchored - a fixed point, not '
                                             "the agent's live pose, so encounters stay staged "
                                             "in the same spot however far the agent has since "
                                             'driven. (default: 2.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'goal_behind_distance', 6.0,
            ParameterDescriptor(description='Extra distance (m) beyond spawn_offset_distance, '
                                             'along the start heading, at which the auto-sent '
                                             "execute_mission goal waypoint sits - i.e. behind "
                                             "the whole encounter zone, so driving toward it "
                                             "carries the agent through every encounter. Must "
                                             "clear the farthest obstacle spawn (overtaking's, "
                                             "initial_range * overtaking_range_scale past the "
                                             'anchor) with headroom or the agent stops short of '
                                             'it. (default: 6.0)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'goal_acceptance_radius', 0.3,
            ParameterDescriptor(description='acceptance_radius (m) stamped on the auto-sent '
                                             'goal waypoint - informational only, tactical_node '
                                             "uses its own fixed acceptance_radius param. "
                                             '(default: 0.3)',
                                 type=ParameterType.PARAMETER_DOUBLE)
        )
        self.declare_parameter(
            'send_goal_waypoint', True,
            ParameterDescriptor(description='Auto-send one execute_mission goal waypoint to '
                                             'tactical_node behind the encounter zone, so the '
                                             'agent keeps driving for the whole demo without an '
                                             'operator send-goaling it manually. Set False to '
                                             'drive the agent yourself instead. (default: True)',
                                 type=ParameterType.PARAMETER_BOOL)
        )
        self.declare_parameter(
            'frame_id', 'odom',
            ParameterDescriptor(description='frame_id stamped on published polygons/markers - '
                                             'cosmetic only, tactical_node only reads the vertex '
                                             'list. (default: odom)',
                                 type=ParameterType.PARAMETER_STRING)
        )

        sequence = [name for name in self.get_parameter('encounter_sequence').value if name]
        unknown = sorted(set(sequence) - set(ENCOUNTER_LABELS))
        if unknown:
            raise ValueError(
                f"encounter_sequence contains unknown encounter type(s) {unknown} - "
                f"must be one of {sorted(ENCOUNTER_LABELS)}"
            )
        if not sequence:
            raise ValueError("encounter_sequence must not be empty")
        self._sequence = sequence
        self._sequence_index = 0

        self._geometry_generators = {
            'head_on': self._geometry_head_on,
            'crossing_give_way': self._geometry_crossing_give_way,
            'crossing_stand_on': self._geometry_crossing_stand_on,
            'overtaking': self._geometry_overtaking,
            'being_overtaken': self._geometry_being_overtaken,
        }

        self._have_odom = False
        self._agent_x = 0.0
        self._agent_y = 0.0
        self._agent_heading = 0.0
        self._agent_speed = 0.0
        self._agent_yaw_rate = 0.0

        # agent's pose at the first /odom message - the fixed point every
        # encounter is anchored relative to (see spawn_offset_distance)
        self._start_captured = False
        self._start_x = 0.0
        self._start_y = 0.0
        self._start_heading = 0.0

        self._goal_waypoint_sent = False

        self._latest_automaton_state = None

        self._engaged = False
        self._current_type = None
        now = time.monotonic()
        self._phase_started_at = now  # counting down cooldown_period before the first encounter

        # virtual obstacle kinematic state, valid only while self._engaged
        self._obs_x = 0.0
        self._obs_y = 0.0
        self._obs_heading = 0.0
        self._obs_speed = 0.0

        self._riskenv_pub = self.create_publisher(
            PolygonStamped, '/hybraut_nav/riskenv', qos_profile_system_default,
        )
        self._riskenv_marker_pub = self.create_publisher(
            MarkerArray, '/hybraut_nav/riskenv_markers', qos_profile_system_default,
        )
        self._encounter_marker_pub = self.create_publisher(
            MarkerArray, '/hybraut_nav/colreg_encounter_markers', qos_profile_system_default,
        )

        self._goal_action_client = ActionClient(
            self, ExecuteMission, '/hybraut_nav/tactical_node/execute_mission',
        )

        self._odom_sub = self.create_subscription(
            Odometry, '/odom', self._odom_cb, qos_profile_system_default,
        )
        self._automaton_state_sub = self.create_subscription(
            String, '/hybraut_nav/tactical_node/automaton_state', self._automaton_state_cb,
            qos_profile_system_default,
        )
        self._timer = self.create_timer(self.get_parameter('tick_period').value, self._tick_cb)

        self.get_logger().info(
            f"colreg_encounter_publisher up - cycling {self._sequence} against the live agent, "
            f"real riskenv.create_unsafe_set() each tick"
        )

    """ === live agent state === """

    def _odom_cb(self, msg: Odometry):
        self._agent_x = msg.pose.pose.position.x
        self._agent_y = msg.pose.pose.position.y
        orientation = msg.pose.pose.orientation
        self._agent_heading = quaternion_to_heading(
            orientation.x, orientation.y, orientation.z, orientation.w
        )
        self._agent_speed = math.hypot(msg.twist.twist.linear.x, msg.twist.twist.linear.y)
        self._agent_yaw_rate = msg.twist.twist.angular.z
        self._have_odom = True

        if not self._start_captured:
            self._start_x = self._agent_x
            self._start_y = self._agent_y
            self._start_heading = self._agent_heading
            self._start_captured = True

    def _automaton_state_cb(self, msg: String):
        self._latest_automaton_state = msg.data

    """ === encounter geometry (called once, at engagement start) ===

    Each returns (obs_x, obs_y, obs_heading, obs_speed) given the agent's
    anchor pose (ax, ay, aheading) captured at that instant. obs_heading/
    obs_speed are held fixed for the rest of the engagement (see
    _step_engagement) - the obstacle travels its own straight-line encounter
    path, it does not re-aim at the agent's live position. """

    def _geometry_head_on(self, ax, ay, aheading):
        r = self.get_parameter('initial_range').value
        speed = self.get_parameter('obstacle_speed').value
        ox = ax + r * math.cos(aheading)
        oy = ay + r * math.sin(aheading)
        return ox, oy, aheading + math.pi, speed

    def _geometry_crossing_give_way(self, ax, ay, aheading):
        # obstacle on the agent's starboard (right) bow: negative bearing
        # offset in a x-forward/y-left body frame.
        r = self.get_parameter('initial_range').value
        speed = self.get_parameter('obstacle_speed').value
        bearing = aheading - math.radians(self.get_parameter('crossing_bearing_deg').value)
        ox = ax + r * math.cos(bearing)
        oy = ay + r * math.sin(bearing)
        return ox, oy, aheading + math.pi / 2.0, speed

    def _geometry_crossing_stand_on(self, ax, ay, aheading):
        # obstacle on the agent's port (left) bow: positive bearing offset.
        r = self.get_parameter('initial_range').value
        speed = self.get_parameter('obstacle_speed').value
        bearing = aheading + math.radians(self.get_parameter('crossing_bearing_deg').value)
        ox = ax + r * math.cos(bearing)
        oy = ay + r * math.sin(bearing)
        return ox, oy, aheading - math.pi / 2.0, speed

    def _geometry_overtaking(self, ax, ay, aheading):
        # slower obstacle ahead, same course - agent closes on it.
        r = self.get_parameter('initial_range').value * self.get_parameter('overtaking_range_scale').value
        speed = self.get_parameter('overtaking_slow_speed').value
        ox = ax + r * math.cos(aheading)
        oy = ay + r * math.sin(aheading)
        return ox, oy, aheading, speed

    def _geometry_being_overtaken(self, ax, ay, aheading):
        # faster obstacle astern, same course - it closes on the agent.
        r = self.get_parameter('initial_range').value
        speed = self.get_parameter('overtaking_fast_speed').value
        ox = ax + r * math.cos(aheading + math.pi)
        oy = ay + r * math.sin(aheading + math.pi)
        return ox, oy, aheading, speed

    """ === cycle state machine === """

    def _tick_cb(self):
        if not self._have_odom:
            return  # nothing to anchor an encounter to yet

        if not self._goal_waypoint_sent and self.get_parameter('send_goal_waypoint').value:
            self._try_send_goal_waypoint()

        now = time.monotonic()

        if not self._engaged:
            if (now - self._phase_started_at) >= self.get_parameter('cooldown_period').value:
                self._start_next_encounter()
            return

        self._step_engagement()

        reached_fallback = (
            self.get_parameter('clear_on_fallback').value
            and self._latest_automaton_state == FALLBACK_STATE_NAME
        )
        timed_out = (now - self._phase_started_at) >= self.get_parameter('engagement_duration').value

        if reached_fallback or timed_out:
            reason = 'Fallback observed' if reached_fallback else 'engagement_duration reached'
            self._end_encounter(reason)

    def _start_next_encounter(self):
        encounter_type = self._sequence[self._sequence_index]
        self._sequence_index = (self._sequence_index + 1) % len(self._sequence)

        offset = self.get_parameter('spawn_offset_distance').value
        ax = self._start_x + offset * math.cos(self._start_heading)
        ay = self._start_y + offset * math.sin(self._start_heading)
        aheading = self._start_heading
        ox, oy, oheading, ospeed = self._geometry_generators[encounter_type](ax, ay, aheading)

        self._current_type = encounter_type
        self._obs_x, self._obs_y = ox, oy
        self._obs_heading = oheading
        self._obs_speed = ospeed
        self._engaged = True
        self._latest_automaton_state = None
        self._phase_started_at = time.monotonic()

        self.get_logger().info(
            f"colreg encounter starting: {encounter_type} - {ENCOUNTER_LABELS[encounter_type]} "
            f"(obstacle spawned at ({ox:.2f}, {oy:.2f}))"
        )

    def _end_encounter(self, reason: str):
        self.get_logger().info(f"colreg encounter ending: {self._current_type} ({reason})")
        self._engaged = False
        self._current_type = None
        self._phase_started_at = time.monotonic()

        self._publish_riskenv([])
        self._publish_riskenv_markers([])
        self._publish_encounter_markers(None, 0.0, 0.0, 0.0)

    """ === auto-sent mission goal (drives the agent through the encounter zone) === """

    def _try_send_goal_waypoint(self):
        """One-shot, non-blocking: as soon as tactical_node's execute_mission
        server is up, send a mission goal behind the whole encounter zone
        (start pose + spawn_offset_distance + goal_behind_distance, along the
        start heading) so the agent drives continuously through it for the
        life of the demo - automates the manual `ros2 action send_goal` step
        from docs/turtlebot3_colreg_encounters_demo.md. Retried every tick
        (server_is_ready() is non-blocking) until accepted."""
        if not self._goal_action_client.server_is_ready():
            return

        distance = (
            self.get_parameter('spawn_offset_distance').value
            + self.get_parameter('goal_behind_distance').value
        )
        gx = self._start_x + distance * math.cos(self._start_heading)
        gy = self._start_y + distance * math.sin(self._start_heading)

        goal = ExecuteMission.Goal()
        goal.stamp = self.get_clock().now().to_msg()
        goal.mission_tag = 'colreg_encounter_publisher'
        goal.goal_waypoint = Waypoint(
            position=Point(x=gx, y=gy, z=0.0),
            acceptance_radius=self.get_parameter('goal_acceptance_radius').value,
        )

        self._goal_waypoint_sent = True  # set before sending: avoids a duplicate
                                          # send racing in from next tick while
                                          # send_goal_async is in flight
        self.get_logger().info(
            f"auto-sending execute_mission goal waypoint ({gx:.2f}, {gy:.2f}) - "
            f"behind the encounter zone, drives the agent through it"
        )
        future = self._goal_action_client.send_goal_async(goal)
        future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn(
                "tactical_node rejected the auto-sent execute_mission goal - "
                "drive the agent manually instead (see "
                "docs/turtlebot3_colreg_encounters_demo.md)"
            )
            self._goal_waypoint_sent = False  # allow a retry next tick
            return
        goal_handle.get_result_async().add_done_callback(self._on_goal_result)

    def _on_goal_result(self, future):
        result = future.result().result
        self.get_logger().info(
            f"execute_mission goal waypoint finished: success={result.success} "
            f"({result.message})"
        )

    def _step_engagement(self):
        # obs_heading/obs_speed were fixed once at engagement start (see the
        # _geometry_* generators) - the obstacle holds its own straight-line
        # encounter path, it never re-aims at the agent's live position.
        dt = self.get_parameter('tick_period').value

        self._obs_x += self._obs_speed * math.cos(self._obs_heading) * dt
        self._obs_y += self._obs_speed * math.sin(self._obs_heading) * dt

        agent = Agent(
            position=(self._agent_x, self._agent_y),
            heading=self._agent_heading,
            speed=self._agent_speed,
            yaw_rate=self._agent_yaw_rate,
            safety_radius=self.get_parameter('agent_safety_radius').value,
        )
        obstacle = Obstacle(
            position=(self._obs_x, self._obs_y),
            heading=self._obs_heading,
            speed=self._obs_speed,
            yaw_rate=0.0,
            safety_radius=self.get_parameter('obstacle_safety_radius').value,
            tag=self._current_type,
        )

        vertices = create_unsafe_set(
            agent=agent,
            obstacles=[obstacle],
            dsf=self.get_parameter('dsf').value,
            time_of_interest=self.get_parameter('time_of_interest').value,
        )

        self._publish_riskenv(vertices)
        self._publish_riskenv_markers(vertices)
        self._publish_encounter_markers(
            self._current_type, self._obs_x, self._obs_y, self._obs_heading
        )

    """ === publishing === """

    def _publish_riskenv(self, vertices: list):
        msg = PolygonStamped()
        msg.header = Header(
            stamp=self.get_clock().now().to_msg(),
            frame_id=self.get_parameter('frame_id').value,
        )
        msg.polygon.points = [
            Point32(x=float(v[0]), y=float(v[1]), z=0.0) for v in vertices
        ]
        self._riskenv_pub.publish(msg)

    def _publish_riskenv_markers(self, vertices: list):
        """Same filled TRIANGLE_LIST + LINE_STRIP outline style as
        risk_envelope_node._publish_riskenv_marker, so the hull looks
        identical in RViz whichever node is driving it. Fan-triangulated
        from vertex 0 - safe since create_unsafe_set returns a convex hull."""
        stamp = self.get_clock().now().to_msg()
        frame_id = self.get_parameter('frame_id').value

        if len(vertices) < 3:
            clear = Marker()
            clear.header.frame_id = frame_id
            clear.header.stamp = stamp
            clear.ns = 'riskenv'
            clear.action = Marker.DELETEALL
            self._riskenv_marker_pub.publish(MarkerArray(markers=[clear]))
            return

        points = [Point(x=float(v[0]), y=float(v[1]), z=0.0) for v in vertices]

        fill = Marker()
        fill.header.frame_id = frame_id
        fill.header.stamp = stamp
        fill.ns = 'riskenv'
        fill.id = 0
        fill.type = Marker.TRIANGLE_LIST
        fill.action = Marker.ADD
        fill.pose.orientation.w = 1.0
        fill.scale.x = fill.scale.y = fill.scale.z = 1.0
        fill.color.r, fill.color.g, fill.color.b, fill.color.a = (1.0, 0.0, 0.0, 0.35)
        for i in range(1, len(points) - 1):
            fill.points.extend([points[0], points[i], points[i + 1]])

        outline = Marker()
        outline.header.frame_id = frame_id
        outline.header.stamp = stamp
        outline.ns = 'riskenv'
        outline.id = 1
        outline.type = Marker.LINE_STRIP
        outline.action = Marker.ADD
        outline.pose.orientation.w = 1.0
        outline.scale.x = 0.15
        outline.color.r, outline.color.g, outline.color.b, outline.color.a = (1.0, 0.0, 0.0, 0.9)
        outline.points = points + [points[0]]

        self._riskenv_marker_pub.publish(MarkerArray(markers=[fill, outline]))

    def _publish_encounter_markers(self, encounter_type, ox: float, oy: float, oheading: float):
        """The virtual obstacle's body + a text label naming the active
        encounter - there's no real Gazebo model standing in for it."""
        stamp = self.get_clock().now().to_msg()
        frame_id = self.get_parameter('frame_id').value

        if encounter_type is None:
            clear = Marker()
            clear.header.frame_id = frame_id
            clear.header.stamp = stamp
            clear.ns = 'colreg_encounter'
            clear.action = Marker.DELETEALL
            self._encounter_marker_pub.publish(MarkerArray(markers=[clear]))
            return

        r, g, b = ENCOUNTER_COLORS[encounter_type]

        body = Marker()
        body.header.frame_id = frame_id
        body.header.stamp = stamp
        body.ns = 'colreg_encounter'
        body.id = 0
        body.type = Marker.CYLINDER
        body.action = Marker.ADD
        body.pose.position.x = ox
        body.pose.position.y = oy
        body.pose.position.z = 0.15
        body.scale.x = body.scale.y = 2.0 * self.get_parameter('obstacle_safety_radius').value
        body.scale.z = 0.3
        body.color.r, body.color.g, body.color.b, body.color.a = (r, g, b, 0.9)

        heading_arrow = Marker()
        heading_arrow.header.frame_id = frame_id
        heading_arrow.header.stamp = stamp
        heading_arrow.ns = 'colreg_encounter'
        heading_arrow.id = 1
        heading_arrow.type = Marker.ARROW
        heading_arrow.action = Marker.ADD
        heading_arrow.pose.position.x = ox
        heading_arrow.pose.position.y = oy
        heading_arrow.pose.position.z = 0.15
        heading_arrow.pose.orientation.z = math.sin(oheading / 2.0)
        heading_arrow.pose.orientation.w = math.cos(oheading / 2.0)
        heading_arrow.scale.x = 0.5
        heading_arrow.scale.y = 0.08
        heading_arrow.scale.z = 0.08
        heading_arrow.color.r, heading_arrow.color.g, heading_arrow.color.b, heading_arrow.color.a = (r, g, b, 1.0)

        label = Marker()
        label.header.frame_id = frame_id
        label.header.stamp = stamp
        label.ns = 'colreg_encounter'
        label.id = 2
        label.type = Marker.TEXT_VIEW_FACING
        label.action = Marker.ADD
        label.pose.position.x = ox
        label.pose.position.y = oy
        label.pose.position.z = 0.6
        label.scale.z = 0.3
        label.color.r, label.color.g, label.color.b, label.color.a = (1.0, 1.0, 1.0, 1.0)
        label.text = ENCOUNTER_LABELS[encounter_type]

        self._encounter_marker_pub.publish(MarkerArray(markers=[body, heading_arrow, label]))


def main(args=None):
    rclpy.init(args=args)
    node = ColregEncounterPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
