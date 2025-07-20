from typing import Dict, List
from abc import ABC, abstractmethod
from typing import Dict, List, Set
from rclpy.node import Node
from .state import State
from rclpy.qos import QoSProfile
from rclpy.callback_groups import CallbackGroup
from typing import Optional, Type
from dataclasses import dataclass, field
from typing import Any
import logging

# Set up module-level logger
logger = logging.getLogger(__name__)

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