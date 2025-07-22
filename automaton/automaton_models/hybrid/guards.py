from .component_interfaces import WrapperInterface
from .context import EvaluationContext
from  .aci_interfaces import GuardInterface
from automaton_interfaces.msg import GuardEvaluationMSG 
from dataclasses import dataclass
from typing import Type, Dict, Any

@dataclass
class GuardWrapper(WrapperInterface):
    """
    Wrapper for guard components that evaluate transition conditions.
    """
    _component_class: Type[GuardInterface]

    def _evaluate(self, context: EvaluationContext) -> GuardEvaluationMSG:
        if self._component_instance is None:
            raise RuntimeError("Component instance is None. Call activate() first.")
        
        # Delegate to the actual component instance
        result = self._component_instance(context)
        
        # Ensure we return the correct message type
        if isinstance(result, GuardEvaluationMSG):
            return result
        else:
            # Convert or wrap the result if needed
            evaluation = GuardEvaluationMSG()
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
