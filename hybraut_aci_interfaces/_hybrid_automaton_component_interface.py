""" 
interface for hybrid automaton core_interfaces
for the core compoenents, Guards, Resets, Dynamics
and Invariants interfaces which are utilized for 
implementations of those classes for creation of 
hybrid automaton.
"""
from abc import ABC, abstractmethod
from typing import List
from rclpy.logging import get_logger
from typing import Any, ClassVar, Dict, Type
from ._io_spec import IOSpec


class HybridComponentInterface(ABC):
    """
    Base interface for all hybrid automaton components.
    
    This interface provides common functionality for initialization, validation,
    and introspection that all hybrid automaton components share. It standardizes
    the component lifecycle and provides consistent error handling.
    
    All hybrid automaton components (dynamics, guards, invariants, resets) inherit
    from this base interface.
    
    Attributes:
        logger: ROS2 logger instance for debugging and information output
        is_initialized: Flag indicating if the component has been properly initialized
    """
    
    # Class-level specifications that subclasses should override
    _component_type: str = ""
    _init_input_spec: ClassVar[List[IOSpec]] = []
    _state_input_spec: ClassVar[List[IOSpec]] = []
    _evaluation_output_spec: Any = None
    
    def __init__(self, **init_kwargs):
        """
        Initialize the component with configuration parameters.
        
        Args:
            **init_kwargs: Variable keyword arguments for component configuration
            
        Raises:
            ValueError: If invalid configuration parameters are provided
            TypeError: If required parameters are missing or of wrong type
        """
        self.logger = get_logger(self.__class__.__name__)
        self.is_initialized = False
        
        # Validate and set initialization parameters
        self._validate_initialization(**init_kwargs)
        self._set_instance_initialization(**init_kwargs)
        
        # Allow subclasses to perform additional initialization
        self._post_init_hook()
        
        self.is_initialized = True
    
    def _set_instance_initialization(self, **init_kwargs) -> None:
        """
        Set instance attributes from initialization kwargs.
        
        Override this method in subclasses to customize how initialization
        parameters are processed and stored.
        """
        for key, value in init_kwargs.items():
            setattr(self, key, value)
    
    def _post_init_hook(self) -> None:
        """
        Hook method called after initialization but before marking as initialized.
        
        Override this method in subclasses to perform additional setup
        that depends on initialization parameters being set.
        """
        pass
    
    def _validate_initialization(self, **init_kwargs) -> None:
        """
        Validate initialization parameters against the component's specification.
        
        Args:
            **init_kwargs: Keyword arguments passed to __init__
            
        Raises:
            ValueError: If parameters are invalid
            TypeError: If parameters are of wrong type
            KeyError: If required parameters are missing
        """
        for expected_init_input in self._init_input_spec:
            if expected_init_input.name not in init_kwargs:
                raise KeyError(f"Missing required initialization parameter: '{expected_init_input.name}'")
            
            value = init_kwargs[expected_init_input.name]
            if not isinstance(value, expected_init_input.type):
                raise TypeError(
                    f"Initialization parameter '{expected_init_input.name}' expected type: "
                    f"{expected_init_input.type.__name__}, got: {type(value).__name__}"
                )
    
    def _validate_states(self, **state_kwargs) -> None:
        """
        Validate state inputs against the component's specification.
        
        Args:
            **state_kwargs: State input keyword arguments to validate
            
        Raises:
            ValueError: If state inputs are invalid
            TypeError: If state inputs are of wrong type
            KeyError: If required state inputs are missing
            RuntimeError: If component is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError(f'{self.__class__.__name__} component is not initialized')
        
        for expected_state_input in self._state_input_spec:
            if expected_state_input.name not in state_kwargs:
                raise KeyError(f"Missing required state input: '{expected_state_input.name}'")
            
            value = state_kwargs[expected_state_input.name]
            if not isinstance(value, expected_state_input.type):
                raise TypeError(
                    f"State input '{expected_state_input.name}' expected type: "
                    f"{expected_state_input.type.__name__}, got: {type(value).__name__}"
                )
            
    @abstractmethod
    def _evaluate(self, **state_kwargs) -> Any:
        """
        Perform the runtime evaluation for the component.

        This method must be implemented by all subclasses. It defines the core
        logic of the component based on the provided state inputs.

        Args:
            **state_kwargs: Arbitrary keyword arguments representing state input.

        Returns:
            Any: The result of evaluating the component logic.

        Raises:
            RuntimeError: If evaluation cannot be performed.
        """
        pass

    def _validate_evaluation_output(self, output: Any):
        """
        Validate the output returned from _evaluate.

        Subclasses may override this to enforce output constraints.

        Args:
            output (Any): Output from _evaluate.

        Raises:
            ValueError: If the output is not valid.
        """
        if not isinstance(output, self._evaluation_output_type):
            raise ValueError('output of runtime component evaluation wrong type.')
    
    def __call__(self, **state_kwargs) -> Any:
        """
        Execute the component's main functionality.

        This method handles the full lifecycle:
        1. Initialization check
        2. Input validation
        3. Evaluation
        4. Output validation

        Args:
            **state_kwargs: Arbitrary keyword arguments representing state input.

        Returns:
            Any: The result of evaluating the component logic.

        Raises:
            RuntimeError: If the component is not initialized.
            ValueError: If state inputs or evaluation output are invalid.
            TypeError: If input types are incorrect.
            KeyError: If required state fields are missing.
        """
        if not self.is_initialized:
            raise RuntimeError(f"{self.__class__.__name__} must be initialized before calling.")

        self._validate_states(**state_kwargs)

        result = self._evaluate(**state_kwargs)

        self._validate_evaluation_output(result)

        return result
    
    # Introspection methods
    @classmethod
    def get_init_input_spec_names(cls) -> List[str]:
        """Return list of initialization input names."""
        return [spec.name for spec in cls._init_input_spec]
    
    @classmethod
    def get_init_input_spec_types(cls) -> List[Type]:
        """Return list of initialization input types."""
        return [spec.type for spec in cls._init_input_spec]
    
    @classmethod
    def get_state_input_spec_names(cls) -> List[str]:
        """Return list of state input names."""
        return [spec.name for spec in cls._state_input_spec]
    
    @classmethod
    def get_state_input_spec_types(cls) -> List[Type]:
        """Return list of state input types."""
        return [spec.type for spec in cls._state_input_spec]
    
    def get_component_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about this component.
        
        Returns:
            Dictionary containing component metadata, specifications, and status
        """
        class_doc = self.__class__.__doc__
        return {
            'class_name': self.__class__.__name__,
            'module': self.__class__.__module__,
            'component_type': self._get_component_type(),
            'description': class_doc.strip().split('\n')[0] if class_doc else "No description",
            'is_initialized': self.is_initialized,
            'init_input_spec_names': self.get_init_input_spec_names(),
            'init_input_spec_types': [t.__name__ for t in self.get_init_input_spec_types()],
            'state_input_spec_names': self.get_state_input_spec_names(),
            'state_input_spec_types': [t.__name__ for t in self.get_state_input_spec_types()],
        }
    
    def _get_component_type(self) -> str:
        """Get the component type name for introspection."""
        return self._component_type
    
    def __repr__(self) -> str:
        """String representation of the component."""
        return f"{self.__class__.__name__}(initialized={self.is_initialized})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        component_type = self._get_component_type()
        return f"Hybrid Automaton {component_type}: {self.__class__.__name__}"