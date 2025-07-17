"""
Hybrid Automaton Reset Interface

This interface defines the contract for reset functions in the hybrid automaton framework.
Reset functions are used to update state variables when a transition between modes occurs.

All reset implementations must inherit from this interface and implement the required methods.
Resets are executed during the hybrid automaton's transition to update system state
based on the current conditions and reset logic.

Example Usage:
    class WaypointReset(ResetInterface):
        _init_input_spec = [
            InputSpec.create_input_spec("waypoint_increment", int)
        ]
        _state_input_spec = [
            InputSpec.create_input_spec("agent_state", AgentState),
            InputSpec.create_input_spec("waypoints_state", WaypointsState)
        ]
        _reset_targets_spec = [
            InputSpec.create_input_spec("current_waypoint_index", int),
            InputSpec.create_input_spec("waypoint_position", tuple)
        ]
        
        def __call__(self, **state_kwargs) -> Dict[str, Any]:
            super().__call__(**state_kwargs)
            # Implementation logic here
            return {
                'current_waypoint_index': new_index,
                'waypoint_position': new_position
            }
"""

from abc import abstractmethod
from typing import Any, Dict, List, ClassVar, Type
from .hybrid_automaton_component_interface import IOSpec, HybridAutomatonComponentInterface


class ResetInterface(HybridAutomatonComponentInterface):
    """
    Interface for hybrid automaton reset functions.
    
    Reset functions update state variables during hybrid automaton transitions.
    They determine what state values should be modified when transitioning 
    from one mode to another based on the current system state.
    
    This interface extends the base HybridAutomatonComponentInterface to provide
    reset-specific functionality including target validation and output verification.
    
    Attributes:
        logger: ROS2 logger instance for debugging and information output
        is_initialized: Flag indicating if the reset has been properly initialized
        reset_targets: List of objects that will be updated by this reset function
    """


    _reset_targets_spec: ClassVar[List[IOSpec]] = []

    def _post_init_hook(self) -> None:
        """
        Hook method called after initialization to validate reset targets.
        
        This ensures that reset targets are properly specified during initialization.
        """
        super()._post_init_hook()
        self._validate_reset_targets()

    @abstractmethod
    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:
        return super()._evaluate(**state_kwargs)

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
                super().__call__(**state_kwargs)  # Always call parent for validation
                new_index = self._calculate_next_waypoint(agent_state, waypoints_state)
                new_position = waypoints_state.waypoints[new_index]
                return {
                    'current_waypoint_index': new_index,
                    'waypoint_position': new_position
                }
        """
        # Call parent validation
        return super().__call__(**state_kwargs)
        
        # Subclasses should implement the actual reset logic after calling super()
        # and return a dictionary of {name: value} pairs

    def _validate_evaluation_output(self, output):
        self._validate_reset_output(output)

    def _validate_reset_targets(self) -> None:
        """
        Validate reset targets specification.
        
        Raises:
            TypeError: If reset targets are not properly specified
            ValueError: If reset targets are empty or invalid
        """
        if not isinstance(self._reset_targets_spec, list):
            raise TypeError("_reset_targets_spec must be a list")
        
        if not self._reset_targets_spec:
            raise ValueError("_reset_targets_spec cannot be empty")
        
        for i, target in enumerate(self._reset_targets_spec):
            if not isinstance(target, IOSpec):
                raise TypeError(f"_reset_targets_spec[{i}] must be an InputSpec object")
            
            if not hasattr(target, 'name') or not isinstance(target.name, str):
                raise TypeError(f"_reset_targets_spec[{i}] must have a valid 'name' attribute as string")
            
            if not hasattr(target, 'type') or not isinstance(target.type, type):
                raise TypeError(f"_reset_targets_spec[{i}] must have a valid 'type' attribute as type")

    def _validate_reset_output(self, reset_output: Dict[str, Any]) -> None:
        """
        Validate the output of the reset function against target specifications.
        
        This method checks that the returned dictionary contains the expected
        keys and value types as defined in _reset_targets_spec.
        
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

    # Reset-specific introspection methods
    @classmethod
    def get_reset_target_spec_names(cls) -> List[str]:
        """Return a list of reset target names."""
        return [spec.name for spec in cls._reset_targets_spec]
    
    @classmethod
    def get_reset_target_spec_types(cls) -> List[Type]:
        """Return a list of reset target types."""
        return [spec.type for spec in cls._reset_targets_spec]

    def get_component_info(self) -> Dict[str, Any]:
        """
        Get information about this reset function.
        
        Returns:
            Dict[str, Any]: Dictionary containing reset metadata including
                          class name, initialization status, target objects, and configuration
        """
        # Get base component info and add reset-specific details
        info = super().get_component_info()
        info.update({
            'reset_target_spec_names': self.get_reset_target_spec_names(),
            'reset_target_spec_types': [t.__name__ for t in self.get_reset_target_spec_types()],
            'reset_specific_info': {
                'updates_state_variables': True,
                'returns_dictionary': True,
                'target_count': len(self._reset_targets_spec)
            }
        })
        return info

    def _get_component_type(self) -> str:
        return "Reset"

    def __repr__(self) -> str:
        """String representation of the reset function."""
        target_names = [target.name for target in self._reset_targets_spec] if self.is_initialized else []
        return f"{self.__class__.__name__}(initialized={self.is_initialized}, targets={target_names})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        target_count = len(self._reset_targets_spec) if hasattr(self, '_reset_targets_spec') else 0
        return f"Reset Function: {self.__class__.__name__} (targets: {target_count})"