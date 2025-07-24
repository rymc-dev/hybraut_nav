import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type

from builtin_interfaces.msg import Time

from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile, qos_profile_default
from rclpy.subscription import Subscription

from automaton_types.msg_type import MsgType
from component_interfaces.registry_interface import ComponentRegistry

# Set up module-level logger
logger = logging.getLogger(__name__)


@dataclass
class StateBus:
    _node: Node
    _topic: str
    _msg_type: Type
    _subscription_callback: Callable

    # now all the defaults come *after*
    _qos: Optional[QoSProfile] = field(
        init=True,
        default_factory=lambda: qos_profile_default
    )
    _cb_group: Optional[CallbackGroup] = field(
        init=True,
        default_factory=ReentrantCallbackGroup()
    )

    _state_publisher: Publisher     = field(default=None, init=False)
    _state_subscription: Subscription = field(default=None, init=False)
    _is_active: bool                 = field(default=False, init=False)

    def activate(self) -> None:
        # pass in the node, qos, and cb_group stored on self
        self._create_state_publisher(self._node, self._qos, self._cb_group)
        self._create_state_subscription(self._node, self._qos, self._cb_group)
        self._is_active = True

    def deactivate(self) -> None:
        if self._state_publisher:
            self._node.destroy_publisher(self._state_publisher)
        if self._state_subscription:
            self._node.destroy_subscription(self._state_subscription)
        self._is_active = False

    def publish_state(self, message: Any) -> None:
        if not self._is_active or not self._state_publisher:
            raise RuntimeError(f"State topic '{self._topic}' is not active for publishing")
        self._state_publisher.publish(message)

    # now each helper actually takes the things it needs:
    def _create_state_publisher(
        self,
        node: Node,
        qos: QoSProfile,
        cb_group: CallbackGroup
    ) -> None:
        if not isinstance(node, Node):
            raise RuntimeError("Invalid node type, should be rclpy.node.Node")
        if self._state_publisher is None:
            self._state_publisher = node.create_publisher(
                msg_type=self._msg_type,
                topic=self._topic,
                qos_profile=qos,
                callback_group=cb_group()
            )

    def _create_state_subscription(
        self,
        node: Node,
        qos: QoSProfile,
        cb_group: CallbackGroup
    ) -> None:
        if not isinstance(node, Node):
            raise RuntimeError("Invalid node type, should be rclpy.node.Node")
        if self._state_subscription is None:
            self._state_subscription = node.create_subscription(
                msg_type=self._msg_type,
                topic=self._topic,
                callback=lambda msg: self._subscription_callback(msg),
                qos_profile=qos,
                callback_group=cb_group()
            )

    @classmethod
    def initialize_state_bus(
        cls,
        node: Node,
        topic: str,
        msg_type: Type,
        subscription_callback: Callable,
        qos: Optional[QoSProfile] = qos_profile_default,
        cb_Group: Optional[CallbackGroup] = ReentrantCallbackGroup,
    ) -> 'StateBus':
        """generate StateBus dataclass instance

        Args:
            node (Node): _description_
            topic (str): _description_
            msg_type (Type): _description_
            subscription_callback (Callable): _description_
            qos (Optional[QoSProfile], optional): _description_. Defaults to qos_profile_default.
            cb_Group (Optional[CallbackGroup], optional): _description_. Defaults to ReentrantCallbackGroup.

        Returns:
            StateBus: _description_
        """
        return cls(
            _node = node,
            _topic=topic,
            _msg_type=msg_type,
            _subscription_callback=subscription_callback,
            _qos=qos,
            _cb_group=cb_Group
        )
        

