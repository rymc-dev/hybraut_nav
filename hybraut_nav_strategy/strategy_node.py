#!/usr/bin/env python3

"""
Layer one of the hybraut navigation stack: the global planner.

This node subscribes to global cost map updates and agent states. On a
`navigate_to_goal` action goal it plans a global path (A*) from the agent's
current position to the requested overall target, downsamples it into a
bounded list of intermediate waypoints, and
dispatches them to layer two (the local planner hybrid automaton) **one at
a time**, via `tactical_node`'s own `execute_mission` action
(`hybraut_nav/action/ExecuteMission`) - sending one leg, awaiting its
result, then sending the next, until the route is exhausted.

While a mission is active, this node also checks the agent's position
against the stored global plan at a slow frequency. If it has drifted past
a tolerance, it cancels whatever leg is currently in flight and replans
from the agent's current position to the same overall goal, discarding
whatever was left of the old route.

This node's own `navigate_to_goal` action streams feedback covering both
the live state of whichever leg is currently executing (relayed straight
from tactical_node's own feedback) and mission-level progress across the
whole route - the planned waypoint list, elapsed time since the mission
started, an estimated time remaining, and overall distance-based progress.

UML Reference:
    See state machine diagram: ./diagrams/strategy_node_state_machine.puml
    See class diagram: .diagrams/strategy_node_class_class_diagram.uml
"""

import os
import sys
import math
from enum import Enum
from typing import List, Optional, Tuple, Union

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, ActionClient, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration
from rclpy.timer import Timer
from rclpy.parameter import Parameter
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult

from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped
from hybraut_nav.msg import AgentState, Waypoint
from hybraut_nav.action import ExecuteMission, NavigateToGoal

# Import path planning modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hybraut_nav_strategy.path_planning import (
    Planner, Grid as PlannerGrid, Point as PlannerPoint,
    PlannerType, downsample_path, distance_to_path,
)

from hybraut_nav.qos import map_qos, world_state_qos
from hybraut_nav.state import NodeState


class _LegOutcome(Enum):
    """Internal only - how one dispatched tactical leg (_run_leg) resolved,
    for the mission drive loop (_execute_mission_cb) to act on."""
    REACHED = "reached"
    CANCELED_FOR_REPLAN = "canceled_for_replan"
    CANCELED_BY_USER = "canceled_by_user"
    FAILED = "failed"


