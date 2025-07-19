from dataclasses import dataclass, field
from automaton.core_interfaces import (
    GuardInterface,
    ResetInterface,
    InvariantInterface,
    DynamicsInterface
)
from builtin_interfaces.msg import Time
from typing import Optional, Dict, Any, Type, List
from automaton_interfaces.msg import (
    AutomatonGuardEvaluation, 
    AutomatonReset, 
    AutomatonInvariantStatus, 
    AutomatonDynamicsEvaluation
)
from abc import ABC, abstractmethod
import importlib
from automaton.core_interfaces.hybrid_automaton_component_interface import HybridAutomatonComponentInterface
from builtin_interfaces.msg import Time, Duration

def import_class(module_path: str, class_name: str) -> Type[Any]:
    """
    Dynamically import and return a class from a module.
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Cannot import '{class_name}' from '{module_path}': {e}")

from .automaton_registrys import StateRegistry

@dataclass
class EvaluationContext:
    """
    Context class that holds evaluation state and parameters.
    initialized on automaton evaluation time, and passed to evaluation
    functions.
    """
    states: StateRegistry
    current_mode: int
    stamp: Time
    metadata: Dict[str, Any]

    def get_state_values(state_names) -> Dict[str, Any]:
        pass

    def get_state_age(state_name) -> Duration:
        pass


    def get_event_history() -> None:
        """not sure how to implement this yet."""
        pass






@dataclass
class ComponentPath:
    _module: str
    _class_name: str

    def get_component_class(self) -> Any:
        cls = import_class(self._module, self._class_name)
        return cls

    @classmethod
    def load_component_from_famd(cls, component_dict: dict):
        return cls(
            _module=component_dict['module'],
            _class_name=component_dict['class_name']
        )


@dataclass
class WrapperInterface(ABC):
    _name: str
    _component_class: Type[HybridAutomatonComponentInterface]
    _component_instance: Optional[HybridAutomatonComponentInterface] = field(default=None, init=False)
    _configuration: Optional[Dict[str, Any]] = None
    _cache_enabled: bool = True
    _cache_ttl: float = 1.0  # Time-to-live in seconds for caching evaluation results
    _last_evaluation: Optional[Any] = field(default=None, init=False)
    _last_evaluation_time: Optional[Time] = field(default=None, init=False)
    _is_activated: bool = field(default=False, init=False)

    def __post_init__(self):
        """
        Called automatically after dataclass initialization.
        Validates the component configuration against the expected constructor arguments.
        """
        if self._configuration is None:
            raise ValueError("Configuration must be provided to initialize the wrapper.")

        expected_names: List[str] = self._component_class.get_init_input_spec_names()
        expected_types: List[Type] = self._component_class.get_init_input_spec_types()

        for config_name, expected_type in zip(expected_names, expected_types):
            if config_name not in self._configuration:
                raise ValueError(
                    f"Missing configuration for required argument '{config_name}' in component '{self._component_class.__name__}'."
                )
            if not isinstance(self._configuration[config_name], expected_type):
                raise TypeError(
                    f"Invalid type for configuration key '{config_name}': "
                    f"expected {expected_type.__name__}, got {type(self._configuration[config_name]).__name__}."
                )

        self.__post_init_hook__()

    def __post_init_hook__(self):
        """
        Optional hook for subclasses to run additional validation or setup after post-init.
        """
        pass

    def __pre_evaluate_hook__(self, context: EvaluationContext):
        """
        Optional hook to validate the evaluation context before calling `evaluate`.
        Subclasses may override this to perform schema checks or consistency validation.
        """
        if not self._is_activated:
            raise RuntimeError('Tried to evaluate but the component is not activated')

    def _is_cache_valid(self, context: EvaluationContext) -> bool:
        """
        Check if cached result is still valid based on TTL and context.
        """
        if not self._cache_enabled or self._last_evaluation_time is None:
            return False
        
        if context.current_time is None:
            return False
            
        # Simple TTL check - in real implementation you'd convert Time to seconds
        time_diff = context.current_time.sec - self._last_evaluation_time.sec
        return time_diff < self._cache_ttl

    @abstractmethod
    def _evaluate(self, context: EvaluationContext) -> Any:
        """
        Abstract method that must be implemented by subclasses to perform evaluation logic.
        """
        pass

    def __call__(self, context: EvaluationContext) -> Any:
        self.__pre_evaluate_hook__(context)
        
        # Check cache first
        if self._is_cache_valid(context):
            return self._last_evaluation
        
        # Perform evaluation
        result = self._evaluate(context)
        
        # Update cache
        if self._cache_enabled:
            self._last_evaluation = result
            self._last_evaluation_time = context.current_time
        
        return result

    def activate(self):
        """
        Instantiates the component using the provided configuration dictionary.
        Sets the `_is_activated` flag to True.
        """
        if not self._configuration:
            raise RuntimeError("Cannot activate component without valid configuration.")
        self._component_instance = self._component_class(**self._configuration)
        self._is_activated = True

    def deactivate(self):
        """
        Deactivates the component and clears the instance.
        """
        self._component_instance = None
        self._is_activated = False

    def clear_cache(self) -> None:
        """
        Clears the cached evaluation result.
        """
        self._last_evaluation = None
        self._last_evaluation_time = None


@dataclass
class InvariantWrapper(WrapperInterface):
    """
    Wrapper for invariant components that evaluate conditions that must hold within a state.
    """
    _component_class: Type[InvariantInterface]

    def _evaluate(self, context: EvaluationContext) -> AutomatonInvariantStatus:
        if self._component_instance is None:
            raise RuntimeError("Component instance is None. Call activate() first.")
        
        # Delegate to the actual component instance
        result = self._component_instance(context)
        
        # Ensure we return the correct message type
        if isinstance(result, AutomatonInvariantStatus):
            return result
        else:
            # Convert or wrap the result if needed
            status = AutomatonInvariantStatus()
            # Set appropriate fields based on result
            return status
    
    @classmethod
    def load_invariant_from_famd(cls, invariant_name: str, invariant_dict: dict):
        component_path = ComponentPath.load_component_from_famd(invariant_dict)
        configuration = invariant_dict.get('configuration', None)
        component_class = component_path.get_component_class()
        return cls(
            _name=invariant_name,
            _component_class=component_class,
            _configuration=configuration
        )


@dataclass
class GuardWrapper(WrapperInterface):
    """
    Wrapper for guard components that evaluate transition conditions.
    """
    _component_class: Type[GuardInterface]

    def _evaluate(self, context: EvaluationContext) -> AutomatonGuardEvaluation:
        if self._component_instance is None:
            raise RuntimeError("Component instance is None. Call activate() first.")
        
        # Delegate to the actual component instance
        result = self._component_instance(context)
        
        # Ensure we return the correct message type
        if isinstance(result, AutomatonGuardEvaluation):
            return result
        else:
            # Convert or wrap the result if needed
            evaluation = AutomatonGuardEvaluation()
            # Set appropriate fields based on result
            return evaluation
        
    @classmethod
    def load_guard_from_famd(cls, guard_name: str, guard_dict: Dict[str, Any]) -> 'GuardWrapper':
        component_path = ComponentPath.load_component_from_famd(guard_dict)
        component_class = component_path.get_component_class()
        configuration = guard_dict.get('configuration', None)
        return cls( 
            _name=guard_name,
            _component_class=component_class,
            _configuration=configuration
        )


@dataclass
class ResetWrapper(WrapperInterface):
    """
    Wrapper for reset components that handle state transitions.
    """
    _component_class: Type[ResetInterface]

    def _evaluate(self, context: EvaluationContext) -> AutomatonReset:
        if self._component_instance is None:
            raise RuntimeError("Component instance is None. Call activate() first.")
        
        # Delegate to the actual component instance
        result = self._component_instance(context)
        
        # Ensure we return the correct message type
        if isinstance(result, AutomatonReset):
            return result
        else:
            # Convert or wrap the result if needed
            reset = AutomatonReset()
            # Set appropriate fields based on result
            return reset
        
    @classmethod
    def load_reset_from_famd(cls, reset_name: str, reset_dict: Dict[str, Any]) -> 'ResetWrapper':
        component_path = ComponentPath.load_component_from_famd(reset_dict)
        component_class = component_path.get_component_class()
        configuration = reset_dict.get('configuration', None)
        return cls( 
            _name=reset_name,
            _component_class=component_class,
            _configuration=configuration
        )


@dataclass
class DynamicsWrapper(WrapperInterface):
    """
    Wrapper for dynamics components that handle continuous evolution within states.
    """
    _component_class: Type[DynamicsInterface]

    def _evaluate(self, context: EvaluationContext) -> AutomatonDynamicsEvaluation:
        if self._component_instance is None:
            raise RuntimeError("Component instance is None. Call activate() first.")
        
        # Delegate to the actual component instance
        result = self._component_instance(context)
        
        # Ensure we return the correct message type
        if isinstance(result, AutomatonDynamicsEvaluation):
            return result
        else:
            # Convert or wrap the result if needed
            evaluation = AutomatonDynamicsEvaluation()
            # Set appropriate fields based on result
            return evaluation

    @classmethod
    def load_dynamics_from_famd(cls, dynamics_name: str, dynamics_dict: Dict[str, Any]) -> 'DynamicsWrapper':
        component_path = ComponentPath.load_component_from_famd(dynamics_dict)
        component_class = component_path.get_component_class()
        configuration = dynamics_dict.get('configuration', None)
        return cls( 
            _name=dynamics_name,
            _component_class=component_class,
            _configuration=configuration
        )