from dataclasses import dataclass
from typing import Type, Any, Dict, Optional
from rclpy.node import Node
from rclpy.qos import QoSProfile
from rclpy.callback_groups import CallbackGroup
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
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

    _current_state: Any = None
    _last_update: Time = None
    _state_publisher: Publisher = None
    _state_subscription: Subscription = None
    _update_hz: Optional[int] = None
    _timeout_sec: Optional[float] = None
    _is_active: bool = False
    _error_count: int = 0
    _max_errors: int = 10

    def activate_state(self, node: Node, qos: Optional[QoSProfile] = None, cb_group: Optional[CallbackGroup] = None):
        if self._is_active:
            raise RuntimeError('Tried to activate State, but it has already been activated')

        self._create_state_publisher(node, qos, cb_group)
        self._create_state_subscription(node, qos, cb_group)
        self._is_active = True

    def deactivate_state(self, node: Node):
        """
        Clean up state by destroying publisher and subscription.
        """
        if not self._is_active:
            raise RuntimeError('Tried to deactivate State, but it is not currently active')
        if not isinstance(node, Node):
            raise RuntimeError('node needs to be type rclpy.node.Node')
        
        node.destroy_subscription(self._state_subscription)
        node.destroy_publisher(self._state_publisher)

        self._is_active = False

    def _state_received_callback(self, node: Node, state_msg: Any):
        """Callback for receiving new state messages."""
        self.is_stale(state_msg.header.stamp)
        self._current_state = state_msg
        self._last_update = node.get_clock().now().to_msg()

    def is_stale(self, state_stamp: Time) -> bool:
        # Optional: Implement staleness check based on timeout
        return False

    def reset_error_count(self):
        self._error_count = 0

    def increment_error_count(self):
        self._error_count += 1

    def _create_state_publisher(self, node: Node, qos: Optional[QoSProfile] = None, cb_group: Optional[CallbackGroup] = None):
        if not isinstance(node, Node):
            raise RuntimeError('Invalid node type, should be rclpy.node.Node')
        if self._state_publisher is None:
            self._state_publisher = node.create_publisher(
                msg_type=self._msg_type,
                topic=self._topic,
                qos_profile=qos,
                callback_group=cb_group
            )

    def _create_state_subscription(self, node: Node, qos: Optional[QoSProfile] = None, cb_group: Optional[CallbackGroup] = None):
        if not isinstance(node, Node):
            raise RuntimeError('Invalid node type, should be rclpy.node.Node')
        if self._state_subscription is None:
            self._state_subscription = node.create_subscription(
                msg_type=self._msg_type,
                topic=self._topic,
                callback=lambda state_msg: self._state_received_callback(node=node, state_msg=state_msg),
                qos_profile=qos,
                callback_group=cb_group
            )

    def __str__(self):
        return f"<State '{self._name}' on topic '{self._topic}' (Active: {self._is_active})>"

    def __repr__(self):
        return (f"State(_name={self._name!r}, _topic={self._topic!r}, "
                f"_msg_type={self._msg_type.__name__ if hasattr(self._msg_type, '__name__') else str(self._msg_type)}, "
                f"_is_active={self._is_active}, _update_hz={self._update_hz}, "
                f"_timeout_sec={self._timeout_sec}, _error_count={self._error_count})")

    def get_state_info(self) -> Dict[str, Any]:
        """
        Returns a dictionary with current state info.
        """
        return {
            "name": self._name,
            "topic": self._topic,
            "active": self._is_active,
            "update_hz": self._update_hz,
            "timeout_sec": self._timeout_sec,
            "error_count": self._error_count,
            "last_update": str(self._last_update) if self._last_update else "None",
            "current_state": str(self._current_state) if self._current_state else "None",
        }

    @classmethod
    def load_state_from_famd(cls, name: str, state_dict: Dict[str, Any]) -> 'State':
        msg_type: MsgType = MsgType(**state_dict['type'])
        msg_type = import_class(msg_type.pkg, msg_type.msg)
        update_hz = state_dict.get('params', {}).get('update_hz')
        timeout_sec = state_dict.get('params', {}).get('timeout_sec')

        return cls(
            _name=name,
            _topic=state_dict['topic'],
            _msg_type=msg_type,
            _update_hz=update_hz,
            _timeout_sec=timeout_sec
        )

    
import threading
import rclpy
from rclpy.node import Node

if __name__ == '__main__':
    pose_stamped_state = {
        "topic": "/state/pose_stamped_state",
        "description": "State of the unsafe set, indicating unsafe conditions for the agent.",
        "type": {
            "pkg": "geometry_msgs.msg",  # Used for test-agnostic compatibility
            "msg": "PolygonStamped"      # Example geometry message; can be changed as needed
        },
        "params": {
            "update_hz": 2.0,
            "timeout_sec": 1.5
        }
    }

    rclpy.init()
    state: State = State.load_state_from_famd(name='pose_stamped_state', state_dict=pose_stamped_state)
    mock_node = Node('mock_node')
    thread = threading.Thread(target=lambda: rclpy.spin(mock_node))
    thread.start()

    state.activate_state(node=mock_node, qos=QoSProfile(depth=10))
    state.deactivate_state(node=mock_node)


    print (repr(state))
    print (str(state))
    print (state.get_state_info())

    rclpy.shutdown()


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