class StrategyNode(Node):
    """
    Global planner for the Hybraut_nav navigation stack.

    Plans a global path relative to the agent's current state to a goal
    waypoint using A*, then dispatches it to the Tactical Layer (layer two)
    one waypoint at a time via that layer's own `execute_mission` action,
    replanning from scratch if the agent drifts too far off the stored
    route.

    This is Layer one of the HybrautNav navigation stack, generating optimal
    trajectories over the static cost map layer - a continuous representation
    of a 2D environment where each cell represents traversability cost.

    ROS Standard Cost Map cell state convention:
    - -1: Unknown
    - 0: Free
    - 1-99: Increasing cost of traversal
    - 100: Insurmountable obstacle

    Each waypoint handed to the Tactical Layer (layer 2, a hybrid automaton
    defined using 'AMDL' - Automaton Modeling Description Language) is run to
    completion as its own leg via `ExecuteMission` - tactical_node reports
    back (that action's result) once it actually reaches that target, at
    which point this node sends the next one. COLAV's own local-avoidance
    virtual waypoints are handled entirely inside the tactical layer and
    never surface here. The tactical layer's resulting continuous dynamics
    are tracked by a controller (layer 3).
    """

    # Parameter Defaults
    DEFAULT_PLANNER_TYPE: str = PlannerType.ASTAR.value  # DEFAULT planner type is A*
    DEFAULT_MAX_TACTICAL_WAYPOINTS: int = 8              # cap on legs dispatched per plan
    DEFAULT_PLAN_CHECK_FREQUENCY: float = 0.2            # Hz - deviation check every 5s
    DEFAULT_PATH_DEVIATION_TOLERANCE: float = 0.5        # metres off the global plan before replanning

    # World State Variables
    _map: Optional[PlannerGrid] = None            # latest cost map, converted for planning
    _start_point: Optional[PlannerPoint] = None    # latest agent position, converted for planning

    # Mission State Variables - all reset together in _clear_mission_state()
    _goal_waypoint: Optional[Waypoint] = None      # overall target of the active mission, if any
    _global_path: Optional[Path] = None            # full-resolution planned path, for deviation checks
    _route_waypoints: List[Waypoint] = None        # current downsampled route, dispatched one at a time
    _segment_lengths: List[float] = None           # per-leg length of _route_waypoints, for progress/ETA
    _current_waypoint_index: int = 0               # index into _route_waypoints of the leg now executing
    _mission_start_time = None                     # rclpy.time.Time - when the active mission's goal was accepted
    _active_mission_goal_handle = None              # ServerGoalHandle for the in-flight navigate_to_goal goal
    _tactical_goal_handle = None                    # ClientGoalHandle for the in-flight tactical leg, if any
    _replan_requested: bool = False                 # set by _plan_check_cb, consumed by _run_leg/_execute_mission_cb
    _cancel_sent_for_active_leg: bool = False       # guards against re-sending cancel_goal_async every feedback tick

    # Node State Variables
    _state: NodeState = NodeState.INACTIVE  # State of StrategyNode by default always INACTIVE
    _planner: Optional[Planner] = None      # planner class instance utilized for making path planning

    # publishers
    _plan_pub: Optional[Publisher] = None        # <<nav_msgs/msg/Path>> - downsampled dispatch route, for observability
    _goal_pose_pub: Optional[Publisher] = None   # <<geometry_msgs/msg/PoseStamped>>

    # subscriptions
    _map_sub: Optional[Subscription] = None    # <<nav_msgs/msg/OccupancyGrid>>
    _agent_sub: Optional[Subscription] = None  # <<hybraut_nav/msg/AgentState>>

    # Action server (this node's own interface) / client (into the tactical layer)
    _mission_action_server: Optional[ActionServer] = None   # <<hybraut_nav/action/NavigateToGoal>>
    _tactical_action_client: Optional[ActionClient] = None  # <<hybraut_nav/action/ExecuteMission>>

    # Timers
    _plan_check_timer: Optional[Timer] = None  # slow-frequency deviation check; not running until a mission starts

    """ === Node Initialization === """

    def __init__(self, *args, **kwargs):
        """
        Initializes the planner node, setting parameters for dynamic
        reconfiguration, the action server/client pair for driving a
        mission and the tactical layer respectively, subscriptions for
        world state updates required for planning, and publishers for
        planned paths and goal poses. Also sets up a timer for periodic
        deviation checking without starting it immediately.

        Args:
            *args: Variable length argument list for Node
            **kwargs: Arbitrary keyword arguments for Node
        Returns:
            None
        Raises:
            Exception: if any initialization step fails
        """
        super().__init__('strategy_node', namespace='hybraut_nav', *args, **kwargs)

        self._route_waypoints = []
        self._segment_lengths = []

        # Declare and initialize parameters
        self.__init_parameters__()

        # Initialize planner
        self.set_planner(self.get_parameter('planner').value)

        # Client into the tactical layer's execute_mission action
        self.__init_tactical_client__()

        # Setup parameter change callback
        self.add_on_set_parameters_callback(self._parameter_update_cb)

        # Setup subscriptions
        self.__init_subscriptions__()

        # Setup publishers
        self.__init_publishers__()

        # Setup timer
        self.__init_timer__()

        # This node's own action server - last, since a goal could in
        # principle arrive the moment it's created and everything above
        # needs to already be ready.
        self.__init_action_server__()

    def __init_parameters__(self):
        """
        Declares node parameters for dynamic reconfiguration
        of this planner node.

        Args:
            None

        Returns:
            None

        Raises:
            Exception: if parameters cannot be declared
        """
        self.declare_parameter(
            'planner',
            self.DEFAULT_PLANNER_TYPE,
            ParameterDescriptor(
                description='Type of global planner to use. '
                           'Options: A* '
                           f'(default: {self.DEFAULT_PLANNER_TYPE})'
            )
        )
        self.declare_parameter(
            'max_tactical_waypoints',
            self.DEFAULT_MAX_TACTICAL_WAYPOINTS,
            ParameterDescriptor(
                description='Maximum number of intermediate waypoints (legs) '
                           'dispatched to the tactical layer per plan. Must '
                           'stay comfortably below the tactical layer\'s '
                           'waypoint_buffer_len. '
                           f'(default: {self.DEFAULT_MAX_TACTICAL_WAYPOINTS})'
            )
        )
        self.declare_parameter(
            'plan_check_frequency',
            self.DEFAULT_PLAN_CHECK_FREQUENCY,
            ParameterDescriptor(
                description='Frequency (Hz) at which the agent\'s position is '
                           'checked against the stored global plan while a '
                           'mission is active. '
                           f'(default: {self.DEFAULT_PLAN_CHECK_FREQUENCY} Hz)'
            )
        )
        self.declare_parameter(
            'path_deviation_tolerance',
            self.DEFAULT_PATH_DEVIATION_TOLERANCE,
            ParameterDescriptor(
                description='Maximum distance (m) the agent may drift from '
                           'the stored global plan before a replan is '
                           'triggered. '
                           f'(default: {self.DEFAULT_PATH_DEVIATION_TOLERANCE} m)'
            )
        )
        self.declare_parameter(
            'description',
            self.__doc__ or "Global Planner Node for Hybraut Navigation Stack",
            ParameterDescriptor(
                description='Description of the planner node'
            )
        )

    def __init_tactical_client__(self):
        """
        Create the action client used to drive the tactical layer: handing
        it one waypoint at a time via `execute_mission`, one leg at a time,
        awaiting each leg's result before dispatching the next.

        Args:
            None
        Returns:
            None
        """
        self._tactical_action_client = ActionClient(
            self,
            ExecuteMission,
            '/hybraut_nav/tactical_node/execute_mission',
            callback_group=ReentrantCallbackGroup()
        )

    def __init_subscriptions__(self):
        """
        initializes topic subscriptions for world state updates required
        for path planning.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            lambda msg: self._map_rcv_cb(msg),
            map_qos,
            callback_group=ReentrantCallbackGroup()
        )

        self._agent_sub = self.create_subscription(
            AgentState,
            '/agent_state',
            lambda msg: self._agent_state_rcv_cb(msg),
            world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )

    def __init_publishers__(self):
        """
        Create topic publishers for the downsampled dispatch route (purely
        for observability - the tactical layer is fed one waypoint at a
        time via the execute_mission action, not via this topic) and goal
        poses.

        Args:
            None
        Returns:
            None
        Raises:
            Exception: if publishers cannot be created
        """
        self._plan_pub = self.create_publisher(
            Path,
            'planner/plan',
            qos_profile=world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )

        self._goal_pose_pub = self.create_publisher(
            PoseStamped,
            'planner/goal_pose',
            qos_profile=world_state_qos,
            callback_group=ReentrantCallbackGroup()
        )

    def __init_timer__(self):
        """
        Initialize the slow-frequency plan-deviation-check timer without
        starting it immediately - it only runs while a mission is active
        (started/stopped from _execute_mission_cb's drive loop).

        Args:
            None

        Returns:
            None

        Raises:
            Exception: if timer cannot be created
        """
        self._plan_check_timer = self.create_timer(
            1.0 / float(self.get_parameter('plan_check_frequency').value),
            self._plan_check_cb,
            autostart=False,
            callback_group=ReentrantCallbackGroup()
        )

    def __init_action_server__(self):
        """
        Create this node's own action server - one goal = one whole
        mission. Only one mission runs at a time (see _goal_cb).

        Args:
            None
        Returns:
            None
        """
        self._mission_action_server = ActionServer(
            self, NavigateToGoal, '/hybraut_nav/strategy_node/navigate_to_goal',
            execute_callback=self._execute_mission_cb,
            goal_callback=self._goal_cb,
            cancel_callback=self._cancel_cb,
            callback_group=ReentrantCallbackGroup()
        )

    """ === getters === """

    def get_planner_type(self) -> str:
        """
        getter for planner type as a string.

        Returns:
            str: Planner type as string

        Example:
            >> ptype = planner_node.get_planner_type()
            >> print(f"Current Planner Type: {ptype}")

        Test: tests/hybraut_nav_strategy/unit_tests/test_strategy_node:TestStrategy_node::test_get_planner_type
        """
        return str(self.get_parameter('planner').value)

    def get_description(self) -> str:
        """
        Getter for the description of the planner node.

        Returns:
            str: Description of the planner node
        """
        return str(self.get_parameter('description').value)

    def get_state(self) -> NodeState:
        """
        Getter for the current state of the planner."""
        return self._state

    """ === setters === """

    def set_planner(self, new_planner_type: Union[PlannerType, str], reset_replan_timer: Optional[bool] = False):
        """
        Setter for the planning algorithm type.

        Args:
            new_planner_type: PlannerType or str: Type of planner to set
            reset_replan_timer: bool: unused - kept for interface compatibility.

        example:
            >>> set_planner(PlannerType.ASTAR)
        Raises:
            ValueError: if planner type is not recognized
        """
        try:
            planner_type = (
                new_planner_type if isinstance(new_planner_type, PlannerType)
                else PlannerType.from_string(new_planner_type)
            )
            new_planner = PlannerType.initialize_planner(planner_type)
        except Exception as e:
            self.get_logger().error(f"Failed to set planner: {e}")
            raise

        self._planner = new_planner

    def set_state(self, state: NodeState):
        """Set the current state of the planner."""
        if not isinstance(state, NodeState):
            raise Exception("State must be an instance of NodeState Enum")
        self._state = state

    """ === helper functions === """

    def is_active(self) -> bool:
        """Check if planner is in active state."""
        return bool(self._state == NodeState.ACTIVE)

    def _validate_goal(self, goal_pose: PoseStamped) -> Tuple[bool, str]:
        """
        Validates an incoming goal pose against currently available world
        state (agent position, cost map bounds).

        Note: frame_id cross-checking against the cost map isn't possible
        here - self._map/self._start_point are already converted into
        planner-local types (PlannerGrid/PlannerPoint) by _map_rcv_cb /
        _agent_state_rcv_cb, which don't retain the original frame_id.
        """
        if self._start_point is None or self._map is None:
            return False, "Cannot set goal: missing world state data (agent pose or cost map)"
        if not isinstance(goal_pose, PoseStamped):
            return False, "Cannot set goal: invalid goal pose"

        origin_x, origin_y, _ = self._map.origin
        width_m = self._map.width * self._map.resolution
        height_m = self._map.height * self._map.resolution
        x, y = goal_pose.pose.position.x, goal_pose.pose.position.y
        if not (origin_x <= x <= origin_x + width_m) or not (origin_y <= y <= origin_y + height_m):
            return False, "Goal pose is out of cost map bounds"

        return True, ""

    def _plan(self, goal_pose: PoseStamped) -> Optional[Path]:
        """
        Plans a global path from the agent's current position to
        `goal_pose` using the currently configured planner.

        Returns:
            The dense nav_msgs/Path from the planner, or None if no path
            was found.
        """
        goal_pt = PlannerPoint.from_ros_msg(goal_pose)
        return self._planner.plan_path(self._map, self._start_point, goal_pt)

    """ === World State Callback Functions === """

    def _map_rcv_cb(self, msg: OccupancyGrid):
        """
        Callback for cost map updates.

        Args:
            msg: OccupancyGrid message representing the cost map

        Returns: None

        raises: Exception logger message if message is invalid
        """
        if not isinstance(msg, OccupancyGrid):
            self.get_logger().error("Received cost map is not of type OccupancyGrid")
            return
        if msg.info.width == 0 or msg.info.height == 0 or msg.info.resolution <= 0:
            self.get_logger().error("Received cost map has invalid dimensions or resolution")
            return
        if not msg.data or len(msg.data) != msg.info.width * msg.info.height:
            self.get_logger().error("Received cost map data size does not match grid dimensions")
            return

        self._map = PlannerGrid.from_ros_msg(msg)

    def _agent_state_rcv_cb(self, msg: AgentState):
        """Callback for agent state updates."""
        if not isinstance(msg, AgentState):
            self.get_logger().error("Received agent state is not of type AgentState")
            return

        current_agent_pose = PoseStamped(header=msg.header, pose=msg.pose)
        self._start_point = PlannerPoint.from_ros_msg(current_agent_pose)

    """ === navigate_to_goal action server === """

    def _goal_cb(self, goal_request) -> GoalResponse:
        """Only one mission runs at a time - reserves the active state
        immediately (rather than waiting for execute_callback to start) so
        a second goal arriving in that gap is still rejected, same pattern
        tactical_node uses for its own single-leg-at-a-time gate."""
        if self.is_active():
            self.get_logger().warning("Rejecting mission goal - a mission is already in progress.")
            return GoalResponse.REJECT
        self.set_state(NodeState.ACTIVE)
        return GoalResponse.ACCEPT

    def _cancel_cb(self, goal_handle) -> CancelResponse:
        """Always accept - the actual stop is driven from _run_leg/
        _on_tactical_feedback noticing is_cancel_requested and canceling
        whatever tactical leg is currently in flight."""
        return CancelResponse.ACCEPT

    async def _execute_mission_cb(self, goal_handle) -> NavigateToGoal.Result:
        """
        Drives one whole mission: plans a route to the goal, then dispatches
        it to the tactical layer one leg at a time until the route is
        exhausted, canceled, or fails - replanning in place if the agent
        drifts off the stored route mid-mission (see _plan_check_cb).

        This single coroutine is the only place that ever mutates route
        state (_route_waypoints/_segment_lengths/_current_waypoint_index) -
        _plan_check_cb only flags a replan and cancels the in-flight leg to
        interrupt it promptly, it never touches the route itself.
        """
        request = goal_handle.request
        self._mission_start_time = self.get_clock().now()
        self._active_mission_goal_handle = goal_handle
        self._tactical_goal_handle = None
        self._replan_requested = False
        self._cancel_sent_for_active_leg = False

        ok, message = await self._plan_and_set_route(request.goal_waypoint)
        if not ok:
            self.get_logger().warning(f"Mission rejected: {message}")
            goal_handle.abort()
            self._clear_mission_state()
            return NavigateToGoal.Result(success=False, message=message)

        self._start_plan_check_timer()

        while self._current_waypoint_index < len(self._route_waypoints):
            target = self._route_waypoints[self._current_waypoint_index]
            outcome, detail = await self._run_leg(target, request.mission_tag)

            if outcome is _LegOutcome.REACHED:
                self._current_waypoint_index += 1

            elif outcome is _LegOutcome.CANCELED_FOR_REPLAN:
                self.get_logger().info("Deviated from planned route - replanning")
                self._replan_requested = False
                ok, message = await self._plan_and_set_route(request.goal_waypoint)
                if not ok:
                    self.get_logger().error(f"Replan failed: {message}")
                    self._stop_plan_check_timer()
                    goal_handle.abort()
                    self._clear_mission_state()
                    return NavigateToGoal.Result(success=False, message=f"Replan failed: {message}")

            elif outcome is _LegOutcome.CANCELED_BY_USER:
                self._stop_plan_check_timer()
                goal_handle.canceled()
                self._clear_mission_state()
                return NavigateToGoal.Result(success=False, message="Mission canceled")

            else:  # FAILED
                self.get_logger().error(f"Leg failed: {detail}")
                self._stop_plan_check_timer()
                goal_handle.abort()
                self._clear_mission_state()
                return NavigateToGoal.Result(success=False, message=detail)

        self._stop_plan_check_timer()
        self.get_logger().info("Mission complete: reached final goal waypoint")
        goal_handle.succeed()
        duration = self.get_clock().now() - self._mission_start_time
        self._clear_mission_state()
        return NavigateToGoal.Result(
            success=True, message="Mission complete", total_mission_duration=duration.to_msg()
        )

    async def _run_leg(self, target: Waypoint, mission_tag: str) -> Tuple[_LegOutcome, str]:
        """
        Sends one waypoint to tactical_node's execute_mission action and
        awaits its result, mapping the outcome for _execute_mission_cb's
        drive loop. A genuine TERMINAL_REACHED success always wins even if
        a replan/cancel was also requested right around the same time -
        tactical_node's own result determination already gives a real
        success priority over a late-arriving cancel request, so this
        mirrors that here.
        """
        # a replan or cancel may already be pending from the gap between
        # the previous leg's result and this call - don't bother sending a
        # tactical goal we'd have to immediately cancel anyway.
        if self._replan_requested:
            return _LegOutcome.CANCELED_FOR_REPLAN, ""
        if self._active_mission_goal_handle is not None and self._active_mission_goal_handle.is_cancel_requested:
            return _LegOutcome.CANCELED_BY_USER, ""

        if not self._tactical_action_client.wait_for_server(timeout_sec=5.0):
            return _LegOutcome.FAILED, "tactical_node/execute_mission action server unavailable"

        goal = ExecuteMission.Goal()
        goal.stamp = self.get_clock().now().to_msg()
        goal.mission_tag = mission_tag
        goal.goal_waypoint = target
        self._cancel_sent_for_active_leg = False

        goal_handle = await self._tactical_action_client.send_goal_async(
            goal, feedback_callback=self._on_tactical_feedback
        )
        if not goal_handle.accepted:
            return _LegOutcome.FAILED, "tactical_node rejected the waypoint goal"

        self._tactical_goal_handle = goal_handle
        result_response = await goal_handle.get_result_async()
        self._tactical_goal_handle = None
        result = result_response.result

        if result.success:
            return _LegOutcome.REACHED, ""
        if self._replan_requested:
            return _LegOutcome.CANCELED_FOR_REPLAN, ""
        if self._active_mission_goal_handle is not None and self._active_mission_goal_handle.is_cancel_requested:
            return _LegOutcome.CANCELED_BY_USER, ""
        return _LegOutcome.FAILED, result.message or "tactical leg failed"

    def _on_tactical_feedback(self, feedback_msg):
        """
        Feedback callback for the currently in-flight tactical leg - fires
        at tactical_node's own continuous_dynamics_publish_rate cadence
        (default 50 Hz). Doubles as the cancel-detection heartbeat, the
        same "periodic tick also checks for a pending cancel" pattern
        tactical_node itself uses for its own cancel detection - here it's
        what actually cancels the tactical goal once either this node's own
        mission goal is canceled, or _plan_check_cb has flagged a replan.
        """
        if (self._tactical_goal_handle is not None
                and not self._cancel_sent_for_active_leg
                and (self._replan_requested
                     or (self._active_mission_goal_handle is not None
                         and self._active_mission_goal_handle.is_cancel_requested))):
            self._cancel_sent_for_active_leg = True
            self._tactical_goal_handle.cancel_goal_async()
            return

        self._publish_strategy_feedback(feedback_msg.feedback)

    def _publish_strategy_feedback(self, tactical_feedback: ExecuteMission.Feedback):
        """Builds and publishes this mission's own feedback: the relayed
        tactical fields plus mission-level progress computed fresh each
        tick from _segment_lengths/_current_waypoint_index."""
        if self._active_mission_goal_handle is None or not self._active_mission_goal_handle.is_active:
            return

        elapsed = self.get_clock().now() - self._mission_start_time
        elapsed_sec = elapsed.nanoseconds / 1e9

        completed = sum(self._segment_lengths[:self._current_waypoint_index])
        total = sum(self._segment_lengths)
        if total > 0:
            progress = completed / total
        elif self._route_waypoints:
            progress = self._current_waypoint_index / len(self._route_waypoints)
        else:
            progress = 0.0

        eta_sec = 0.0
        if completed > 0 and elapsed_sec > 0:
            avg_speed = completed / elapsed_sec
            if avg_speed > 0:
                eta_sec = max(0.0, (total - completed) / avg_speed)

        feedback = NavigateToGoal.Feedback()
        feedback.planned_waypoints = list(self._route_waypoints)
        feedback.current_waypoint_index = self._current_waypoint_index
        feedback.progress = progress
        feedback.elapsed_time = elapsed.to_msg()
        feedback.estimated_time_remaining = Duration(seconds=eta_sec).to_msg()
        feedback.tactical_automaton_state = tactical_feedback.automaton_state
        feedback.tactical_time_since_last_transition = tactical_feedback.time_since_last_transition
        feedback.current_position = tactical_feedback.current_position
        feedback.stamp = self.get_clock().now().to_msg()

        self._active_mission_goal_handle.publish_feedback(feedback)

    """ === planning / route management === """

    async def _plan_and_set_route(self, goal_waypoint: Waypoint) -> Tuple[bool, str]:
        """
        (Re)plans a global route from the agent's current position to
        goal_waypoint, downsamples it, and replaces _route_waypoints/
        _current_waypoint_index/_segment_lengths/_global_path with the
        result. Used both for the initial plan on mission start and for
        every replan mid-mission - a replan discards the previous route
        wholesale rather than splicing it, same as before.
        """
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.pose.position = goal_waypoint.position

        valid, message = self._validate_goal(goal_pose)
        if not valid:
            return False, message

        try:
            path = self._plan(goal_pose)
        except Exception as e:
            return False, f"Planning failed: {str(e)}"

        if path is None or len(path.poses) < 2:
            return False, "Planner found no valid path to goal"

        max_waypoints = int(self.get_parameter('max_tactical_waypoints').value)
        downsampled = downsample_path(path, max_waypoints)
        if not downsampled.poses:
            return False, "Downsampled plan produced no waypoints"

        self._goal_waypoint = goal_waypoint
        self._global_path = path
        self._route_waypoints = [
            Waypoint(position=pose.pose.position) for pose in downsampled.poses
        ]
        self._current_waypoint_index = 0
        self._segment_lengths = self._compute_segment_lengths()

        downsampled.header.stamp = self.get_clock().now().to_msg()
        self._plan_pub.publish(downsampled)
        self._goal_pose_pub.publish(goal_pose)

        return True, ""

    def _compute_segment_lengths(self) -> List[float]:
        """Euclidean length of each leg in _route_waypoints, in order,
        starting from the agent's position at (re)plan time - index-aligned
        with _route_waypoints, so segment_lengths[i] is the length of the
        leg ending at route_waypoints[i]. Used for _publish_strategy_feedback's
        distance-based progress/ETA."""
        if self._start_point is None or not self._route_waypoints:
            return []
        lengths = []
        prev_x, prev_y = self._start_point.x, self._start_point.y
        for wp in self._route_waypoints:
            x, y = wp.position.x, wp.position.y
            lengths.append(math.hypot(x - prev_x, y - prev_y))
            prev_x, prev_y = x, y
        return lengths

    def _clear_mission_state(self):
        self._goal_waypoint = None
        self._global_path = None
        self._route_waypoints = []
        self._segment_lengths = []
        self._current_waypoint_index = 0
        self._active_mission_goal_handle = None
        self._tactical_goal_handle = None
        self._mission_start_time = None
        self._replan_requested = False
        self._cancel_sent_for_active_leg = False
        self.set_state(NodeState.INACTIVE)

    """ === plan deviation / replan === """

    async def _plan_check_cb(self):
        """
        Slow-frequency timer: checks the agent's current position against
        the stored global plan and, if it's drifted past
        path_deviation_tolerance, flags a replan and cancels whatever
        tactical leg is currently in flight to interrupt it promptly. The
        actual replanning happens back in _execute_mission_cb's drive loop
        once that leg's cancellation comes back - not here, so there's only
        ever one place mutating route state (see its docstring).
        """
        if not self.is_active() or self._replan_requested:
            return
        if self._start_point is None or self._global_path is None or not self._global_path.poses:
            return

        deviation = distance_to_path(self._start_point, self._global_path)
        tolerance = float(self.get_parameter('path_deviation_tolerance').value)
        if deviation <= tolerance:
            return

        self.get_logger().warning(
            f"Deviation {deviation:.2f}m exceeds tolerance {tolerance:.2f}m - replanning"
        )
        self._replan_requested = True
        if self._tactical_goal_handle is not None and not self._cancel_sent_for_active_leg:
            self._cancel_sent_for_active_leg = True
            self._tactical_goal_handle.cancel_goal_async()

    def _start_plan_check_timer(self):
        if self._plan_check_timer.is_canceled():
            self._plan_check_timer.reset()

    def _stop_plan_check_timer(self):
        if not self._plan_check_timer.is_canceled():
            self._plan_check_timer.cancel()

    """ === dynamic configuration callback functions === """

    def _parameter_update_cb(self, params: List[Parameter]) -> SetParametersResult:
        """
        Handle dynamic parameter changes.

        Args:
            params: List of parameters that changed

        Returns:
            Result indicating success or failure
        """
        try:
            for param in params:
                if param.name == 'planner':
                    self.set_planner(param.value)
        except Exception as e:
            return SetParametersResult(successful=False, reason=str(e))

        return SetParametersResult(successful=True)


def main(args=None):
    from rclpy.executors import MultiThreadedExecutor

    rclpy.init(args=args)
    node = StrategyNode()
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
