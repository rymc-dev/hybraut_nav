"""
Hybrid Automaton Guard Abstract Base Class

This abstract class defines the interface for guard functions in the hybrid automaton framework.
Reset functions are executed during mode transitions to modify continuous state variables.

All reset implementations must inherit from this class and implement the required methods.
Reset functions are called when transitioning between modes and can modify one or more
continuous states based on the current system state and transition context.

Example Usage:
    class RemoveFirstWaypointReset(HybridAutomatonReset):
        def __init__(self, min_waypoints: int = 1):
            self.min_waypoints = min_waypoints
            
        def __call__(self, waypoints_state: WaypointsState) -> Tuple[WaypointsState]:
            # Implementation logic here
            return (updated_waypoints_state,)
"""


from abc import ABC, abstractmethod
from typing import Tuple, Any, Dict, Optional, Union
from colav_interfaces.msg import WaypointsState, AgentState, ObstaclesState
import rclpy
from rclpy.logging import get_logger

class Guard(ABC):
    """
    Abstract base class for hybrid automaton reset functions.
    
    Reset functions are executed during mode transitions to modify continuous
    state variables. They provide a mechanism to update system state when
    transitioning between different behavioral modes.
    
    Attributes:
        logger: ROS2 logger instance for debugging and information output
        is_initialized: Flag indicating if the reset has been properly initialized
    """

    def __init__(self, **init_kwargs):
        """
        Initialize the reset function with static configuration parameters.
        
        This initialization is called once during the hybrid automaton configuration
        phase. Use this method to set up any static parameters, constants, or
        pre-computed values that don't change during execution.
        
        Args:
            *args: Variable positional arguments for reset configuration
            **kwargs: Variable keyword arguments for reset configuration
            
        Raises:
            ValueError: If invalid configuration parameters are provided
            TypeError: If required parameters are missing or of wrong type
        """
        self.logger = get_logger(self.__class__.__name__)
        self.is_initialized = False
        self._validate_initialization(**init_kwargs)
        self.is_initialized = True

    @abstractmethod
    def __call__(self, **state_kwargs) -> bool:
        """
        Execute the reset function with current state inputs.
        
        This method is called during mode transitions to modify continuous states.
        It receives the current state values and returns updated state values.
        
        Args:
            *kwargs: Variable number of state kwargs inputs (e.g., WaypointsState, 
                          AgentState, ObstaclesState) as defined in the configuration
                          
        Returns:
            Tuple[Any, ...]: Tuple of updated state objects in the same order as
                           specified in the configuration's state_outputs field
                           
        Raises:
            RuntimeError: If reset is called before proper initialization
            ValueError: If state inputs are invalid or incompatible
            TypeError: If state inputs don't match expected types
            
        Example:
            # For a reset that modifies waypoints
            def __call__(self, waypoints_state: WaypointsState) -> Tuple[WaypointsState]:
                updated_waypoints = self._process_waypoints(waypoints_state)
                return (updated_waypoints,)
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before calling")
        
        # Validate inputs
        self._validate_states(**state_kwargs)

    def _validate_initialization(self, **init_kwargs) -> None:
        """
        Validate initialization parameters.
        
        Override this method in subclasses to implement custom validation
        of initialization parameters.
        
        Args:
            *args: Positional arguments passed to __init__
            **kwargs: Keyword arguments passed to __init__
            
        Raises:
            ValueError: If parameters are invalid
            TypeError: If parameters are of wrong type
        """
        pass
    
    def _validate_states(self, **state_kwargs) -> None:
        """
        Validate state inputs before processing.
        
        Override this method in subclasses to implement custom validation
        of state inputs.
        
        Args:
            *state_inputs: State input objects to validate
            
        Raises:
            ValueError: If state inputs are invalid
            TypeError: If state inputs are of wrong type
        """
        pass
        
    def get_guard_info(self) -> Dict[str, Any]:
        """
        Get information about this reset function.
        
        Returns:
            Dict[str, Any]: Dictionary containing reset metadata including
                          class name, initialization status, and configuration
        """
        class_doc = self.__class__.__doc__
        return {
            'class_name': self.__class__.__name__,
            'module': self.__class__.__module__,
            'is_initialized': self.is_initialized,
            'description': class_doc.strip().split('\n')[0] if class_doc else "No description"
        }
    
    def __repr__(self) -> str:
        """String representation of the guard function."""
        return f"{self.__class__.__name__}(initialized={self.is_initialized})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Guard Function: {self.__class__.__name__}"
        
    