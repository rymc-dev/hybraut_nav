from dataclasses import dataclass, field
from automaton_models.hybrid.aci_interfaces import (
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
from automaton_models.hybrid.aci_interfaces.hybrid_automaton_component_interface import HybridAutomatonComponentInterface
from builtin_interfaces.msg import Time, Duration
from .context.evaluation_context import EvaluationContext

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



fields based on result
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