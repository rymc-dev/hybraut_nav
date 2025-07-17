from dataclasses import dataclass
from typing import Type, Any, Dict, Optional
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.callback_groups import CallbackGroup
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from importlib import impo
import importlib
from builtin_interfaces.msg import Time

def import_class(module_path: str, class_name: str) -> Type[Any]:
    """
    Dynamically import and return a class from a module.
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Cannot import '{class_name}' from '{module_path}': {e}")


@dataclass
class MsgType:
    pkg: str
    msg: str
    
@dataclass
class State: 
    _name: str
    _topic: str
    _msg_type: Any
    _current_state: Any
    _last_update: Time
    _state_publisher: Publisher = None
    _state_subscription: Subscription = None
    _update_hz: Optional[int]
    _timeout_sec: Optional[float]
    _is_active: bool = False
    _error_count: int = 0
    _max_errors: int = 10
    
    def activate_state(self, node: Node, qos: QoSProfile, cb_group: CallbackGroup):

        if self._is_active:
            raise RuntimeError('tried to activate State, but it has already been activated')

        self._create_state_publisher(node, qos, cb_group)
        self._create_state_subscription(node, qos, cb_group)

        self._is_active = True
      
    def deactivate_state(self, node: Node):
        
        if not self._is_active:
            raise RuntimeError('tried to deactive State, but it is not currently active')
        
        node.destroy_subscription(self._state_subscription)
        node.destroy_publisher(self._state_publisher)

        self._is_active = False

    def _state_received_callback(self, node:Node, state_msg: Any):
        """callback for the state subscription"""
        # Do validation of state, add an error, log it ...
        self.is_stale(state_msg.header.stamp)
        self._current_state = state_msg
        self._last_update = node.get_clock().now().to_msg()

    def is_stale(self, state_stamp: Time) -> bool:
        return False

    def reset_error_count(self):
        self._error_count=0

    def increment_error_count(self):
        self._error_count+=1
    
    def _create_state_publisher(self, node: Node, qos: QoSProfile, cb_group: CallbackGroup):
        self._state_publisher: Publisher = node.create_publisher(
            msg_type=self._msg_type,
            topic=self._topic,
            qos_profile=qos,
            callback_group=cb_group
        )

    def _create_state_subscription(self, node: Node, qos: QoSProfile, cb_group: CallbackGroup):
        self._state_subscription:Subscription = node.create_subscription(
            msg_type=self._msg_type,
            topic=self._topic,
            callback=lambda state_msg: self._state_received_callback(node=node, state_msg=state_msg),
            qos_profile=qos,
            callback_group=cb_group
        )

    def load_state_from_famd(cls, name: str, state_dict: Dict[str, Any]) -> 'State':
        msg_type:MsgType = MsgType(**state_dict['type'])
        msg_type = import_class(msg_type.pkg, msg_type.msg)
        return cls(
            _name=name,
            _topic=state_dict['topic'],
            _msg_type=msg_type,
        )
        

# @dataclass
# class Mode:
#     _id: int
#     _name: str
#     _description: str
#     _dynamics: DynamicsWrapper
#     _transitions: List[Transition]
#     _invariant_refs: List[str]
#     _entry_actions: List[str]
#     _exit_actions: List[str]
#     _is_goal_mode: bool

#     def on_enter(context: EvaluationContext):
#         pass

#     def on_exit(context: EvaluationContext):
#         pass

#     def evaluate_invariants(context: EvaluationContext) -> bool:
#         pass

#     from automaton_interfaces.msg import AutomatonTransitionEvaluations
#     def evalute_transitions() -> AutomatonTransitionEvaluations:
#         pass

# @dataclass
# class EvaluationContext:
#     _state: StateRegistry
#     _current_mode: Mode
#     _timestamp: float
#     _event_history: List[AutomatonEvent]
#     _metadata: Dict[str, Any]

#     def get_state_value(name: str):
#         # will return the state values based on the key
#         pass

#     def get_state_age(name: str):
#         # gets the age of the state
#         pass

#     def add_metadata(key: str, value: any):
#         pass

# class TransitionResult:
#     _success: bool
#     _new_mode: int
#     _errors: List[str]
#     _warnings: List[str]


# from automaton.automaton_registrys import GuardsRegistry
# from automaton.automaton_registrys import ResetsRegistry
# from automaton_interfaces.msg import AutomatonTransitionEvaluation
# from automaton_interfaces.msg import AutomatonReset, AutomatonResets
# from typing import Tuple

# @dataclass
# class Transition:
#     _name: str
#     _target_mode: int
#     _guard_ref: str
#     _reset_ref: Optional[str]
#     _priority: int
#     _metadata: Dict[str, Any]

    
#     def evaluate(context: EvaluationContext, guards_registry: GuardsRegistry) -> AutomatonTransitionEvaluation:
#         # here we perform a transition evaluation to check if the transition is enabled
#         pass

#     def execute(self, context: EvaluationContext, resets_registry: ResetsRegistry) -> Tuple[TransitionResult, AutomatonResets]: 
#         # the guard for this transition has been evaluated as being true, therefore we attempt to execute the transition
#         pass

