"""
Hybrid Automaton Reset Abstract Base Class

This abstract class defines the interface for reset functions in the hybrid automaton framework.
Reset functions are used to update state variables when a transition between modes occurs.

All reset implementations must inherit from this class and implement the required methods.
Resets are executed during the hybrid automaton's transition to update system state
based on the current conditions and reset logic.

Example Usage:
    class WaypointReset(Reset):
        def __init__(self, reset_targets: List[Dict[str, Any]]):
            # reset_targets = [
            #     {'name': 'current_waypoint_index', 'type': int},
            #     {'name': 'waypoint_position', 'type': Tuple[float, float]}
            # ]
            super().__init__(reset_targets=reset_targets)
            
        def __call__(self, agent_state: AgentState, waypoints_state: WaypointsState) -> Dict[str, Any]:
            # Implementation logic here
            return {
                'current_waypoint_index': new_index,
                'waypoint_position': new_position
            }
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
from rclpy.logging import get_logger
from colav_hybrid_automaton.automaton._internal.types import InputSpec


class ResetABC(ABC):
    """
    Abstract base class for hybrid automaton reset functions.
    
    Reset functions update state variables during hybrid automaton transitions.
    They determine what state values should be modified when transitioning 
    from one mode to another based on the current system state.
    
    Attributes:
        logger: ROS2 logger instance for debugging and information output
        is_initialized: Flag indicating if the reset has been properly initialized
        reset_targets: List of objects that will be updated by this reset function
    """

    _expected_init_inputs: List[InputSpec] = []
    _expected_state_inputs = List[InputSpec] = []
    _reset_targets = List[InputSpec] = []

    def __init__(self, reset_targets: List[Dict[str, Any]], **init_kwargs):
        """
        Initialize the reset function with target objects and configuration parameters.
        
        This initialization is called once during the hybrid automaton configuration
        phase. Use this method to set up the list of objects that will be updated
        and any static parameters or constants.
        
        Args:
            reset_targets: List of dictionaries defining objects to be reset.
                         Each dictionary should contain:
                         - 'name': str - The name/key of the object to update
                         - 'type': type - The expected type of the object
                         - 'description': str (optional) - Description of the object
            **init_kwargs: Variable keyword arguments for reset configuration
            
        Raises:
            ValueError: If invalid configuration parameters are provided
            TypeError: If required parameters are missing or of wrong type
        """
        self.logger = get_logger(self.__class__.__name__)
        self.is_initialized = False
        self.reset_targets = reset_targets
        self._validate_initialization(reset_targets=reset_targets, **init_kwargs)
        self.is_initialized = True

    @abstractmethod
    def __call__(self, **state_kwargs) -> Dict[str, Any]:
        """
        Execute the reset function with current state inputs.
        
        This method is called during hybrid automaton transitions to compute
        the new values for the target objects. It receives the current state values
        and returns a dictionary mapping object names to their new values.
        
        Args:
            **state_kwargs: Variable keyword arguments containing state inputs
                          (e.g., agent_state, waypoints_state, obstacles_state)
                          as defined in the hybrid automaton configuration
                          
        Returns:
            Dict[str, Any]: Dictionary mapping target object names to their new values.
                           Keys should match the 'name' fields from reset_targets.
                           
        Raises:
            RuntimeError: If reset is called before proper initialization
            ValueError: If state inputs are invalid or incompatible
            TypeError: If state inputs don't match expected types or returned values don't match target types
            KeyError: If required state inputs are missing
            
        Example:
            def __call__(self, agent_state: AgentState, waypoints_state: WaypointsState) -> Dict[str, Any]:
                new_index = self._calculate_next_waypoint(agent_state, waypoints_state)
                new_position = waypoints_state.waypoints[new_index]
                return {
                    'current_waypoint_index': new_index,
                    'waypoint_position': new_position
                }
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before calling")
        
        # Validate inputs
        self._validate_states(**state_kwargs)
        
        # Subclasses should implement the actual reset logic after calling super()
        # and return a dictionary of {name: value} pairs

    def _validate_initialization(self, reset_targets: List[Dict[str, Any]], **init_kwargs) -> None:
        """
        Validate initialization parameters including reset targets.
        
        Override this method in subclasses to implement custom validation
        of initialization parameters. Always call super()._validate_initialization() 
        first in your override.
        
        Args:
            reset_targets: List of target objects to be validated
            **init_kwargs: Keyword arguments passed to __init__
            
        Raises:
            ValueError: If parameters are invalid
            TypeError: If parameters are of wrong type
            KeyError: If required parameters are missing
        """
        if not isinstance(reset_targets, list):
            raise TypeError("reset_targets must be a list")
        
        if not reset_targets:
            raise ValueError("reset_targets cannot be empty")
        
        for i, target in enumerate(reset_targets):
            if not isinstance(target, dict):
                raise TypeError(f"reset_targets[{i}] must be a dictionary")
            
            if 'name' not in target:
                raise KeyError(f"reset_targets[{i}] must contain 'name' key")
            
            if 'type' not in target:
                raise KeyError(f"reset_targets[{i}] must contain 'type' key")
            
            if not isinstance(target['name'], str):
                raise TypeError(f"reset_targets[{i}]['name'] must be a string")
    
    def _validate_states(self, **state_kwargs) -> None:
        """
        Validate state inputs before processing.
        
        Override this method in subclasses to implement custom validation
        of state inputs. Always call super()._validate_states() first in
        your override.
        
        Args:
            **state_kwargs: State input keyword arguments to validate
            
        Raises:
            ValueError: If state inputs are invalid
            TypeError: If state inputs are of wrong type
            KeyError: If required state inputs are missing
            RuntimeError: If reset is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError(f'{self.__class__.__name__} reset is not initialized')
    
    def _validate_reset_output(self, reset_output: Dict[str, Any]) -> None:
        """
        Validate the output of the reset function against target specifications.
        
        This method checks that the returned dictionary contains the expected
        keys and value types as defined in reset_targets.
        
        Args:
            reset_output: Dictionary returned by the __call__ method
            
        Raises:
            ValueError: If output is invalid
            TypeError: If output types don't match target specifications
            KeyError: If required output keys are missing
        """
        if not isinstance(reset_output, dict):
            raise TypeError("Reset function must return a dictionary")
        
        target_names = {target['name'] for target in self.reset_targets}
        output_names = set(reset_output.keys())
        
        missing_names = target_names - output_names
        if missing_names:
            raise KeyError(f"Reset output missing required keys: {missing_names}")
        
        extra_names = output_names - target_names
        if extra_names:
            self.logger.warning(f"Reset output contains unexpected keys: {extra_names}")
        
        # Validate types
        target_types = {target['name']: target['type'] for target in self.reset_targets}
        for name, value in reset_output.items():
            if name in target_types:
                expected_type = target_types[name]
                if not isinstance(value, expected_type):
                    raise TypeError(f"Reset output '{name}' expected type {expected_type.__name__}, got {type(value).__name__}")

    @property
    def expected_init_inputs(self) -> Dict[str, Type]:
        """Return a list of initialization inputs expected for the __init__ , names and types"""
        return self._expected_init_inputs.copy()
    
    @property
    def required_init_input_names(self) -> List[str]: 
         """return a list of names of initialization args"""
         return list(self._expected_init_inputs.keys())
    
    @property
    def expected_state_inputs(self) -> Dict[str, Type]:
        """Return a list of state inputs expected for the __call__ , names and types"""
        return self._expected_state_inputs.copy()
    
    @property
    def required_state_inputs_names(self) -> List[str]: 
        """Return a list of state inputs"""
        return list(self._expected_state_inputs.keys())

    @property
    def expected_reset_targets(self) -> Dict[str, Type]:
        """Return a list of reset target names and types for the __call__"""
        return self._reset_targets.copy()
    
    @property
    def required_reset_target_names(self) -> List[str]: 
        """Return a list of state inputs"""
        return list(self._reset_targets.keys())

    def get_reset_info(self) -> Dict[str, Any]:
        """
        Get information about this reset function.
        
        Returns:
            Dict[str, Any]: Dictionary containing reset metadata including
                          class name, initialization status, target objects, and configuration
        """
        class_doc = self.__class__.__doc__
        return {
            'class_name': self.__class__.__name__,
            'module': self.__class__.__module__,
            'is_initialized': self.is_initialized,
            'required_init_inputs':self.required_init_input_names(),
            'required_init_types': {
                name: type_.__name__ for name, type_ in self._expected_init_inputs.items()
            },
            'required_state_inputs': self.required_state_inputs_names,
            'expected_state_types':  {
                name: type_.__name__ for name, type_ in self._expected_state_inputs.items()
            },
            'reset_targets': self.reset_targets,
            'target_count': len(self.reset_targets),
            'target_names': [target['name'] for target in self.reset_targets],
            'description': class_doc.strip().split('\n')[0] if class_doc else "No description"
        }
    
    def __repr__(self) -> str:
        """String representation of the reset function."""
        target_names = [target['name'] for target in self.reset_targets] if self.is_initialized else []
        return f"{self.__class__.__name__}(initialized={self.is_initialized}, targets={target_names})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Reset Function: {self.__class__.__name__} (targets: {len(self.reset_targets) if self.is_initialized else 0})"