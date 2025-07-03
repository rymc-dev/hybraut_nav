from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from collections import namedtuple
from rclpy.logging import get_logger


class DynamicsABC(ABC):
    """
    Abstract base class for hybrid automaton dynamics functions.
    
    Dynamics functions define how the system evolves over time in a given mode,
    based on current system state and possibly control inputs.
    
    Subclasses must implement the __call__ method to compute the output.
    """

    def __init__(self, output_type: Type[namedtuple], **init_kwargs):
        """
        Initialize the dynamics function with the required output structure.
        
        Args:
            output_type: A namedtuple class defining the expected output structure.
            **init_kwargs: Additional configuration parameters.
        """
        self.logger = get_logger(self.__class__.__name__)
        if not isinstance(output_type, type) or not hasattr(output_type, "_fields"):
            raise TypeError("output_type must be a namedtuple type")
        
        self.output_type = output_type
        self.is_initialized = False
        self._validate_initialization(**init_kwargs)
        self.is_initialized = True

    @abstractmethod
    def __call__(self, **state_kwargs) -> Any:
        """
        Compute the dynamics output based on the current system state.
        
        Args:
            **state_kwargs: Keyword arguments representing state inputs.
        
        Returns:
            An instance of the configured output_type.
        
        Raises:
            RuntimeError: If not initialized
            ValueError / TypeError: If state inputs are invalid
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before calling")

        self._validate_states(**state_kwargs)
        # Implementation logic should return self.output_type(...)
    
    def _validate_initialization(self, **init_kwargs) -> None:
        """Validate static initialization parameters."""
        pass
    
    def _validate_states(self, **state_kwargs) -> None:
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} is not initialized")

    def get_dynamics_info(self) -> Dict[str, Any]:
        class_doc = self.__class__.__doc__
        return {
            'class_name': self.__class__.__name__,
            'module': self.__class__.__module__,
            'is_initialized': self.is_initialized,
            'output_type': self.output_type.__name__,
            'description': class_doc.strip().split('\n')[0] if class_doc else "No description"
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(output_type={self.output_type.__name__}, initialized={self.is_initialized})"

    def __str__(self) -> str:
        return f"Dynamics Function: {self.__class__.__name__} (Output: {self.output_type.__name__})"