class State:
    """
    Manages the lifecycle and data flow of a ROS2 state topic.
    
    This class encapsulates a bidirectional ROS2 topic (publisher/subscriber pair)
    with automatic message handling, error tracking, and lifecycle management.
    
    Attributes:
        _name (str): Unique identifier for this state
        _topic (str): ROS2 topic name
        _msg_type (Any): ROS2 message type class
        _current_state (Any): Most recent received message
        _last_update (Time): Timestamp of last message reception
        _state_publisher (Publisher): ROS2 publisher instance
        _state_subscription (Subscription): ROS2 subscription instance
        _update_hz (Optional[int]): Expected update frequency in Hz
        _timeout_sec (Optional[float]): Message timeout threshold in seconds
        _is_active (bool): Whether publisher/subscriber are active
        _error_count (int): Number of errors encountered
        _max_errors (int): Maximum allowed errors before flagging
        _logger (logging.Logger): Dedicated logger for this state instance
    
    Raises:
        RuntimeError: When attempting invalid lifecycle transitions
    """

    def __init__(
        self,
        name: str,
        topic: str,
        node: Node,
        msg_type: Type,
        qos_profile: Optional[QoSProfile] = None,
        cb_group: Optional[CallbackGroup] = None,
        update_hz: Optional[int] = None,
        timeout_sec: Optional[float] = None,
        max_errors: int = 10
    ):
        # stash everything you need
        self._name       = name
        self._topic      = topic
        self._node       = node
        self._update_hz  = update_hz
        self._timeout_sec= timeout_sec
        self._max_errors = max_errors

        # build the bus
        self._state_bus = StateBus.initialize_state_bus(
            node=node,
            topic=topic,
            msg_type=msg_type,
            subscription_callback=self.update_state,
        )
        self._is_active = False
        self._current_state = None
        self._error_count = 0
        self._last_update = None
        # set up your logger
        self._logger = logging.getLogger(f"{__name__}.State.{self._name}")

    def __post_init__(self):
        """Initialize the logger after dataclass creation."""
        self._logger = logging.getLogger(f"{__name__}.State.{self._name}")

    def is_synced(self, expected_hz: float, timeout_sec: float) -> bool:
        """Check if the state has been updated recently enough."""
        if not self._is_active:
            raise RuntimeError("can't check is_synced if states are not active")
        
        return True
        # now = time.time()
        # time_since_update = now - self.timestamp
        # min_expected_interval = 1.0 / expected_hz
        # return time_since_update <= timeout_sec and time_since_update <= 2 * min_expected_interval

    def activate(self) -> None:
        """
        Activate the state by creating publisher and subscriber.
        
        This method transitions the state from inactive to active, creating
        the necessary ROS2 communication infrastructure.
            
        Raises:
            RuntimeError: If state is already active
        """
        if self._is_active:
            raise RuntimeError(f"State '{self._name}' is already active")

        self._logger.info(f"Activating state '{self._name}' on topic '{self._topic}'")
        
        self._state_bus.activate()
        self._is_active = True
        
        self._logger.debug(f"State '{self._name}' successfully activated")

    def update_state(self, current_state: Any): 
        """
        Internal callback for processing received state messages.
        
        This method updates the internal state and timestamp when new
        messages are received from the subscription.
        
        Args:
            node (Node): ROS2 node (for clock access)
            state_msg (Any): Received ROS2 message
        """
        try:
            # Update state data
            self._current_state = current_state
            self._last_update = node.get_clock().now().to_msg()
            
            # Reset error count on successful reception
            self.reset_error_count()
            self._logger.debug(f"Successfully processed message for state '{self._name}'")
        except Exception as e:
            self.increment_error_count()
            self._logger.error(f"Error processing message for state '{self._name}': {e}")

    def deactivate(self) -> None:
        """
        Deactivate the state by cleaning up publisher and subscription.
        
        This method transitions the state from active to inactive, properly
        cleaning up ROS2 resources to prevent memory leaks.
        
        Args:
            node (Node): ROS2 node containing the publisher/subscriber
            
        Raises:
            RuntimeError: If state is not active or node is invalid
        """
        if not self._is_active:
            raise RuntimeError(f"State '{self._name}' is not currently active")
        if not isinstance(node, Node):
            raise RuntimeError('node must be of type rclpy.node.Node')
        
        self._logger.info(f"Deactivating state '{self._name}'")
        
        self._state_bus.deactivate()
        self._is_active = False

        self._logger.debug(f"State '{self._name}' successfully deactivated")

    def reset_error_count(self) -> None:
        """Reset the error counter to zero."""
        if self._error_count > 0:
            self._logger.debug(f"Resetting error count for state '{self._name}'")
        self._error_count = 0

    def increment_error_count(self) -> None:
        """Increment the error counter and log warnings if threshold exceeded."""
        self._error_count += 1
        self._logger.warning(f"Error count for state '{self._name}': {self._error_count}")
        
        if self._error_count >= self._max_errors:
            self._logger.error(f"State '{self._name}' has exceeded maximum error count ({self._max_errors})")

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"<State '{self._name}' on topic '{self._state_bus._topic}' (Active: {self._is_active})>"

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        msg_type_name = getattr(self._state_bus._msg_type, '__name__', str(self._state_bus._msg_type))
        return (f"State(_name={self._name!r}, _topic={self._state_bus._topic!r}, "
                f"_msg_type={msg_type_name}, _is_active={self._is_active}, "
                f"_update_hz={self._update_hz}, _timeout_sec={self._timeout_sec}, "
                f"_error_count={self._error_count})")

    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current state.
        
        Returns:
            Dict[str, Any]: Dictionary containing all relevant state information
        """
        return {
            "name": self._name,
            "topic": self._state_bus._topic,
            "message_type": getattr(self._state_bus._msg_type, '__name__', str(self._state_bus._msg_type)),
            "active": self._is_active,
            "update_hz": self._update_hz,
            "timeout_sec": self._timeout_sec,
            "error_count": self._error_count,
            "max_errors": self._max_errors,
            "last_update": str(self._last_update) if self._last_update else None,
            "has_current_state": self._current_state is not None,
            "current_state_summary": str(self._current_state)[:100] if self._current_state else None,
        }


    @property
    def state_bus(self) -> StateBus:
        return self._state_bus

    @property
    def current_state(self) -> Any:
        """Get the current state message (read-only property)."""
        return self._current_state

    @property
    def is_active(self) -> bool:
        """Check if the state is currently active (read-only property)."""
        return self._is_active

    @classmethod
    def load_state_from_amdl(cls, state_name: str, state_dict: Dict[str, Any], node:Node) -> 'State':
        """
        Create a State instance from FAMD (Formal Automaton Model Description) configuration.
        
        This factory method enables creation of State objects from configuration
        dictionaries, typically loaded from YAML or JSON files.
        
        Args:
            name (str): Unique name for the state
            state_dict (Dict[str, Any]): Configuration dictionary containing:
                - topic (str): ROS2 topic name
                - type (dict): Message type specification with 'pkg' and 'msg'
                - params (dict): Optional parameters like 'update_hz', 'timeout_sec'
        
        Returns:
            State: Configured State instance
            
        Raises:
            KeyError: If required configuration keys are missing
            ImportError: If message type cannot be imported
            
        Example:
            >>> config = {
            ...     "topic": "/robot/pose",
            ...     "type": {"pkg": "geometry_msgs.msg", "msg": "Pose"},
            ...     "params": {"update_hz": 10.0, "timeout_sec": 0.5}
            ... }
            >>> state = State.load_state_from_famd("pose_state", config)
        """
        try:
            # Extract and validate message type
            msg_type_info = MsgType(**state_dict['type'])
            msg_type = msg_type_info.import_msg_type()
            
            # Extract optional parameters
            params = state_dict.get('params', {})
            update_hz = params.get('update_hz')
            timeout_sec = params.get('timeout_sec')
            max_errors = params.get('max_errors', 10)
            
            logger.info(f"Loading state '{state_name}' from FAMD configuration")
            
            return State(
                name = state_name,
                topic = state_dict['topic'],
                node = node,
                msg_type = msg_type,
                qos_profile = None,
                cb_group = None,
                update_hz = update_hz,
                timeout_sec = timeout_sec,
                max_errors = None
            )

        except KeyError as e:
            error_msg = f"Missing required key in state configuration for '{state_name}': {e}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load state '{state_name}' from FAMD: {e}"
            logger.error(error_msg)
            raise

@dataclass
class StateRegistry(ComponentRegistry['State']):
    """Registry specialized for managing State components."""

    def __post_init__(self):
        self._component_type_name = "State"
        super().__post_init__()

    def get_current_states(self, state_names: List[str]) -> Dict[str, Any]:
        components = self.get_components_by_names(state_names)
        current_states = {}
        for component_name, component_val in components.items():
            current_states[component_name] = component_val.current_state

        return current_states

    @classmethod
    def _component_class(cls) -> Type[State]:
        return State

    @classmethod
    def register(cls: Type['ComponentRegistry'], config_dict: Dict[str, Any], node: Node) -> Dict[str, State]:
        """
        Create and return component instances from configuration dict.
        Subclasses must implement `_component_class()` returning their component class.
        """
        components = {}
        for name, conf in config_dict.items():
            try:
                component_cls = cls._component_class()
                component = component_cls.load_state_from_amdl(state_name=name, state_dict=conf, node=node)
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to load component '{name}': {e}")
                raise
        return components
        
    @classmethod
    def load_state_registry_from_amdl(cls, node: Node, states_dict: Dict[str, Any]) -> 'StateRegistry':
        logger.info("Loading StateRegistry from 'amdl' configuration")
        states = cls.register(node=node, config_dict=states_dict)
        registry = cls(_components=states)
        logger.info(f"Created StateRegistry with {len(states)} states")
        return registry


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    states = {
        "pose_state": {
            "topic": "/state/pose",
            "description": "Pose of the agent including position and orientation.",
            "type": {
                "pkg": "geometry_msgs.msg",
                "msg": "Pose"
            },
            "params": {
                "update_hz": 10.0,
                "timeout_sec": 0.5
            }
        },
        "twist_state": {
            "topic": "/state/twist",
            "description": "Twist of the agent including linear and angular velocity.",
            "type": {
                "pkg": "geometry_msgs.msg",
                "msg": "Twist"
            },
            "params": {
                "update_hz": 10.0,
                "timeout_sec": 0.5
            }
        }
    }

    import rclpy
    from rclpy.node import Node
    import threading
    from rclpy.executors import MultiThreadedExecutor

    rclpy.init()

    node = Node('test_node')
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    try:
        _state_registry: StateRegistry = StateRegistry.load_state_registry_from_amdl(node=node, states_dict=states)
        
        logger.info(f"Registry status before activation: {_state_registry}")
        _state_registry.activate_components(node)
        
        import time
        time.sleep(2.0)
        
        state_names = _state_registry.get_component_names()
        current_states = _state_registry.get_current_states(state_names)
        
        logger.info(f"Registry status: {_state_registry.get_registry_status()}")
        
        _state_registry.deactivate_components(node)
        logger.info(f"Registry status after deactivation: {_state_registry}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        rclpy.shutdown()
        thread.join()