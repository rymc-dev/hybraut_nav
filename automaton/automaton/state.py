from dataclasses import dataclass
from typing import Type, Any, Dict, Optional
from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_default
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.callback_groups import CallbackGroup
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from builtin_interfaces.msg import Time
import logging
from typing import List, Dict
from dataclasses import dataclass, field
from utils import import_class
from automaton_types import MsgType

# Set up module-level logger
logger = logging.getLogger(__name__)


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
    _update_hz: Optional[int] = None
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
            msg_type = msg_type_info.import_msg_type()
            
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

# import threading
# import rclpy
# from rclpy.node import Node

# if __name__ == '__main__':
#     # Configure logging
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
    
#     pose_stamped_state = {
#         "topic": "/state/pose_stamped_state",
#         "description": "State of the unsafe set, indicating unsafe conditions for the agent.",
#         "type": {
#             "pkg": "geometry_msgs.msg",  # Used for test-agnostic compatibility
#             "msg": "PolygonStamped"      # Example geometry message; can be changed as needed
#         },
#         "params": {
#             "update_hz": 2.0,
#             "timeout_sec": 1.5
#         }
#     }

#     rclpy.init()
#     state: State = State.load_state_from_famd(name='pose_stamped_state', state_dict=pose_stamped_state)
#     mock_node = Node('mock_node')
#     thread = threading.Thread(target=lambda: rclpy.spin(mock_node))
#     thread.start()

#     state.activate_state(node=mock_node, qos=QoSProfile(depth=10))
#     state.deactivate_state(node=mock_node)

#     print(repr(state))
#     print(str(state))
#     print(state.get_state_info())

#     rclpy.shutdown()
#     thread.join()

