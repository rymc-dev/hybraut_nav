# import importlib
# import logging
# from dataclasses import dataclass, field
# from typing import Any, Dict, List, Optional, Type
# import yaml

# from nodes.guards import GuardABC
# from nodes.resets import ResetABC
# from nodes.invariants import InvariantABC
# from nodes.dynamics import DynamicsABC
# from rclpy.publisher import Publisher
# from rclpy.node import Node
# from rclpy.qos import QoSProfile
# from rclpy.callback_groups import ReentrantCallbackGroup, CallbackGroup
# from automaton_interfaces.msg import AutomatonModeState, AutomatonMode, AutomatonEvents
# from nodes._internal.callbacks.mode_callback import on_mode_callback
# from nodes._internal.callbacks.invariant_callback import invariant_enforcer_callback
# from nodes._internal.callbacks.transition_callback import transition_evaluation_callback
# from nodes._internal.callbacks.dynamic_callbacks import dynamics_evaluation_callback
# import threading
# from rclpy.timer import Timer
# from rclpy.subscription import Subscription
# from nodes._internal.automaton.watchdog.watchdog_fsm import WatchdogFSM

# # Set up module logger
# type Logger = logging.Logger
# logger: Logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# DEFAULT_QOS = QoSProfile(depth=10)
# DEFAULT_CALLBACK_GROUP = ReentrantCallbackGroup()




# @dataclass
# class State:
#     """
#     State is a blueprint for an instance of 
#     a hybrid automaton state as defined in the
#     Hybrid Automaton Famd, State has functionality 
#     for switching it on and off, actionition and deactionation
#     on activate state subscriptions and state publishers and enabled 
#     for a node passed in, deactivate simply frees up those resources
#     """
#     _name: str
#     _topic: str
#     _msg_type: Any
#     _current_state: Any
#     _state_publisher: Publisher 
#     _state_subscription: Subscription
#     _update_hz: int
#     _timeout_sec: float
#     _is_activated: bool = False

#     def activate_state(self, node: Node, qos_profile: QoSProfile, callback_group: CallbackGroup) -> bool:
#         if self._is_activated:
#             raise RuntimeWarning("can't activate state because it is already active.")

#         self._create_state_publisher(node, qos_profile=qos_profile, callback_group=callback_group)
#         self._create_state_subscription(node, qos_profile=qos_profile, callback_group=callback_group)
#         self._is_activated = True
#         return True

#     def deactivate_state(self, node: Node) -> bool:
#         if not self._is_activated:
#             raise RuntimeWarning("can't deactivate state as it is not currently active")
        
#         node.destroy_subscription(self._state_subscription)
#         node.destroy_publisher(self._state_publisher)
#         return True

#     def _update_state(self, state_msg: Any) -> None:
#         """Update the current runtime state."""
#         if not self._is_activated:
#             raise RuntimeWarning("can't publish a state update if state is not active")

#         if not isinstance(state_msg, self._msg_type):
#             raise TypeError(f"Expected message of type {self._msg_type}, got {type(state_msg)}")
        
#         self._current_state = state_msg

#     def _publish_state(self, state_msg: Any) -> None:
#         if not self._is_activated:
#             raise RuntimeWarning("can't publish a state update if state is not active")

#         if not isinstance(state_msg, self._msg_type):
#             raise TypeError(f"Expected message of type {self._msg_type}, got {type(state_msg)}")
        
#         if self._state_publisher:
#             self._state_publisher.publish(state_msg)
#         else:
#             raise RuntimeError('attempted to published, however state published is not activated')

#     def _create_state_publisher(self, node: Node, qos_profile: QoSProfile, callback_group: CallbackGroup):
#         self._state_publisher = node.create_publisher(
#             msg_type=self._msg_type,
#             topic=self._topic,
#             qos_profile=qos_profile,
#             callback_group=callback_group
#         )

#     def _create_state_subscription(self, node: Node, qos_profile: QoSProfile, callback_group: CallbackGroup):
#         """create state subscription for this state"""
#         self._state_subscription = node.create_subscription(
#             msg_type=self._msg_type,
#             topic=self._topic,
#             callback=lambda msg: self._update_state(msg),
#             qos_profile=qos_profile,
#             callback_group=callback_group
#         )
    
