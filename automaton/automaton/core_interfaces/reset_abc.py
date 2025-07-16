"""
Hybrid Automaton Reset Abstract Base Class

This abstract class defines the interface for reset functions in the hybrid automaton framework.
Reset functions are used to update state variables when a transition between modes occurs.

All reset implementations must inherit from this class and implement the required methods.
Resets are executed during the hybrid automaton's transition to update system state
based on the current conditions and reset logic.

Example Usage:
    class WaypointReset(ResetABC):
        _state_input_spec = [
            InputSpec(name='agent_state', type=AgentState),
            InputSpec(name='waypoints_state', type=WaypointsState)
        ]
        
        def __init__(self, reset_targets: List[InputSpec]):
            # reset_targets = [
            #     InputSpec(name='current_waypoint_index', type=int),
            #     InputSpec(name='waypoint_position', type=Tuple[float, float])
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
from typing import Any, Dict, List
from rclpy.logging import get_logger
from nodes._internal.types import InputSpec


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

    _init_input_spec: List[InputSpec] = []
    _state_input_spec: List[InputSpec] = []
    _reset_targets_spec: List[InputSpec] = []

    def __init__(self, **init_kwargs):
        """
        Initialize the reset function with target objects and configuration parameters.
        
        This initialization is called once during the hybrid automaton configuration
        phase. Use this method to set up the list of objects that will be updated
        and any static parameters or constants.
        
        Args:
            reset_targets: List of InputSpec objects defining objects to be reset.
                         Each InputSpec should contain:
                         - name: str - The name/key of the object to update
                         - type: type - The expected type of the object
                         - description: str (optional) - Description of the object
            **init_kwargs: Variable keyword arguments for reset configuration
            
        Raises:
            ValueError: If invalid configuration parameters are provided
            TypeError: If required parameters are missing or of wrong type
        """
        self.logger = get_logger(self.__class__.__name__)
        self.is_initialized = False
        
        self._validate_initialization(**init_kwargs)
        self._set_instance_initialization(**init_kwargs)
        self.is_initialized = True

    def _set_instance_initialization(self, **init_kwargs) -> None:
        """Set instance attributes from initialization kwargs."""
        for key, value in init_kwargs.items():
            setattr(self, key, value)

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

    def _validate_initialization(self, **init_kwargs) -> None:
        """
        Validate initialization parameters.
        
        Override this method in subclasses to implement custom validation
        of initialization parameters.
        
        Args:
            reset_targets: List of InputSpec objects defining reset targets
            **init_kwargs: Keyword arguments passed to __init__
            
        Raises:
            ValueError: If parameters are invalid
            TypeError: If parameters are of wrong type
            KeyError: If required parameters are missing
        """
        for expected_init_input in self._init_input_spec:
            try:
                if expected_init_input.name not in init_kwargs:
                    raise KeyError(f"{expected_init_input.name} arg is not given in initialization args.")
                if not isinstance(init_kwargs[expected_init_input.name], expected_init_input.type):
                    raise TypeError(f"{expected_init_input.name} expected type: {expected_init_input.type}, actual type: {type(init_kwargs[expected_init_input.name])}")
            except Exception as e:
                raise e
            
        self._validate_reset_targets()
            
    def _validate_reset_targets(self) -> None:
        """Validate reset targets specification."""
        if not isinstance(self._reset_targets_spec, list):
            raise TypeError("reset_targets must be a list")
        
        if not self._reset_targets_spec:
            raise ValueError("reset_targets cannot be empty")
        
        for i, target in enumerate(self._reset_targets_spec):
            if not isinstance(target, InputSpec):
                raise TypeError(f"reset_targets[{i}] must be an InputSpec object")
            
            if not hasattr(target, 'name') or not isinstance(target.name, str):
                raise TypeError(f"reset_targets[{i}] must have a valid 'name' attribute as string")
            
            if not hasattr(target, 'type') or not isinstance(target.type, type):
                raise TypeError(f"reset_targets[{i}] must have a valid 'type' attribute as type")
    
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
            RuntimeError: If guard is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError(f'{self.__class__.__name__} reset is not initialized')
        
        # Validate expected state inputs
        for expected_state_input in self._state_input_spec:
            if expected_state_input.name not in state_kwargs:
                raise KeyError(f"Required state input '{expected_state_input.name}' is missing")
            if not isinstance(state_kwargs[expected_state_input.name], expected_state_input.type):
                raise TypeError(f"State input '{expected_state_input.name}' expected type: {expected_state_input.type}, actual type: {type(state_kwargs[expected_state_input.name])}")   

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
        
        target_names = {target.name for target in self._reset_targets_spec}
        output_names = set(reset_output.keys())
        
        missing_names = target_names - output_names
        if missing_names:
            raise KeyError(f"Reset output missing required keys: {missing_names}")
        
        extra_names = output_names - target_names
        if extra_names:
            self.logger.warning(f"Reset output contains unexpected keys: {extra_names}")
        
        # Validate types
        target_types = {target.name: target.type for target in self._reset_targets_spec}
        for name, value in reset_output.items():
            if name in target_types:
                expected_type = target_types[name]
                if not isinstance(value, expected_type):
                    raise TypeError(f"Reset output '{name}' expected type {expected_type.__name__}, got {type(value).__name__}")

    @classmethod
    def init_input_spec_names(cls) -> List[InputSpec]:
        """Return a list of initialization inputs expected for the __init__, names and types"""
        return [spec.name for spec in cls._init_input_spec]
    
    @classmethod
    def init_input_spec_types(cls) -> List[str]: 
        """Return a list of names of initialization args"""
        return [spec.type for spec in cls._init_input_spec]
    
    @classmethod
    def state_input_spec_names(cls) -> List[InputSpec]:
        """Return a list of state inputs expected for the __call__, names and types"""
        return [spec.name for spec in cls._state_input_spec]
    
    @classmethod
    def state_input_spec_types(cls) -> List[str]: 
        """Return a list of state input names"""
        return [spec.type for spec in cls._state_input_spec]

    @classmethod
    def reset_target_spec_names(cls) -> List[InputSpec]:
        """Return a list of reset target names and types for the __call__"""
        return [spec.name for spec in cls._reset_targets_spec]
    
    @classmethod
    def reset_target_spec_types(cls) -> List[str]: 
        """Return a list of reset target names"""
        return [spec.type for spec in cls._reset_targets_spec]

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
            'description': class_doc.strip().split('\n')[0] if class_doc else "No description",
            'is_initialized': self.is_initialized,
            'init_input_spec_names': self.init_input_spec_names(),
            'init_input_spec_types': self.init_input_spec_types(),
            'state_input_spec_names': self.state_input_spec_names(),
            'state_input_spec_types': self.state_input_spec_types(),
            'reset_target_spec_names': self.reset_target_spec_names(),
            'reset_target_spec_types': self.reset_target_spec_types(),
        }
    
    def __repr__(self) -> str:
        """String representation of the reset function."""
        target_names = [target.name for target in self._reset_targets_spec] if self.is_initialized else []
        return f"{self.__class__.__name__}(initialized={self.is_initialized}, targets={target_names})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Reset Function: {self.__class__.__name__} (targets: {len(self._reset_targets_spec) if self.is_initialized else 0})"