from dataclasses import dataclass
from automaton.core_interfaces import (
    GuardInterface,
    ResetInterface,
    InvariantInterface,
    DynamicsInterface
)
from builtin_interfaces.msg import Time
from typing import Optional, Dict, Any
from automaton_interfaces.msg import AutomatonGuardEvaluation, AutomatonReset, AutomatonInvariantStatus, AutomatonDynamicsEvaluation
from abc import ABC, abstractmethod
from typing import Type
import importlib
from typing import List, Type
from automaton.core_interfaces.hybrid_automaton_component_interface import HybridAutomatonComponentInterface

def import_class(module_path: str, class_name: str) -> Type[Any]:
    """
    Dynamically import and return a class from a module.
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Cannot import '{class_name}' from '{module_path}': {e}")

class EvaluationContext():
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
            _module = component_dict['module'],
            _class_name = component_dict['class_name']
        )

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type, List
from builtin_interfaces.msg import Time  # Replace with your actual source

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
            raise RuntimeError('tried to evaluate the component is not activated')

    @abstractmethod
    def _evaluate(self, context: EvaluationContext) -> Any:
        """
        Abstract method that must be implemented by subclasses to perform evaluation logic.
        """
        self.__pre_evaluate_hook__(context)
        ...

    def __call__(self, context) -> Any:
        self.__pre_evaluate_hook__(context)
        result = self._evaluate(context)
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
class GuardWrapper(WrapperInterface):

    def _evaluate(self, context: EvaluationContext) -> AutomatonGuardEvaluation:
        super()._evaluate(context=context)
        print ('hello there')
        return AutomatonGuardEvaluation()
        
    @classmethod
    def load_guard_from_famd(cls, guard_name:str, guard_dict: Dict[str, Any]) -> 'GuardWrapper':
        # assign component class in here
        
        component_path:ComponentPath= ComponentPath.load_component_from_famd(guard_dict)
        component_class = component_path.get_component_class()
        configuration = guard_dict.get('configuration', None)
        return cls( 
            _name=guard_name,
            _component_class=component_class,
            _configuration = configuration
        )

if __name__ == '__main__':
    guard = {
        "module": "automaton.common_behaviours.guards.boolean_flag_guard",
        "class_name": "BooleanFlagGuard",
        "configuration": {
            "expected_flag": True
        }
    }

    guard_wrapper: GuardWrapper = GuardWrapper.load_guard_from_famd(guard_name='los_clear_to_waypoint', guard_dict=guard)
    guard_wrapper.activate()
    guard_wrapper(context='context')
    print (guard_wrapper)


# @dataclass
# class ResetWrapper(WrapperInterface):
#     _reset: ResetInterface
    
#     def evaluate(self, context: EvaluationContext) -> AutomatonReset:
#         pass
        
#     @classmethod
#     def load_reset_from_famd(cls, reset_dict: Dict[str, Any]) -> 'ResetWrapper':
#         pass

# @dataclass
# class InvariantWrapper(WrapperInterface):
#     _invariant: InvariantInterface
    
#     def evaluate(self, context: EvaluationContext) -> AutomatonInvariantStatus:
#         pass
        
#     @classmethod
#     def load_reset_from_famd(cls, reset_dict: Dict[str, Any]) -> 'InvariantWrapper':
#         pass

# @dataclass
# class DynamicsWrapper(WrapperInterface):
#     _invariant: InvariantInterface
    
#     def evaluate(self, context: EvaluationContext) -> AutomatonDynamicsEvaluation:
#         pass
        
#     @classmethod
#     def load_dynamics_from_from_famd(cls, reset_dict: Dict[str, Any]) -> 'InvariantWrapper':
#         pass

# # class InvariantWrapper:
#     - name: str
#     - invariant: InvariantInterface
#     - violation_count: int
#     - max_violations: int
#     + evaluate_invariant(context: EvaluationContext) bool
#     + reset_violation_count()
#     + load_invariant_from_famd(data: Dict[str, Any]) InvariantWrapper


# class DynamicsWrapper:
#     - name: str
#     - dynamics: DynamicsInterface
#     + evaluate_dynamics(context: EvaluationContext) Any
#     + load_dynamics_from_famd(data: Dict[str, Any]) DynamicsWrapper