#     def __str__(self):
#         pass
    
#     @classmethod
#     def load_state_from_famd(cls, state_data: Dict[str, Any]) -> "State":
#         pkg = state_data['type']['pkg']
#         msg = state_data['type']['msg']
#         msg_cls = import_class(pkg, msg)  # import_class should return a type/class
#         return cls(
#             _name=state_data.get('name', ''),
#             _topic=state_data.get('topic', ''),
#             _msg_type=msg_cls,
#             _update_hz=state_data.get('params', {}).get('update_hz', -1.0),
#             _timeout_sec=state_data.get('params', {}).get('timeout_sec', -1.0),
#         )









# @dataclass
# class Mode:
#     name: str
#     description: str
#     dynamics: DynamicsABC
#     invariants: List[InvariantABC]
#     transitions: List[Transition]

#     @classmethod
#     def from_famd(cls, data: Dict[str, Any], famd: Dict[str, Any]) -> "Mode":
#         dynamics = DynamicsWrapper.from_famd(
#             famd['dynamics'][data['dynamics']]
#         )
#         invariants = [
#             InvariantWrapper.from_famd(famd['invariants'][k])
#             for k in data.get('invariants', [])
#         ]
#         transitions = []
#         for t in data.get('transitions', []):
#             name, details = next(iter(t.items()))
#             # attach priority from inline details
#             famd['transitions'][name]['priority'] = details.get('priority', 0)
#             transitions.append(
#                 Transition.from_famd(
#                     name,
#                     famd['transitions'][name],
#                     famd.get('guards', {}),
#                     famd.get('resets', {}),
#                 )
#             )
#         return cls(
#             name=data.get('name', ''),
#             description=data.get('description', ''),
#             dynamics=dynamics,
#             invariants=invariants,
#             transitions=sorted(transitions, key=lambda tr: tr.priority),
#         )

# @dataclass
# class HybridAutomaton:
#     name: str
#     description: str
#     states: Dict[str, State]
#     modes: Dict[int, Mode]
#     initial_mode: int
#     goal_modes: List[int]

#     transition_evaluation_frequency_hz: float
#     control_frequency_hz: float

#     _current_mode: int

#     _watchdog_fsm: WatchdogFSM
#     _mode_publisher: Publisher
#     _event_publisher: Publisher
#     _transition_evaluation_publisher: Publisher
#     _dynamic_evaluation_publisher: Publisher
#     _invariants_evaluation_publisher: Publisher

#     _transition_evaluator: Timer
#     _dynamic_evaluator: Timer
#     _invariant_evaluator: Timer

#     def activate_automaton(self, waypoint: Waypoint)

#     def _set_mode(self, new_mode_id: int) -> bool:
#         try:
#             mode_idx = new_mode_id
#             if mode_idx not in self.modes.keys():
#                 raise ValueError(f"invalid mode idx received: {mode_idx}, available mode idx are: {self.modes.keys()}.")
#             self.current_mode = mode_idx
#             return True
#         except Exception as e:
#             raise Exception(f"exception occured during 'HybridAutomaton.update_mode': {str(e)}")
        
#     def _get_mode(self) -> int:
#         return self.current_mode
    
#     def _create_mode_publisher(self, node: Node, qos_profile = DEFAULT_QOS, callback_group=DEFAULT_CALLBACK_GROUP) -> None:
#         """create the mode subscription for the automaton"""
#         node.create_publisher(
#           msg_type=AutomatonModeState,
#           topic='/automaton/mode',
#           qos_profile=qos_profile,
#           callback_group=callback_group
#         )

#     def _create_mode_subscription(self, node: Node, event_publisher: Publisher, qos_profile = DEFAULT_QOS, callback_group=DEFAULT_CALLBACK_GROUP):
#         """
#         creates a subscription to the hybrid automaton mode
#         """
#         node.create_subscription(
#                 AutomatonMode,
#                 '/automaton/mode',
#                 callback=lambda msg: on_mode_callback(
#                     lock=threading.Lock,
#                     rcv_mode_state_msg=msg,
#                     automaton_model=self,
#                     event_publisher=event_publisher
#                 ),
#                 qos_profile=qos_profile,
#                 callback_group=callback_group
#             )
        
