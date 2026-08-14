# !/usr/bin/env python3
"""
Tactical Node for HybrautNav Navigation Stack is the second layer
responsible for tactical decision-making in navigation tasks.

It hosts a `colav_automaton.ColavAutomaton` (a `hybrid_automaton.Automaton`
definition) and drives it in real time:
    - odometry (`/odom`) is injected into the automaton's continuous state
      so guards/flows plan against the agent's real position/heading/speed.
    - the risk envelope (unsafe set) computed upstream by a risk_env-based
      ROS wrapper is subscribed to on `/hybraut_nav/riskenv` and pushed into
      the automaton's auxiliary state so COLAV guards (los_clear_to_waypoint,
      unsafe_conditions, safe_conditions) and the virtual-waypoint reset can
      route around it.
    - the automaton's resulting continuous state (the reference dynamics the
      active discrete mode's flow produces) is republished on
      `/hybraut_nav/continous_dynamics` for the immediate layer's controller
      to track, outputting yaw/velocity commands.

Interface: a plain `Node` (no ROS 2 lifecycle) with all parameters declared
once at construction from ROS args on startup. The automaton is driven one
waypoint ("leg") at a time via the `execute_mission` action server
(`hybraut_interfaces/action/ExecuteMission`) - a caller (`strategy_node`, or
a console operator via `ros2 action send_goal ... --feedback`) sends one
target, gets live feedback on the automaton's discrete state/transition
timing while the leg runs, and a result once it's reached, canceled, or
fails. Only one leg runs at a time - a goal sent while one is already
executing is rejected.
"""

import asyncio

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.duration import Duration
from rclpy.qos import qos_profile_system_default
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped, PolygonStamped, PoseStamped
from std_msgs.msg import Float64MultiArray, String
from visualization_msgs.msg import Marker, MarkerArray
from scipy.spatial.transform import Rotation as R

from colav_automaton import ColavAutomaton
from hybrid_automaton import Automaton, ContinuousState, AuxiliaryState, RunResult
from hybraut_interfaces.action import ExecuteMission

from hybraut_nav.qos import world_state_qos