@dataclass
class StateRegistry:
    """
    Central registry for managing multiple State instances.
    
    This class implements the Registry pattern to provide centralized management
    of multiple states, including bulk operations for activation/deactivation
    and convenient access methods.
    
    Attributes:
        _states (Dict[str, State]): Dictionary of state instances keyed by name
        _are_states_active (bool): Whether all states are currently active
        _logger (logging.Logger): Dedicated logger for this registry instance
    
    Raises:
        KeyError: When requesting non-existent states
        RuntimeError: When attempting invalid state transitions
    """
    _states: Dict[str, State] = field(default_factory=dict)
    _are_states_active: bool = False
    _logger: Optional[logging.Logger] = None

    def __post_init__(self):
        """Initialize the logger after dataclass creation."""
        self._logger = logging.getLogger(f"{__name__}.StateRegistry")

    def get_current_states_by_name(self, state_names: List[str]) -> Dict[str, Any]:
        """
        Retrieve current state messages for specified states.
        
        Args:
            state_names (List[str]): List of state names to retrieve
            
        Returns:
            Dict[str, Any]: Mapping of state names to their current messages
            
        Raises:
            KeyError: If any state name is not found in the registry
        """
        current_states = {}
        missing_states = []
        
        for name in state_names:
            if name in self._states:
                current_states[name] = self._states[name].current_state
            else:
                missing_states.append(name)
        
        if missing_states:
            error_msg = f"States not found in registry: {missing_states}"
            self._logger.error(error_msg)
            raise KeyError(error_msg)
            
        self._logger.debug(f"Retrieved current states for: {state_names}")
        return current_states

    def get_all_current_states(self) -> Dict[str, Any]:
        """
        Retrieve current state messages for all registered states.
        
        Returns:
            Dict[str, Any]: Mapping of all state names to their current messages
        """
        return self.get_current_states_by_name(list(self._states.keys()))

    def validate_state_dependencies(self, required_states: List[str], 
                                  required_types: Optional[List[Type]] = None) -> bool:
        """
        Validate that required states exist and optionally match expected types.
        
        This method can be used by components to verify their state dependencies
        before attempting to use them.
        
        Args:
            required_states (List[str]): List of required state names
            required_types (Optional[List[Type]]): Expected message types (same order)
            
        Returns:
            bool: True if all dependencies are satisfied
            
        Raises:
            ValueError: If validation fails
        """
        missing_states = [name for name in required_states if name not in self._states]
        if missing_states:
            error_msg = f"Missing required states: {missing_states}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        
        if required_types and len(required_types) == len(required_states):
            type_mismatches = []
            for state_name, expected_type in zip(required_states, required_types):
                actual_type = self._states[state_name]._msg_type
                if actual_type != expected_type:
                    type_mismatches.append(f"{state_name}: expected {expected_type}, got {actual_type}")
            
            if type_mismatches:
                error_msg = f"State type mismatches: {type_mismatches}"
                self._logger.error(error_msg)
                raise ValueError(error_msg)
        
        self._logger.debug(f"State dependencies validated: {required_states}")
        return True

    def get_state_names(self) -> List[str]:
        """
        Get a list of all registered state names.
        
        Returns:
            List[str]: List of state names
        """
        return list(self._states.keys())

    def get_state_msg_types(self) -> List[Type]:
        """
        Get a list of all registered state message types.
        
        Returns:
            List[Type]: List of message types in the same order as state names
        """
        return [state._msg_type for state in self._states.values()]

    def get_state(self, name: str) -> State:
        """
        Get a specific state by name.
        
        Args:
            name (str): Name of the state to retrieve
            
        Returns:
            State: The requested state instance
            
        Raises:
            KeyError: If state name is not found
        """
        if name not in self._states:
            error_msg = f"State '{name}' not found in registry"
            self._logger.error(error_msg)
            raise KeyError(error_msg)
        return self._states[name]

    def activate_states(self, node: Node, qos: Optional[QoSProfile] = None, 
                       cb_group: Optional[CallbackGroup] = None) -> None:
        """
        Activate all registered states.
        
        This method creates publishers and subscribers for all states,
        transitioning the entire registry to active status.
        
        Args:
            node (Node): ROS2 node to attach publishers/subscribers to
            qos (Optional[QoSProfile]): Quality of Service profile for all states
            cb_group (Optional[CallbackGroup]): Callback group for all states
            
        Raises:
            RuntimeError: If states are already active
        """
        if self._are_states_active:
            error_msg = 'States are already active'
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)

        self._logger.info(f"Activating {len(self._states)} states")
        
        activated_states = []
        try:
            for state_name, state in self._states.items():
                self._logger.debug(f"Activating state: {state_name}")
                state.activate_state(node, qos, cb_group)
                activated_states.append(state_name)
                
            self._are_states_active = True
            self._logger.info(f"Successfully activated all states: {activated_states}")
            
        except Exception as e:
            # Rollback: deactivate any states that were successfully activated
            self._logger.error(f"Failed to activate states, rolling back: {e}")
            for state_name in activated_states:
                try:
                    self._logger.debug(f"Rolling back activation for state: {state_name}")
                    self._states[state_name].deactivate_state(node)
                except Exception as rollback_error:
                    self._logger.error(f"Rollback failed for state '{state_name}': {rollback_error}")
            raise

    def deactivate_states(self, node: Node) -> None:
        """
        Deactivate all registered states.
        
        This method cleans up publishers and subscribers for all states,
        transitioning the entire registry to inactive status.
        
        Args:
            node (Node): ROS2 node containing the publishers/subscribers
            
        Raises:
            RuntimeError: If states are not currently active
        """
        if not self._are_states_active:
            error_msg = 'States are not currently active'
            self._logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        self._logger.info(f"Deactivating {len(self._states)} states")
        
        deactivation_errors = []
        for state_name, state in self._states.items():
            try:
                self._logger.debug(f"Deactivating state: {state_name}")
                state.deactivate_state(node)
            except Exception as e:
                error_msg = f"Failed to deactivate state '{state_name}': {e}"
                self._logger.error(error_msg)
                deactivation_errors.append(error_msg)
        
        self._are_states_active = False
        
        if deactivation_errors:
            self._logger.warning(f"Some states failed to deactivate properly: {len(deactivation_errors)} errors")
        else:
            self._logger.info("Successfully deactivated all states")

    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status information about the registry.
        
        Returns:
            Dict[str, Any]: Status information including state count, 
                           activation status, and individual state info
        """
        status = {
            "total_states": len(self._states),
            "states_active": self._are_states_active,
            "state_names": self.get_state_names(),
            "states_info": {name: state.get_state_info() for name, state in self._states.items()},
            "error_states": [name for name, state in self._states.items() if state._error_count > 0]
        }
        
        self._logger.debug(f"Generated registry status: {len(self._states)} states, active: {self._are_states_active}")
        return status

    def add_state(self, name: str, state: State) -> None:
        """
        Add a state to the registry.
        
        Args:
            name (str): Name for the state
            state (State): State instance to add
            
        Raises:
            ValueError: If state name already exists
        """
        if name in self._states:
            error_msg = f"State '{name}' already exists in registry"
            self._logger.error(error_msg)
            raise ValueError(error_msg)
        
        self._states[name] = state
        self._logger.info(f"Added state '{name}' to registry")

    def remove_state(self, name: str, node: Optional[Node] = None) -> None:
        """
        Remove a state from the registry.
        
        Args:
            name (str): Name of the state to remove
            node (Optional[Node]): ROS2 node for deactivation if state is active
            
        Raises:
            KeyError: If state name not found
            RuntimeError: If state is active but no node provided
        """
        if name not in self._states:
            error_msg = f"State '{name}' not found in registry"
            self._logger.error(error_msg)
            raise KeyError(error_msg)
        
        state = self._states[name]
        if state.is_active:
            if node is None:
                error_msg = f"Cannot remove active state '{name}' without providing node for deactivation"
                self._logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            try:
                state.deactivate_state(node)
                self._logger.debug(f"Deactivated state '{name}' before removal")
            except Exception as e:
                self._logger.warning(f"Failed to deactivate state '{name}' during removal: {e}")
        
        del self._states[name]
        self._logger.info(f"Removed state '{name}' from registry")

    @classmethod
    def register_state(cls, state_name: str, state_dict: Dict[str, Any]) -> State:
        """
        Create a single State instance from configuration.
        
        Args:
            state_name (str): Name for the new state
            state_dict (Dict[str, Any]): State configuration dictionary
            
        Returns:
            State: Newly created State instance
        """
        logger.debug(f"Creating state '{state_name}' from configuration")
        return State.load_state_from_famd(state_name, state_dict)

    @classmethod
    def register_states(cls, states_dict: Dict[str, Any]) -> Dict[str, State]:
        """
        Create multiple State instances from configuration dictionary.
        
        Args:
            states_dict (Dict[str, Any]): Dictionary mapping state names to configurations
            
        Returns:
            Dict[str, State]: Dictionary of created State instances
        """
        state_registry = {}
        if states_dict:
            logger.info(f"Registering {len(states_dict)} states")
            for state_name, state_config in states_dict.items():
                try:
                    state_registry[state_name] = cls.register_state(state_name, state_config)
                    logger.debug(f"Registered state '{state_name}'")
                except Exception as e:
                    logger.error(f"Failed to register state '{state_name}': {e}")
                    raise
        else:
            logger.warning("No states provided for registration")
        
        return state_registry

    @classmethod
    def load_state_registry_from_famd(cls, states_dict: Dict[str, Any]) -> 'StateRegistry':
        """
        Create a StateRegistry from FAMD configuration.
        
        This factory method creates a complete registry with all specified states
        from a configuration dictionary, typically loaded from external files.
        
        Args:
            states_dict (Dict[str, Any]): Configuration dictionary mapping 
                                         state names to their configurations
        
        Returns:
            StateRegistry: Fully configured StateRegistry instance
            
        Example:
            >>> config = {
            ...     "pose_state": {
            ...         "topic": "/robot/pose",
            ...         "type": {"pkg": "geometry_msgs.msg", "msg": "Pose"},
            ...         "params": {"update_hz": 10.0}
            ...     }
            ... }
            >>> registry = StateRegistry.load_state_registry_from_famd(config)
        """
        logger.info("Loading StateRegistry from FAMD configuration")
        states = cls.register_states(states_dict)
        
        registry = cls(_states=states)
        logger.info(f"Created StateRegistry with {len(states)} states")
        return registry

    def __len__(self) -> int:
        """Return the number of states in the registry."""
        return len(self._states)

    def __contains__(self, state_name: str) -> bool:
        """Check if a state exists in the registry."""
        return state_name in self._states

    def __iter__(self):
        """Iterate over state names."""
        return iter(self._states)

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        active_status = "Active" if self._are_states_active else "Inactive"
        return f"<StateRegistry: {len(self._states)} states ({active_status})>"

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return (f"StateRegistry(_states={list(self._states.keys())}, "
                f"_are_states_active={self._are_states_active})")


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
        _state_registry: StateRegistry = StateRegistry.load_state_registry_from_famd(states_dict=states)
        
        logger.info(f"Registry status before activation: {_state_registry}")
        _state_registry.activate_states(node)
        
        import time
        time.sleep(2.0)
        
        state_names = _state_registry.get_state_names()
        current_states = _state_registry.get_current_states_by_name(state_names)
        
        logger.info(f"Registry status: {_state_registry.get_registry_status()}")
        
        _state_registry.deactivate_states(node)
        logger.info(f"Registry status after deactivation: {_state_registry}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        rclpy.shutdown()
        thread.join()