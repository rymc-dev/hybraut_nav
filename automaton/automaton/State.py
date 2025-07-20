from dataclasses import dataclass
from typing import Type, Any, Dict, Optional
from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_default
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.callback_groups import CallbackGroup
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
import importlib
from builtin_interfaces.msg import Time
import logging

# Set up module-level logger
logger = logging.getLogger(__name__)

@dataclass
class MsgType:
    """Helper class for message type specification."""
    pkg: str
    msg: str

def import_class(pkg_name: str, class_name: str) -> Type:
    """
    Dynamically import a class from a package.
    
    Args:
        pkg_name (str): Package name (e.g., 'geometry_msgs.msg')
        class_name (str): Class name (e.g., 'PolygonStamped')
    
    Returns:
        Type: The imported class
        
    Raises:
        ImportError: If the package or class cannot be imported
    """
    try:
        module = importlib.import_module(pkg_name)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Cannot import {class_name} from {pkg_name}: {e}")

    
@dataclass
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
    _name: str
    _topic: str
    _msg_type: Any
    
    # State data
    _current_state: Any = None
    _last_update: Optional[Time] = None
    
    # ROS2 communication objects
    _state_publisher: Optional[Publisher] = None
    _state_subscription: Optional[Subscription] = None
    
    # Configuration parameters
    _update_hz: Optional[float] = None
    _timeout_sec: Optional[float] = None
    
    # Status tracking
    _is_active: bool = False
    _error_count: int = 0
    _max_errors: int = 10
    
    # Logger instance
    _logger: Optional[logging.Logger] = None

    def __post_init__(self):
        """Initialize the logger after dataclass creation."""
        self._logger = logging.getLogger(f"{__name__}.State.{self._name}")

    def activate_state(self, node: Node, qos: Optional[QoSProfile] = None, 
                      cb_group: Optional[CallbackGroup] = None) -> None:
        """
        Activate the state by creating publisher and subscriber.
        
        This method transitions the state from inactive to active, creating
        the necessary ROS2 communication infrastructure.
        
        Args:
            node (Node): ROS2 node to attach publisher/subscriber to
            qos (Optional[QoSProfile]): Quality of Service profile
            cb_group (Optional[CallbackGroup]): Callback group for threading
            
        Raises:
            RuntimeError: If state is already active
        """
        if self._is_active:
            raise RuntimeError(f"State '{self._name}' is already active")

        self._logger.info(f"Activating state '{self._name}' on topic '{self._topic}'")
        
        self._create_state_publisher(node, qos, cb_group)
        self._create_state_subscription(node, qos, cb_group)
        self._is_active = True
        
        self._logger.debug(f"State '{self._name}' successfully activated")

    def deactivate_state(self, node: Node) -> None:
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
        
        # Clean up ROS2 resources
        if self._state_subscription:
            node.destroy_subscription(self._state_subscription)
            self._state_subscription = None
            
        if self._state_publisher:
            node.destroy_publisher(self._state_publisher)
            self._state_publisher = None

        self._is_active = False
        self._logger.debug(f"State '{self._name}' successfully deactivated")

    def publish_state(self, node: Node, message: Any) -> None:
        """
        Publish a message to the state topic.
        
        Args:
            node (Node): ROS2 node (for compatibility, may be removed in future)
            message (Any): ROS2 message to publish
            
        Raises:
            RuntimeError: If state is not active or publisher is None
        """
        if not self._is_active or not self._state_publisher:
            raise RuntimeError(f"State '{self._name}' is not active for publishing")
            
        try:
            self._state_publisher.publish(message)
            self._logger.debug(f"Published message to state '{self._name}'")
        except Exception as e:
            self.increment_error_count()
            self._logger.error(f"Failed to publish to state '{self._name}': {e}")
            raise

    def _state_received_callback(self, node: Node, state_msg: Any) -> None:
        """
        Internal callback for processing received state messages.
        
        This method updates the internal state and timestamp when new
        messages are received from the subscription.
        
        Args:
            node (Node): ROS2 node (for clock access)
            state_msg (Any): Received ROS2 message
        """
        try:
            # Check for message staleness if timeout is configured
            if hasattr(state_msg, 'header') and hasattr(state_msg.header, 'stamp'):
                if self.is_stale(state_msg.header.stamp):
                    self._logger.warning(f"Received stale message for state '{self._name}'")
            
            # Update state data
            self._current_state = state_msg
            self._last_update = node.get_clock().now().to_msg()
            
            # Reset error count on successful reception
            self.reset_error_count()
            self._logger.debug(f"Successfully processed message for state '{self._name}'")
        except Exception as e:
            self.increment_error_count()
            self._logger.error(f"Error processing message for state '{self._name}': {e}")

    def is_stale(self, state_stamp: Time) -> bool:
        """
        Check if a message timestamp indicates stale data.
        
        Args:
            state_stamp (Time): Timestamp from message header
            
        Returns:
            bool: True if message is considered stale, False otherwise
            
        Note:
            Currently returns False. Implement staleness logic based on
            _timeout_sec if needed.
        """
        # TODO: Implement staleness check based on _timeout_sec
        # if self._timeout_sec:
        #     current_time = time.time()
        #     message_time = state_stamp.sec + state_stamp.nanosec * 1e-9
        #     return (current_time - message_time) > self._timeout_sec
        return False

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

    def _create_state_publisher(self, node: Node, qos: Optional[QoSProfile] = None, 
                               cb_group: Optional[CallbackGroup] = None) -> None:
        """
        Create and configure the ROS2 publisher for this state.
        
        Args:
            node (Node): ROS2 node to create publisher on
            qos (Optional[QoSProfile]): Quality of Service profile
            cb_group (Optional[CallbackGroup]): Callback group for threading
            
        Raises:
            RuntimeError: If node is invalid type
        """
        if not isinstance(node, Node):
            raise RuntimeError('Invalid node type, should be rclpy.node.Node')
            
        if self._state_publisher is None:
            qos = qos or qos_profile_default
            cb_group = cb_group or ReentrantCallbackGroup()
            
            self._state_publisher = node.create_publisher(
                msg_type=self._msg_type,
                topic=self._topic,
                qos_profile=qos,
                callback_group=cb_group
            )
            
            self._logger.debug(f"Created publisher for state '{self._name}' on topic '{self._topic}'")

    def _create_state_subscription(self, node: Node, qos: Optional[QoSProfile] = None, 
                                  cb_group: Optional[CallbackGroup] = None) -> None:
        """
        Create and configure the ROS2 subscription for this state.
        
        Args:
            node (Node): ROS2 node to create subscription on
            qos (Optional[QoSProfile]): Quality of Service profile
            cb_group (Optional[CallbackGroup]): Callback group for threading
            
        Raises:
            RuntimeError: If node is invalid type
        """
        if not isinstance(node, Node):
            raise RuntimeError('Invalid node type, should be rclpy.node.Node')
            
        if self._state_subscription is None:
            qos = qos or qos_profile_default
            cb_group = cb_group or ReentrantCallbackGroup()
            
            self._state_subscription = node.create_subscription(
                msg_type=self._msg_type,
                topic=self._topic,
                callback=lambda state_msg: self._state_received_callback(node=node, state_msg=state_msg),
                qos_profile=qos,
                callback_group=cb_group
            )
            
            self._logger.debug(f"Created subscription for state '{self._name}' on topic '{self._topic}'")

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"<State '{self._name}' on topic '{self._topic}' (Active: {self._is_active})>"

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        msg_type_name = getattr(self._msg_type, '__name__', str(self._msg_type))
        return (f"State(_name={self._name!r}, _topic={self._topic!r}, "
                f"_msg_type={msg_type_name}, _is_active={self._is_active}, "
                f"_update_hz={self._update_hz}, _timeout_sec={self._timeout_sec}, "
                f"_error_count={self._error_count})")

    def get_state_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current state.
        
        Returns:
            Dict[str, Any]: Dictionary containing all relevant state information
        """
        return {
            "name": self._name,
            "topic": self._topic,
            "message_type": getattr(self._msg_type, '__name__', str(self._msg_type)),
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
    def current_state(self) -> Any:
        """Get the current state message (read-only property)."""
        return self._current_state

    @property
    def is_active(self) -> bool:
        """Check if the state is currently active (read-only property)."""
        return self._is_active

    @classmethod
    def load_state_from_famd(cls, name: str, state_dict: Dict[str, Any]) -> 'State':
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
            msg_type = import_class(msg_type_info.pkg, msg_type_info.msg)
            
            # Extract optional parameters
            params = state_dict.get('params', {})
            update_hz = params.get('update_hz')
            timeout_sec = params.get('timeout_sec')
            max_errors = params.get('max_errors', 10)
            
            logger.info(f"Loading state '{name}' from FAMD configuration")
            
            return cls(
                _name=name,
                _topic=state_dict['topic'],
                _msg_type=msg_type,
                _update_hz=update_hz,
                _timeout_sec=timeout_sec,
                _max_errors=max_errors
            )
            
        except KeyError as e:
            error_msg = f"Missing required key in state configuration for '{name}': {e}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load state '{name}' from FAMD: {e}"
            logger.error(error_msg)
            raise


import threading
import rclpy
from rclpy.node import Node

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
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

    print(repr(state))
    print(str(state))
    print(state.get_state_info())

    rclpy.shutdown()
    thread.join()