class TacticalNode(Node):

    def __init__(self, node_name: str = 'tactical_node', namespace: str = 'hybraut_nav', **kwargs) -> None:
        super().__init__(node_name, namespace=namespace, **kwargs)

        self._declare_params()

        self._automaton: Automaton = ColavAutomaton(
            heading_tolerance=self.get_parameter('heading_tolerance').value,
            k_theta=self.get_parameter('k_theta').value,
            k_v=self.get_parameter('k_v').value,
            constant_velocity=self.get_parameter('constant_velocity').value,
            safety_radius=self.get_parameter('safety_radius').value,
            acceptance_radius=self.get_parameter('acceptance_radius').value,
            los_distance_threshold=self.get_parameter('los_distance_threshold').value,
            longitudinal_offset_distance=self.get_parameter('longitudinal_offset_distance').value,
            lateral_offset_distance=self.get_parameter('lateral_offset_distance').value
        )
        self._dt = self.get_parameter('dt').value
        self._sensor_update_rate = self.get_parameter('sensor_update_rate').value
        self._waypoint_buffer_len = self.get_parameter('waypoint_buffer_len').value
        self._waypoint_marker_scale = self.get_parameter('waypoint_marker_scale').value
        publish_rate = self.get_parameter('continuous_dynamics_publish_rate').value

        # live state - kept up to date for whichever leg is (or is about to
        # be) running.
        self._x = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self._riskenv_vertices = np.empty((0, 2))

        # handles into the running automaton's state objects - populated at
        # the start of each leg in _execute_leg_cb(). The runtime stores
        # these by reference (it does not copy them), so pushing into these
        # objects directly from ROS callbacks is enough to feed live data
        # into the automaton.
        self._continuous_state: ContinuousState = None
        self._waypoints_aux: AuxiliaryState = None
        # NOTE: this MUST stay named 'unsafe_region' - colav_automaton's
        # guards/resets (guards.py, resets.py) hardcode that key when
        # looking up ctx.auxiliary_states. Only the ROS-facing topic and
        # local variables/subscriptions are named 'riskenv'. Built once here
        # (not per-leg) - it only ever wraps self._riskenv_vertices, which
        # _riskenv_rcv() keeps current regardless of whether a leg is active.
        self._riskenv_aux: AuxiliaryState = AuxiliaryState(name='unsafe_region', aux0=self._riskenv_vertices.copy())

        # last-seen discrete state name, used to edge-detect automaton
        # transitions for _publish_automaton_state_if_changed (see note
        # there).
        self._last_automaton_state_name = None

        # goal handle for whichever leg is currently executing (None between
        # legs) - the publish timer below reads this to know where to send
        # feedback and whether a cancel has been requested. _leg_in_progress
        # is a separate flag set eagerly in _goal_cb() (before the goal
        # handle exists) so a second goal arriving in the gap between
        # goal_callback accepting and execute_callback actually starting
        # still gets rejected.
        self._active_goal_handle = None
        self._leg_in_progress = False

        self.__init_subscriptions__()
        self._continuous_dynamics_pub = self.create_publisher(
            Float64MultiArray,
            '/hybraut_nav/continous_dynamics',
            qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
        self._automaton_state_pub = self.create_publisher(
            String,
            '/hybraut_nav/tactical_node/automaton_state',
            qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
        self._automaton_transition_event_pub = self.create_publisher(
            String,
            '/hybraut_nav/tactical_node/automaton_transition_event',
            qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
        # PoseStamped mirror of /hybraut_nav/continous_dynamics (px, py,
        # theta only) purely so RViz - which has no native display for a
        # raw Float64MultiArray - can render the automaton's current
        # reference as an arrow.
        self._continuous_dynamics_pose_pub = self.create_publisher(
            PoseStamped,
            '/hybraut_nav/tactical_node/continous_dynamics_pose',
            world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )
        # current 'waypoints' auxiliary-state stack, split for RViz into the
        # real target (bottom of the stack, this leg's goal) and any
        # COLAV-generated virtual detour waypoints stacked on top of it
        # (colav_automaton's generate_new_virtual_waypoint/pop_virtual_waypoint
        # resets) - see _publish_waypoint_markers().
        self._waypoint_marker_pub = self.create_publisher(
            MarkerArray,
            '/hybraut_nav/tactical_node/waypoint_markers',
            world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )
        self._virtual_waypoint_marker_pub = self.create_publisher(
            MarkerArray,
            '/hybraut_nav/tactical_node/virtual_waypoint_markers',
            world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )

        # one action goal = one waypoint/leg. goal_callback rejects a new
        # goal while one is already executing (single automaton, single leg
        # at a time - mirrors the old queue-fed one-leg-at-a-time design,
        # just enforced by the action server instead of a manual queue).
        self._action_server = ActionServer(
            self, ExecuteMission, '/hybraut_nav/tactical_node/execute_mission',
            execute_callback=self._execute_leg_cb,
            goal_callback=self._goal_cb,
            cancel_callback=self._cancel_cb,
            callback_group=ReentrantCallbackGroup()
        )

        # created once, unconditionally - _publish_continuous_dynamics_cb
        # early-returns while no leg is active, so it's harmless to have it
        # running idle between legs. This is also what drives action
        # feedback and cancel-detection for whichever leg is active (see
        # _publish_leg_feedback/_check_cancel_requested).
        self._publish_timer = self.create_timer(
            1.0 / publish_rate,
            self._publish_continuous_dynamics_cb,
            callback_group=ReentrantCallbackGroup()
        )

    """ subscriptions """

    def __init_subscriptions__(self):
        self.odom_sub = self.create_subscription(
            msg_type=Odometry,
            topic='/odom',
            callback=lambda msg: self._odom_rcv(msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )
        self.base_link_sub=self.create_subscription(
            msg_type=TransformStamped,
            topic='/base_link',
            callback=lambda msg: print (msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )

        # TODO: continous_x state needs to be below
        # tf2_ros.Buffer().lookup_transform("odom", "base_link") # APPLYS ROTATION THEN TRANSLATION

        self.riskenv_sub = self.create_subscription(
            msg_type=PolygonStamped,
            topic='/hybraut_nav/riskenv',
            callback=lambda msg: self._riskenv_rcv(msg),
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )

    """ === action server: execute_mission (one waypoint/leg per goal) === """

    def _goal_cb(self, goal_request) -> GoalResponse:
        """Only one leg runs at a time - the automaton/continuous_state are
        single instances shared across the whole node. Reserves the slot
        immediately (rather than waiting for execute_callback to start) so a
        second goal arriving in that gap is still rejected."""
        if self._leg_in_progress:
            self.get_logger().warning("Rejecting waypoint goal - a leg is already executing.")
            return GoalResponse.REJECT
        self._leg_in_progress = True
        return GoalResponse.ACCEPT

    def _cancel_cb(self, goal_handle) -> CancelResponse:
        """Always accept - the actual stop is driven from the publish
        timer's cancel check (_check_cancel_requested) since that's what's
        running concurrently with the blocked automaton run in
        _execute_leg_cb (see module docstring / threading note there)."""
        return CancelResponse.ACCEPT

    def _execute_leg_cb(self, goal_handle) -> ExecuteMission.Result:
        """
        Runs the automaton for exactly one leg (one waypoint), blocking this
        call until that leg terminates - by reaching its target, being
        canceled, or failing/timing out.

        This runs on one of MultiThreadedExecutor's worker threads (see
        main()), not the thread any other callback runs on - that's what
        lets it block synchronously here for the whole leg duration without
        starving odometry/riskenv callbacks or the publish timer, which is
        exactly the guarantee the old lifecycle version got from spinning up
        its own dedicated threading.Thread. Cancellation and feedback are
        driven from the publish timer (a separate worker thread) reaching
        into self._automaton/self._active_goal_handle while this call is
        blocked inside run_until_complete() - the same cross-thread
        deactivate()-unblocks-run_until_complete() mechanism the old
        on_deactivate()/_activation_thread pair relied on.
        """
        target = np.array([
            goal_handle.request.goal_waypoint.position.x,
            goal_handle.request.goal_waypoint.position.y
        ])
        tag = goal_handle.request.mission_tag
        self.get_logger().info(
            f"Leg started toward ({target[0]:.2f}, {target[1]:.2f})" + (f" [{tag}]" if tag else "")
        )

        self._continuous_state = ContinuousState(
            name='agent_state',
            x0=self._x.copy(),
            x_labels=['x', 'y', 'theta', 'v', 'yaw_rate'],
        )
        self._waypoints_aux = AuxiliaryState(
            name='waypoints', aux0=target, aux_buffer_len=self._waypoint_buffer_len
        )
        self._last_automaton_state_name = None
        self._active_goal_handle = goal_handle

        loop = asyncio.new_event_loop()
        try:
            run_result: RunResult = loop.run_until_complete(self._automaton.activate(
                initial_continuous_state=self._continuous_state,
                initial_auxiliary_states=[self._waypoints_aux, self._riskenv_aux],
                enable_real_time_mode=True,
                enable_self_integration=True,
                delta_time=self._dt,
                continuous_state_provider=self._continuous_state_provider,
                continuous_state_provision_rate=max(1, round(1.0 / self._sensor_update_rate)),
                should_write_logs=True,
                output_dir=f"./log/hybrid_automaton/{self.get_clock().now().seconds_nanoseconds()}"
            ))
        except Exception as e:
            self.get_logger().error(f"Automaton leg run raised an exception: {e}")
            goal_handle.abort()
            return ExecuteMission.Result(success=False, message=f"Automaton leg run raised an exception: {e}")
        finally:
            loop.close()
            self._active_goal_handle = None
            self._leg_in_progress = False
            self._continuous_state = None
            self._waypoints_aux = None
            # no leg running anymore - clear any waypoint markers left over
            # in RViz from the leg that just stopped.
            self._clear_waypoint_markers()

        self.get_logger().info(run_result.summary())
        termination_code = run_result.termination_code.name if run_result.termination_code else None
        status = run_result.status.name if run_result.status else None

        if termination_code == 'TERMINAL_REACHED':
            goal_handle.succeed()
            return ExecuteMission.Result(success=True, message="Waypoint reached")
        if goal_handle.is_cancel_requested or termination_code == 'CANCELLED':
            goal_handle.canceled()
            return ExecuteMission.Result(success=False, message="Leg canceled")
        goal_handle.abort()
        return ExecuteMission.Result(
            success=False,
            message=run_result.termination_message or f"Leg failed ({status})"
        )

    """ === odometry callback ==="""
    def _odom_rcv(self, msg: Odometry):
        quat = np.array([msg.pose.pose.orientation.__getattribute__(attr) for attr in ['x', 'y', 'z', 'w']])
        eul = R.from_quat(quat).as_euler('xyz')  # radians
        yaw = eul[2]
        self._x = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            yaw,
            msg.twist.twist.linear.x,
            msg.twist.twist.angular.z
        ])

    """ === risk envelope (unsafe set) callback === """
    def _riskenv_rcv(self, msg: PolygonStamped):
        """
        Consumes the hull vertices of the risk envelope (unsafe set), as
        produced by `riskenv.create_unsafe_set`, and pushes them straight
        into the automaton's 'unsafe_region' auxiliary state so the COLAV
        guards/resets see the latest risk data on their next evaluation.
        """
        vertices = np.array([[p.x, p.y] for p in msg.polygon.points], dtype=float)
        self._riskenv_vertices = vertices
        if self._riskenv_aux is not None:
            self._riskenv_aux.add(vertices)

    """ === parameters === """

    def _declare_params(self):
        """Declares every parameter this node uses, once, at construction -
        no lifecycle configure step. Values are read via get_parameter(...)
        right after this call in __init__."""
        self.declare_parameter(
            'heading_tolerance',
            0.2,
            ParameterDescriptor(
                name='heading_tolerance',
                type=ParameterType.PARAMETER_DOUBLE,
                description='heading tolerance. '
                        'cfg for guards for colav_automaton '
                        f'(default: {0.2})'
            )
        )
        self.declare_parameter(
            'k_theta',
            1.0,
            ParameterDescriptor(
                name='k_theta',
                type=ParameterType.PARAMETER_DOUBLE,
                description='k_thate. '
                        'k_theta, control gains for theta controllers.'
                        f'(default: {1.0})'
            )
        )
        self.declare_parameter(
            'k_v',
            1.0,
            ParameterDescriptor(
                name='k_v',
                type=ParameterType.PARAMETER_DOUBLE,
                description='k_v. '
                        'control gains for velocity controllers. '
                        f'(default: {1.0})'
            )
        )
        self.declare_parameter(
            'constant_velocity',
            2.0,
            ParameterDescriptor(
                name='constant_velocity',
                type=ParameterType.PARAMETER_DOUBLE,
                description='constant_velocity. '
                        'constant_velocity for colav_automaton'
                        f'(default: {2.0})'
            )
        )
        self.declare_parameter(
            'safety_radius',
            30.0,
            ParameterDescriptor(
                name='safety_radius',
                type=ParameterType.PARAMETER_DOUBLE,
                description='safety_radius. '
                        'radius (m) of the agent safety circle colav_automaton '
                        'checks against the unsafe region for unsafe_conditions_guard/'
                        'safe_conditions_guard. Defaults to colav_automaton\'s own '
                        'vessel-scale default (30.0) - override this for smaller '
                        'platforms (e.g. ~0.3 for a TurtleBot3).'
                        f'(default: {30.0})'
            )
        )
        self.declare_parameter(
            'acceptance_radius',
            20.0,
            ParameterDescriptor(
                name='acceptance_radius',
                type=ParameterType.PARAMETER_DOUBLE,
                description='acceptance_radius'
                        'acceptance radius for waypoint reached guards in colav_automaton.'
                        f'(default: {20.0})'
            )
        )
        self.declare_parameter(
            'los_distance_threshold',
            200.0,
            ParameterDescriptor(
                name='los_distance_threshold',
                type=ParameterType.PARAMETER_DOUBLE,
                description='los_distance_threshold. '
                        'los_distance_threshold for colav_automaton guards.'
                        f'(default: {200.0})'
            )
        )
        self.declare_parameter(
            'longitudinal_offset_distance',
            100.0,
            ParameterDescriptor(
                name='longitudinal_offset_distance',
                type=ParameterType.PARAMETER_DOUBLE,
                description='longitudinal_offset_distance. '
                        'longitudinal_offset_distance for resets for colav_automaton '
                        f'(default: {100.0})'
            )
        )
        self.declare_parameter(
            'lateral_offset_distance',
            100.0,
            ParameterDescriptor(
                name='lateral_offset_distance',
                type=ParameterType.PARAMETER_DOUBLE,
                description='lateral_offset_distance. '
                        'lateral_offset_distance for resets for colav_automaton '
                        f'(default: {0.2})'
            )
        )
        self.declare_parameter(
            'dt',
            0.01,
            ParameterDescriptor(
                name='dt',
                type=ParameterType.PARAMETER_DOUBLE,
                description='dt. '
                        'delta time for evaluation steps. '
                        f'(default: {0.01})'
            )
        )
        self.declare_parameter(
            'sensor_update_rate',
            0.01,
            ParameterDescriptor(
                name='sensor_update_rate',
                type=ParameterType.PARAMETER_DOUBLE,
                description='sensor_update_rate. '
                        'period (seconds) at which live odometry is re-injected '
                        'into the automaton continuous state. '
                        f'(default: {0.01})'
            )
        )
        self.declare_parameter(
            'continuous_dynamics_publish_rate',
            50.0,
            ParameterDescriptor(
                name='continuous_dynamics_publish_rate',
                type=ParameterType.PARAMETER_DOUBLE,
                description='continuous_dynamics_publish_rate. '
                        'rate (Hz) at which the automaton continuous state is '
                        'republished on /hybraut_nav/continous_dynamics for the '
                        'immediate layer, and at which action feedback/cancel '
                        'are checked for the active leg. '
                        f'(default: {50.0})'
            )
        )
        self.declare_parameter(
            'waypoint_buffer_len',
            8,
            ParameterDescriptor(
                name='waypoint_buffer_len',
                type=ParameterType.PARAMETER_INTEGER,
                description='waypoint_buffer_len. '
                        'max length of the waypoints AuxiliaryState stack for a '
                        'single leg - one real target plus headroom for a few '
                        'COLAV virtual detours stacked on top of it within that '
                        'leg. Each leg only ever carries one real waypoint (the '
                        'active goal), so this can stay small. '
                        f'(default: {8})'
            )
        )
        self.declare_parameter(
            'waypoint_marker_scale',
            1.0,
            ParameterDescriptor(
                name='waypoint_marker_scale',
                type=ParameterType.PARAMETER_DOUBLE,
                description='waypoint_marker_scale. '
                        'diameter (m) of the RViz sphere markers published for the '
                        'real target waypoint and any virtual COLAV detour '
                        'waypoints on waypoint_markers/virtual_waypoint_markers - '
                        'scale to platform (e.g. ~0.3-0.5 for a TurtleBot3, larger '
                        'for vessel-scale colav_automaton deployments). '
                        f'(default: {1.0})'
            )
        )

    """ === injection / publishing functions === """

    def _continuous_state_provider(self, ctx) -> np.ndarray:
        """
        Poll-based provider for the automaton runtime: periodically
        re-injects the agent's real (odometry-derived) position so
        position-based guards (waypoint_reached, unsafe_conditions,
        los_clear_to_waypoint) stay anchored to reality rather than drifting
        purely off the integrated reference dynamics.

        Deliberately preserves theta/v/yaw_rate from the automaton's own
        current continuous_state instead of also overwriting them with raw
        odometry. `ctx.continuous_state` doubles as both the guards' input
        AND the reference trajectory this node publishes on
        /hybraut_nav/continous_dynamics for the immediate layer's controller
        to track - flow_los_heading's theta_dot = k_theta * e_theta only
        ever gets one integration step (dt) to nudge theta before this
        provider runs again (same ~10ms cadence as dt). Overwriting theta
        with real, barely-moving odometry every cycle stomped that
        correction back to "wherever the robot already is" before it could
        accumulate - the reference heading could never diverge from the
        agent's current heading, so the immediate layer's controller saw a
        near-zero heading error and the robot never actually turned.
        Splicing in only real (x, y) keeps guards honest about true position
        while letting the active mode's flow own theta/v/yaw_rate, as a
        guidance (reference) layer should - immediate_node's own controller
        already closes the loop against real /odom heading separately.
        """
        reference = ctx.continuous_state.latest()
        merged = self._x.copy()
        merged[2:5] = reference[2:5]  # theta, v, yaw_rate stay reference-owned
        return merged

    def _publish_continuous_dynamics_cb(self):
        """Publishes the automaton's current continuous state (the reference
        dynamics for the immediate layer's controller to track) at a fixed
        rate. Also polls/publishes the automaton's current discrete state -
        see _publish_automaton_state_if_changed() - and, while a leg is
        active, drives that leg's action feedback and cancel-detection."""
        if self._continuous_state is None:
            return

        data = self._continuous_state.latest().tolist()
        msg = Float64MultiArray()
        msg.data = data
        self._continuous_dynamics_pub.publish(msg)

        self._publish_continuous_dynamics_pose(data)
        self._publish_automaton_state_if_changed()
        self._publish_waypoint_markers()
        self._check_cancel_requested()
        self._publish_leg_feedback(data)

    def _check_cancel_requested(self):
        """Runs on the publish timer's worker thread, concurrently with
        _execute_leg_cb's thread blocked inside run_until_complete() for the
        active leg - calling deactivate() here is what unblocks it, the same
        cross-thread mechanism the old on_deactivate()/_activation_thread
        pair relied on."""
        if (self._active_goal_handle is not None
                and self._active_goal_handle.is_cancel_requested
                and self._automaton is not None):
            self._automaton.deactivate()

    def _publish_leg_feedback(self, data: list):
        """Publishes ExecuteMission action feedback for whichever leg is
        currently executing - automaton discrete state, time since its last
        transition, transition count, and live reference position."""
        if self._active_goal_handle is None or not self._active_goal_handle.is_active:
            return

        feedback = ExecuteMission.Feedback()
        feedback.automaton_state = self._get_current_automaton_state_name() or ""
        elapsed, transitions_count = self._get_automaton_runtime_stats()
        if elapsed is not None:
            feedback.time_since_last_transition = Duration(seconds=elapsed).to_msg()
        feedback.transitions_count = transitions_count or 0
        feedback.current_position.x = float(data[0])
        feedback.current_position.y = float(data[1])
        feedback.stamp = self.get_clock().now().to_msg()
        self._active_goal_handle.publish_feedback(feedback)

    def _publish_continuous_dynamics_pose(self, data: list):
        """Publishes the automaton's current reference (px, py, theta) as a
        PoseStamped purely so RViz - which has no native display for a raw
        Float64MultiArray - can render it as an arrow next to /cmd_vel."""
        qx, qy, qz, qw = R.from_euler('z', data[2]).as_quat()
        pose = PoseStamped()
        pose.header.frame_id = 'odom'  # px/py are odom-frame, from /odom
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = float(data[0])
        pose.pose.position.y = float(data[1])
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw
        self._continuous_dynamics_pose_pub.publish(pose)

    def _publish_waypoint_markers(self):
        """Splits the automaton's live 'waypoints' auxiliary-state stack
        into RViz markers on two topics: the real target (the bottom/oldest
        entry - this leg's goal, never popped) on waypoint_markers, and any
        COLAV-generated virtual detour waypoints stacked on top of it by
        colav_automaton's generate_new_virtual_waypoint/pop_virtual_waypoint
        resets - see colav_automaton/resets/resets.py - on
        virtual_waypoint_markers. AuxiliaryState.add() appendleft()s, so
        buffer[0] is the newest (topmost/active) entry and buffer[-1] is the
        real target.
        """
        if self._waypoints_aux is None:
            return

        stack = list(self._waypoints_aux.get_aux_buffer())
        if not stack:
            return

        stamp = self.get_clock().now().to_msg()
        scale = self._waypoint_marker_scale
        real_waypoint, virtual_waypoints = stack[-1], stack[:-1]

        self._waypoint_marker_pub.publish(MarkerArray(markers=[
            self._make_waypoint_marker(
                real_waypoint, marker_id=0, stamp=stamp, ns='real_waypoint',
                scale=scale, color=(0.0, 1.0, 0.0, 1.0)
            )
        ]))

        if virtual_waypoints:
            markers = [
                self._make_waypoint_marker(
                    waypoint, marker_id=i, stamp=stamp, ns='virtual_waypoints',
                    scale=scale, color=(1.0, 0.55, 0.0, 1.0)
                )
                for i, waypoint in enumerate(virtual_waypoints)
            ]
        else:
            # nothing currently detouring - clear any virtual markers left
            # over from a detour that has since been popped/resolved.
            markers = [self._make_delete_all_marker(stamp, ns='virtual_waypoints')]
        self._virtual_waypoint_marker_pub.publish(MarkerArray(markers=markers))

    def _make_waypoint_marker(self, waypoint, marker_id: int, stamp, ns: str, scale: float, color: tuple) -> Marker:
        """Builds a single SPHERE marker for one (x, y) waypoint. Waypoints
        live in odom-frame coordinates (matching the goal's target) - there's
        no map->odom TF without a localization source running, so stamping
        'map' here left these invisible in RViz."""
        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = stamp
        marker.ns = ns
        marker.id = marker_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = float(waypoint[0])
        marker.pose.position.y = float(waypoint[1])
        marker.pose.orientation.w = 1.0
        marker.scale.x = marker.scale.y = marker.scale.z = scale
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
        return marker

    def _make_delete_all_marker(self, stamp, ns: str) -> Marker:
        marker = Marker()
        marker.header.frame_id = 'odom'
        marker.header.stamp = stamp
        marker.ns = ns
        marker.action = Marker.DELETEALL
        return marker

    def _clear_waypoint_markers(self):
        """Publishes DELETEALL on both waypoint marker topics - called once
        a leg stops so a finished leg's markers don't linger in RViz."""
        stamp = self.get_clock().now().to_msg()
        self._waypoint_marker_pub.publish(MarkerArray(
            markers=[self._make_delete_all_marker(stamp, ns='real_waypoint')]
        ))
        self._virtual_waypoint_marker_pub.publish(MarkerArray(
            markers=[self._make_delete_all_marker(stamp, ns='virtual_waypoints')]
        ))

    def _get_current_automaton_state_name(self):
        """
        Best-effort read of the automaton's live discrete state name.

        `hybrid_automaton.Automaton` has no public API for this - `activate()`
        only resolves to a final `RunResult` once the whole run ends, and
        there's no per-transition callback to hook into. The only place the
        live discrete state is tracked is `Automaton._runtime._ctx` (private -
        `Automaton.deactivate()` itself reaches into the very same attribute
        internally). Reads a str/None; never raises, so a private-API
        shape change in a future `hybrid_automaton` release degrades to
        "no live state" rather than crashing the node.
        """
        try:
            return self._automaton._runtime._ctx.discrete_state.name
        except AttributeError:
            return None

    def _get_automaton_runtime_stats(self):
        """
        Best-effort read of the automaton's live transition-timing stats,
        for action feedback - same private-API caveat as
        _get_current_automaton_state_name() above (same `_runtime._ctx`
        attribute chain, wrapped the same way so a shape change degrades to
        "no stats" rather than crashing the node).

        Returns (time_since_last_transition_sec, transitions_count), both
        None if unavailable.
        """
        try:
            ctx = self._automaton._runtime._ctx
            return ctx.clock.get_time_elapsed_since_transition(), ctx.transitions_count
        except AttributeError:
            return None, None

    def _publish_automaton_state_if_changed(self):
        """Edge-triggered publish of the automaton's current discrete state
        (Cruise / Transition_to_LOS / Fallback / Waypoint_Reached) on
        `/hybraut_nav/tactical_node/automaton_state`, and mirrors the same
        transition to the ROS logger - so both are visible without having to
        go dig up the hybrid_automaton runtime's own temporal log file."""
        current_name = self._get_current_automaton_state_name()
        if current_name is None or current_name == self._last_automaton_state_name:
            return

        transition_msg = f"'{self._last_automaton_state_name}' -> '{current_name}'"
        self.get_logger().info(f"automaton transition: {transition_msg}")
        self._automaton_state_pub.publish(String(data=current_name))
        self._automaton_transition_event_pub.publish(String(data=transition_msg))

        self._last_automaton_state_name = current_name


def main(args=None):
    rclpy.init(args=args)
    node = TacticalNode()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