#     def _create_event_publisher(self, node: Node, qos_profile = DEFAULT_QOS, callback_group = DEFAULT_CALLBACK_GROUP):
#         """
#         creates the event publisher which is utilized for viewing events for the hybrid automaton in real time.
#         """
#         node.create_publisher(
#             msg_type=AutomatonEvents,
#             topic='/automaton/events',
#             qos_profile=qos_profile,
#             callback_group=callback_group
#         )
    
#     def _start_automaton_watchdog(self, node: Node, qos_profile = DEFAULT_QOS, callback_group = DEFAULT_CALLBACK_GROUP):
#         """this starts the automaton watchdog"""
        
#         self._watchdog = WatchdogFSM(
#           self.status_publisher,
#           logger=self.get_logger()
#         )

#     def _create_state_subscriptions(self, node: Node, qos_profile = DEFAULT_QOS, callback_group = DEFAULT_CALLBACK_GROUP) -> None: 
#         """ 
#         Attach ROS 2 subscriptions to each State object, enabling runtime updates 
#         to their `current_state` attribute via incoming messages.

#         Args:
#             node (Node): The ROS 2 node to which subscriptions are attached.
#             states (Dict[str, State]): A dictionary of state names to State objects.
#         """
#         for _, state_val in self.states.items():
#             node.create_subscription(
#                 msg_type=state_val.msg_type,
#                 topic=state_val.topic,
#                 callback=lambda msg, state=state_val: setattr(state, "current_state", msg),
#                 callback_group=callback_group,
#                 qos_profile=qos_profile
#             )

#     def _create_state_publishers(self, node: Node, qos_profile: QoSProfile = DEFAULT_QOS, callback_group:CallbackGroup = DEFAULT_CALLBACK_GROUP) -> None: 
#       """
#       Create and assign ROS 2 publishers for each State object, enabling outgoing
#       messages from the hybrid automaton model.

#       Args:
#           node (Node): The ROS 2 node used to create the publishers.
#           states (Dict[str, State]): A dictionary of state names to State objects.

#       Returns:
#           Dict[str, State]: The same input dictionary with updated `publisher` attributes.
#       """
#       for state_name, state_val in self.states.items():
#           self.states[state_name].publisher = node.create_publisher(
#               topic=state_val.topic,
#               msg_type=state_val.msg_type,
#               callback_group=callback_group,
#               qos_profile=qos_profile
#           )



#     @classmethod
#     def from_famd(cls, famd: Dict[str, Any]) -> "HybridAutomaton":
#         name = famd.get('automaton_name', '')
#         description = famd.get('automaton_description', '')
#         states = {
#             k: State.from_famd(v) for k, v in famd.get('states', {}).items()
#         }
#         modes = {
#             int(k): Mode.from_famd(v, famd)
#             for k, v in famd.get('modes', {}).items()
#         }
#         initial_mode = famd.get('initial_mode', 0)
        
#         return cls(
#             name=name,
#             description=description,
#             states=states,
#             modes=modes,
#             initial_mode=initial_mode,
#             goal_modes=famd.get('goal_modes', []),
#             transition_evaluation_frequency_hz=famd.get(
#                 'transition_evaluation_frequency_hz', 10.0
#             ),
#             control_frequency_hz=famd.get('control_frequency_hz', 50.0),
#             current_mode=initial_mode,
#             current_state=0
#         )


# if __name__ == '__main__':
#     famd_content = yaml.safe_load('''# COLAV Hybrid Automaton Formal Automaton Model Definition (FAMD)
# # ============================================================================
# # ROS2 Hybrid Automaton Framework Configuration (COLAV Hybrid Automaton)
# # ============================================================================
# # This defines the configuration for the Hybrid Automaton used in ROS2.
# # It includes mode declarations, transitions, guards, resets, invariants,
# # initial states, and parameter settings in a structured and interpretable format.
# #
# # IMPORTANT:
# # - Python function links (guards/resets) must point to valid, importable symbols.
# # - Functions must be exposed via __init__.py with __all__ to enable automatic access.
# # - Module paths must be within the Python build path (not direct file paths).
# #
# # Hybrid Automaton formalism:
# #   HA = (Q, Q_goal, X, F, Init, Inv, E, G, R)
# #
# #   Q      = modes
# #   Q_goal = goal_modes # Optional
# #   X      = states
# #   F      = dynamics
# #   Init   = initial_mode
# #   Inv    = invariants
# #   E      = transitions
# #   G      = guards
# #   R      = resets
# #
# # additional param:
# # params: This provides metatdata related to the hybrid automaton

