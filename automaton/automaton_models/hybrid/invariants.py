from .component_interfaces import WrapperInterface
from typing import Type, Dict, Any
from automaton_interfaces.msg import InvariantEvaluationMSG, InvariantEvaluationsMSG
from .context import EvaluationContext
from .aci_interfaces import InvariantInterface
from dataclasses import dataclass

@dataclass
class InvariantWrapper(WrapperInterface):
    """
    Wrapper for invariant components that evaluate conditions that must hold within a state.
    """
    _component_class: Type[InvariantInterface]

    def _evaluate(self, context: EvaluationContext) -> InvariantEvaluationMSG:
        if self._component_instance is None:
            raise RuntimeError("Component instance is None. Call activate() first.")
        
        # Delegate to the actual component instance
        result = self._component_instance(context)
        
        # Ensure we return the correct message type
        if isinstance(result, InvariantEvaluationMSG):
            return result
        else:
            # Convert or wrap the result if needed
            status = InvariantEvaluationMSG()
            # Set appropriate 

    @classmethod
    def load_invariant(cls, invariants_dict: Dict[str, Any]):
        pass
    
    @classmethod
    def load_invariant_wrapper_from_famd(cls, invariant_name: str, invariants_dict: Dict[str, Any]) -> 'InvariantWrapper':
        pass

@dataclass 
class InvariantRegistry():
    _invariants: Dict[str, InvariantWrapper]

    
    @classmethod 
    def load_invariants_from_famd(cls, invariants_dict: dict) -> 'InvariantRegistry':
        pass