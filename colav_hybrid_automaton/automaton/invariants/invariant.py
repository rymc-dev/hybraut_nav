"""
Hybrid Automaton Invariant Abstract Base Class

This abstract class defines the interface for invariant functions in the hybrid automaton framework.
Invariant functions are used to determine whether a transition staying in a mode without transitioning is valid.

All invariant implementations must inherit from this class and implement the required methods.
Invariants are evaluated during the hybrid automaton's execution to determine  if it is allowed
to stay in a mode without transitioning every evaluation.

Example Usage:
    class CanIStayInMODEInvariant(Invariant):

        def __call__(self, state_kwargs) -> bool:
            return True
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, List, ClassVar
from rclpy.logging import get_logger
from automaton._internal.types import InputSpec


class InvariantABC(ABC):
    """
    Abstract base class for hybrid automaton invariant functions.
    
    Invariant functions evaluate if we can stay in the current mode based on
    the system state
    
    Attributes:
        logger: ROS2 logger instance for debugging and information output
        is_initialized: Flag indicating if the invariant has been properly initialized
    """
    
    _init_input_spec: ClassVar[List[InputSpec]] = []
    _state_input_spec: ClassVar[List[InputSpec]] = []

    def __init__(self, **init_kwargs):
        """
        Initialize the invariant function with static configuration parameters.
        
        This initialization is called once during the hybrid automaton configuration
        phase. Use this method to set up any static parameters, constants, or
        pre-computed values that don't change during execution.
        
        Args:
            **init_kwargs: Variable keyword arguments for invariant configuration
            
        Raises:
            ValueError: If invalid configuration parameters are provided
            TypeError: If required parameters are missing or of wrong type
        """
        self.logger = get_logger(self.__class__.__name__)
        self.is_initialized = False
        self._validate_initialization(**init_kwargs)
        self._set_instance_initialization(**init_kwargs)
        self.is_initialized = True

    def _set_instance_initialization(self, **init_kwargs):
        """Set instance attributes from initialization kwargs."""
        for key, value in init_kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def __call__(self, **state_kwargs) -> bool:
        """
        Execute the invariant function with current state inputs.
        
        This method is called during hybrid automaton execution to evaluate
        whether a twhether we can stay in current mode. It receives the current state values
        and returns a boolean indicating if the invariant evaluation is satisfied.
        
        Args:
            **state_kwargs: Variable keyword arguments containing state inputs
                          (e.g., agent_state, waypoints_state, obstacles_state)
                          as defined in the hybrid automaton configuration
                          
        Returns:
            bool: True if the invariant condition is satisfied and transition should occur,
                 False otherwise
                           
        Raises:
            RuntimeError: If invariant is called before proper initialization
            ValueError: If state inputs are invalid or incompatible
            TypeError: If state inputs don't match expected types
            KeyError: If required state inputs are missing
            
        Example:
            def __call__(self, agent_state: AgentState, waypoints_state: WaypointsState) -> bool:
                distance = self._calculate_distance(agent_state, waypoints_state)
                return distance <= self.distance_threshold
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before calling")
        
        # Validate inputs
        self._validate_states(**state_kwargs)
        
        # Subclasses should implement the actual invariant logic after calling super()

    def _validate_initialization(self, **init_kwargs) -> None:
        """
        Validate initialization parameters.
        
        Override this method in subclasses to implement custom validation
        of initialization parameters.
        
        Args:
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
            RuntimeError: If invariant is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError(f'{self.__class__.__name__} invariant is not initialized')
        
        # Validate expected state inputs
        for expected_state_input in self._state_input_spec:
            if expected_state_input.name not in state_kwargs:
                raise KeyError(f"Required state input '{expected_state_input.name}' is missing")
            if not isinstance(state_kwargs[expected_state_input.name], expected_state_input.type):
                raise TypeError(f"State input '{expected_state_input.name}' expected type: {expected_state_input.type}, actual type: {type(state_kwargs[expected_state_input.name])}")   

    @classmethod
    def init_input_spec_names(cls) -> List[InputSpec]:
        """Return a list of initialization inputs expected for the __init__, names and types"""
        return [init_input.name for init_input in cls._init_input_spec]
    
    @classmethod
    def init_input_spec_types(cls) -> List[str]:
        """returns a list of initialization input names passed for the __init__"""
        return [init_input.type for init_input in cls._init_input_spec]
    
    @classmethod
    def state_input_spec_names(cls) -> List[InputSpec]:
        """Return a list of state inputs expected for the __call__, names and types"""
        return [state_input.name for state_input in cls._state_input_spec]

    @classmethod
    def state_input_spec_types(cls) -> List[str]:
        """Returns a list of state input names required for the __call__, just names"""
        return [state_input.type for state_input in cls._state_input_spec]

    def get_invariant_info(self) -> Dict[str, Any]:
        """
        Get information about this invariant function.
        
        Returns:
            Dict[str, Any]: Dictionary containing invariant metadata including
                          class name, initialization status, and configuration
        """
        class_doc = self.__class__.__doc__
        return {
            'class_name': self.__class__.__name__,
            'module': self.__class__.__module__,
            'is_initialized': self.is_initialized,
            'state_input_spec': self._state_input_spec,
            'init_input_spec': self._init_input_spec,
            'description': class_doc.strip().split('\n')[0] if class_doc else "No description"
        }
    
    def __repr__(self) -> str:
        """String representation of the invariant function."""
        return f"{self.__class__.__name__}(initialized={self.is_initialized})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Invariant Function: {self.__class__.__name__}"