# # ============================================================================
# # Continuous States (X)
# # These are received via ROS2 topics. Metadata is included per state.
# # Each of these states have buffers associated with buffer_size set in params
# # ============================================================================
# states:
#   agent_state:
#     topic: "/state/agent"
#     description: "State of the agent including position, velocity and heading."
#     type:
#       pkg: "colav_interfaces.msg"
#       msg: "AgentState"
#     params:
#       update_hz: 10.0
#       timeout_sec: 0.5
#       buffer_size: 100

#   obstacles_state:
#     topic: "/state/obstacles"
#     description: "State of the obstacles in the environment."
#     type:
#       pkg: "colav_interfaces.msg"
#       msg: "ObstaclesState"
#     params:
#       update_hz: 4.0
#       timeout_sec: 1.0

#   unsafe_set_state:
#     topic: "/state/unsafe_set"
#     description: "State of the unsafe set, indicating unsafe conditions for the agent."
#     type:
#       pkg: "colav_interfaces.msg"
#       msg: "UnsafeSetState"
#     params:
#       update_hz: 2.0
#       timeout_sec: 1.5

#   waypoints_state:
#     topic: "/state/waypoints"
#     description: "State of the waypoints including current waypoint and virtual waypoints."
#     type:
#       pkg: "colav_interfaces.msg"
#       msg: WaypointsState

# # ============================================================================
# # Reset Functions (R)
# # Executed during transitions to modify continuous state.
# # ============================================================================
# resets:
#   remove_virtual_waypoint_reset:
#     module: colav_hybrid_automaton.automaton.resets
#     class_name: RemoveVirtualWaypointReset
#     description: "Remove the first virtual waypoint from the waypoints state and update the current waypoint."
#     state_inputs:
#       - "waypoints_state"
#     reset_targets:
#       - "waypoints_state"
#     configuration: {}

#   generate_virtual_waypoint_reset:
#     module: colav_hybrid_automaton.automaton.resets
#     class_name: GenerateVirtualWaypointReset
#     description: "Generate a virtual waypoint based on the agent's position and obstacles, and add it to the waypoints state updating the current waypoint to it."
#     state_inputs:
#       - "agent_state"
#       - "obstacles_state"
#       - "unsafe_set_state"
#       - "waypoints_state"
#     reset_targets:
#       - "waypoints_state"
#     configuration:
#       longitudinal_offset_distance: 30.0
#       lateral_offset_distance: 5.0
#       virtual_waypoint_acceptance_radius: 20.0

# # ============================================================================
# # Guard Conditions (G)
# # Boolean functions checked during transition evaluation.
# # ============================================================================
# guards:
#   los_clear_to_waypoint_guard:
#     module: colav_hybrid_automaton.automaton.guards
#     class_name: LOSClearToWaypointGuard
#     description: "Checks if the line of sight from agent position to the current waypoint is clear."
#     state_inputs:
#       - "agent_state"
#       - "obstacles_state"
#       - "unsafe_set_state"
#       - "waypoints_state"
#     configuration:
#       los_distance_threshold: 100.0

#   heading_within_tolerance_guard:
#     module: colav_hybrid_automaton.automaton.guards
#     class_name: HeadingWithinToleranceGuard
#     description: "Checks if the agent's heading is within a specified tolerance of the waypoint direction."
#     state_inputs:
#       - "agent_state"
#       - "waypoints_state"
#     configuration:
#       heading_tolerance: 0.2

#   heading_not_within_tolerance_guard:
#     module: colav_hybrid_automaton.automaton.guards
#     class_name: HeadingNotWithinToleranceGuard
#     description: "Checks if the agent's heading is not within a specified tolerance of the waypoint direction."
#     state_inputs:
#       - "agent_state"
#       - "waypoints_state"
#     configuration:
#       heading_tolerance: 0.2

#   virtual_waypoints_guard:
#     module: colav_hybrid_automaton.automaton.guards
#     class_name: VirtualWaypointsGuard
#     description: "Checks if there are virtual waypoints available in the waypoints state."
#     state_inputs:
#       - "waypoints_state"
#     configuration: {}

