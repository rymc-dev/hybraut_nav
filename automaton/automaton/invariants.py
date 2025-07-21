
# from typing import Type, Dict, Optional
# from dataclasses import dataclass, field
# from automaton.interfaces import WrapperInterface
# from automaton.core_interfaces import InvariantInterface
# from automaton.context import EvaluationContext
# from automaton_interfaces.msg import InvariantEvaluationMSG
# import logging



# @dataclass
# class InvariantWrapper(WrapperInterface):
#     """
#     Wrapper for invariant components that evaluate conditions that must hold within a state.
#     """
#     _component_class: Type[InvariantInterface]

#     def _evaluate(self, context: EvaluationContext) -> InvariantEvaluationMSG:
#         if self._component_instance is None:
#             raise RuntimeError("Component instance is None. Call activate() first.")
        
#         # Delegate to the actual component instance
#         result = self._component_instance(context)
        
#         # Ensure we return the correct message type
#         if isinstance(result, InvariantEvaluationMSG):
#             return result
#         else:
#             # Convert or wrap the result if needed
#             status = InvariantEvaluationMSG()
#             # Set appropriate 

#     @classmethod
#     def load_invariant(cls, invariants_dict: Dict[str, Any]):
#         pass
    
#     @classmethod
#     def load_invariant_wrapper_from_famd(cls, invariant_name: str, invariants_dict: Dict[str, Any]) -> 'InvariantWrapper':
#         pass

# if __name__ == '__main__':
#     invariant_name = 'goal_reached_guard'
#     invariant_dict = {
#         'module': 'automaton.common_behaviours.guards.',
#         'class_name': 'goal_reached_guard',
#         'configuration': {
#             'tolerance': 0.2
#         }
#     }
#     InvariantWrapper.load_invariant_wrapper_from_famd(
#         invariant_name=invariant_name,
#         invariants_dict=invariant_dict
#     )


# from automaton_interfaces.msg import InvariantEvaluationsMSG
# from typing import List, Any

# @dataclass
# class InvariantRegistry():
#     _invariants: Dict[str, InvariantWrapper] = field(default_factory=dict)
#     _are_invariants_initialized = False
#     _logger: Optional[logging.Logger]


#     def __post_init__(self):
#         """Initialize the logger after dataclass creation."""
#         self._logger = logging.getLogger(f"{__name__}.InvariantRegistry")

#     def _evaluate_invariants_by_name(self, invariant_names: List[str], evaluation_context: EvaluationContext) -> InvariantEvaluationsMSG:
#         pass

#     def activate_invariants(self):
#         """ 
#         initialize the invariants with their configurations by calling the activate function for each of them
#         """
#         pass

#     def deactivate_invariants(self):
#         """ 
#         uninitialize the invariants
#         """
#         pass

#     def get_registry_status(self) -> Dict[str, any]:
#         pass

#     @classmethod
#     def register_invariant(self, invariant_name: str, invariant_dict: Dict[str, Any]) -> InvariantWrapper:
#         pass

#     @classmethod
#     def register_invariants(self, invariant_dict: Dict[str, Any]) -> Dict[str, InvariantWrapper]:
#         pass

#     @classmethod
#     def load_invariant_registry_from_famd(cls, invariants_dict: Dict[str, Any]) -> 'InvariantRegistry':
#         pass