#   unsafe_conditions_guard:
#     module: colav_hybrid_automaton.automaton.guards
#     class_name: UnsafeConditionsGuard
#     description: "Checks if the agent is in unsafe conditions based on obstacles and unsafe set."
#     state_inputs:
#       - "agent_state"
#       - "obstacles_state"
#       - "unsafe_set_state"
#     configuration: {}

#   waypoint_reached_guard:
#     module: colav_hybrid_automaton.automaton.guards
#     class_name: WaypointReachedGuard
#     description: "Checks if the agent has reached the current waypoint."
#     state_inputs:
#       - "agent_state"
#       - "waypoints_state"
#     configuration: {}

# # ============================================================================
# # Invariants (Inv)
# # Leave empty if no mode constraints exist.
# # ============================================================================
# invariants:
#   is_goal_waypoint_invariant:
#     module: colav_hybrid_automaton.automaton.invariants
#     class_name: IsGoalWaypointInvariant
#     description: "Checks if the current waypoint is the goal waypoint."
#     state_inputs:
#       - "waypoints_state"
#     configuration: {}

#   trivial_invariant:
#     module: colav_hybrid_automaton.automaton.invariants
#     class_name: TrivialInvariant
#     description: "A trivial invariant that always holds true."
#     state_inputs: []
#     configuration: {}

#   failing_invariant:
#     module: colav_hybrid_automaton.automaton.invariants
#     class_name: FailingInvariant
#     description: "An invariant that always fails, used for fallback mode."
#     state_inputs: []
#     configuration: {}

# # ============================================================================
# # Transitions (E)
# # Mapping of transition names to guard and reset functions.
# # ============================================================================
# transitions:
#   plan_evasive_maneuver:
#     origin_modes:
#       - 0
#     origin_priorities:
#       - 2
#     target_mode: 1
#     guard: "los_clear_to_waypoint_guard"
#     reset: "generate_virtual_waypoint_reset"

#   correct_heading:
#     origin_modes:
#       - 0
#     origin_priorities:
#       - 3
#     target_mode: 1
#     guard: "heading_not_within_tolerance_guard"
#     reset: null

#   enter_emergency_fallback:
#     origin_modes:
#       - 0
#       - 1
#     origin_priorities:
#       - 0
#       - 0
#     target_mode: 3
#     guard: "unsafe_conditions_guard"
#     reset: null

#   waypoint_arrival:
#     origin_modes:
#       - 0
#       - 1
#     origin_priorities:
#       - 1
#       - 2
#     target_mode: 2
#     guard: "waypoint_reached_guard"
#     reset: null

#   heading_aligned:
#     origin_modes:
#       - 1
#     origin_priorities:
#       - 0
#     target_mode: 0
#     guard: "heading_within_tolerance_guard"
#     reset: null

#   proceed_to_next_waypoint:
#     origin_modes:
#       - 2
#     origin_priorities:
#       - 0
#     target_mode: 0
#     guard: "virtual_waypoints_guard"
#     reset: "remove_virtual_waypoint_reset"

# # ============================================================================
# # Dynamics (F)
# # Controllers used for continuous evolution within each mode.
# # ============================================================================
# dynamics:
#   cruise_pid_controller:
#     module: colav_hybrid_automaton.automaton.dynamics
#     class_name: PIDControllerDynamics
#     description: "pid controller tuned for cruise mode."
#     state_inputs:
#       - "agent_state"
#       - "waypoints_state"
#     dynamic_outputs:
#       dynamic_parameter_names:
#         - "velocity"
#         - "yaw_rate"
#       dynamic_parameter_value_types:
#         - float
#         - float
#       dynamic_parameter_metrics:
#         - "m/s"
#         - "rad/s"
#     configuration:
#       target_velocity: 25.0 # updated cruise speed
#       yaw_kp: 0.3 # gentle heading proportional gain
#       yaw_ki: 0.01 # small integral for smooth correction
#       yaw_kd: 0.05 # small derivative gain to damp oscillations
#       vel_kp: 0.5 # moderate velocity proportional gain
#       vel_ki: 0.05 # small integral to avoid windup
#       vel_kd: 0.05 # small derivative for smooth velocity changes
#       error_tolerance: 0.01 # precision in heading error
#       max_yaw_rate: 0.1 # limit yaw rate to gentle turns

#   t2los_pid_controller:
#     module: colav_hybrid_automaton.automaton.dynamics
#     class_name: PIDControllerDynamics
#     description: "pid controller tuned for transition to line of sight (T2LOS) mode."
#     state_inputs:
#       - "agent_state"
#       - "waypoints_state"
#     dynamic_outputs:
#       dynamic_parameter_names:
#         - "velocity"
#         - "yaw_rate"
#       dynamic_parameter_value_types:
#         - float
#         - float
#       dynamic_parameter_metrics:
#         - "m/s"
#         - "rad/s"
#     configuration:
#       target_velocity: 25.0 # updated cruise speed
#       yaw_kp: 0.3 # gentle heading proportional gain
#       yaw_ki: 0.01 # small integral for smooth correction
#       yaw_kd: 0.05 # small derivative gain to damp oscillations
#       vel_kp: 0.5 # moderate velocity proportional gain
#       vel_ki: 0.05 # small integral to avoid windup
#       vel_kd: 0.05 # small derivative for smooth velocity changes
#       error_tolerance: 0.01 # precision in heading error
#       max_yaw_rate: 0.1 # limit yaw rate to gentle turns

#   no_op_controller:
#     module: colav_hybrid_automaton.automaton.dynamics
#     class_name: NoOpControllerDynamics
#     description: "No operation controller, used in waypoint reached and fallback mode for returning state 0 yaw rate and velocity."
#     state_inputs: []
#     dynamic_outputs:
#       dynamic_parameter_names:
#         - "velocity"
#         - "yaw_rate"
#       dynamic_parameter_value_types:
#         - float
#         - float
#       dynamic_parameter_metrics:
#         - "m/s"
#         - "rad/s"
#     configuration: {}

# # ============================================================================
# # Modes (Q)
# # Discrete states, each associated with dynamics, invariants, and transitions.
# # ============================================================================
# modes:
#   0:
#     name: cruise
#     description: "Cruise mode with pid controller tuned for cruise mode."
#     dynamics: cruise_pid_controller
#     invariants:
#       - trivial_invariant
#     transitions:
#       - enter_emergency_fallback:
#           priority: 0
#       - waypoint_arrival:
#           priority: 1
#       - plan_evasive_maneuver:
#           priority: 2
#       - correct_heading:
#           priority: 3

#   1:
#     name: t2los
#     description: "Transition to Line of Sight (T2LOS) mode with proportional yaw rate control"
#     dynamics: t2los_pid_controller
#     invariants:
#       - trivial_invariant
#     transitions:
#       - enter_emergency_fallback:
#           priority: 0
#       - heading_aligned:
#           priority: 1
#       - waypoint_arrival:
#           priority: 2

#   2:
#     name: waypoint_reached
#     description: "Waypoint reached mode, indicating successful navigation to a waypoint"
#     dynamics: no_op_controller
#     invariants:
#       - is_goal_waypoint_invariant
#     transitions:
#       - proceed_to_next_waypoint:
#           priority: 0

#   3:
#     name: fallback
#     description: "Fallback mode for emergency conditions, no active control"
#     dynamics: no_op_controller
#     invariants:
#       - failing_invariant
#     transitions: []

# # ============================================================================
# # Goal Modes (Q_goal)
# # ============================================================================
# goal_modes:
#   - 2

# # ============================================================================
# # Initial Mode (Init)
# # This is the mode the hybrid automaton will initially enter on
# # automaton activation
# # ============================================================================
# initial_mode: 0

# # ============================================================================
# # Parameters
# # these are parameters of the hybrid automaton set on
# # activation
# # ============================================================================
# parameters:
#   goal_waypoint:
#     type:
#       pkg: "colav_interfaces.msg"
#       msg: "Waypoint"

#   evaluation_frequency:
#     type: float

#   control_frequency:
#     type: float

# automaton_name: "colav_hybrid_automaton"
# automaton_description: "automaton for collision avoidance"
# transition_evaluation_frequency_hz: 10.0
# control_frequency_hz: 10.0
#     ''')
#     automaton = HybridAutomaton.from_famd(famd_content)
#     print (automaton)