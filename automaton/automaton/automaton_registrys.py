from typing import Dict, List
from .automaton_wrappers import (
    InvariantWrapper, 
    ResetWrapper,
    GuardWrapper,
)
from abc import ABC, abstractmethod
from typing import Dict, List, Set
from rclpy.node import Node
from .automaton_components import State
# class ComponentRegistryInterface(ABC):
#     _component_registry: Dict[]

from rclpy.qos import QoSProfile
from rclpy.callback_groups import CallbackGroup
from typing import Optional, Type

class StateRegistry:
    _states: Set[State]
    _are_state_active: bool = False


    def validate_state_dependencies(self, state_names: List[str], state_types: List[Type]) -> None:
        """components can utilize this function to """

    def get_state_names(self) -> List[str]:
        """returns a list of state names in a life from the set"""
        states_names = []
        for state in self._states:
            states_names.append(state._name)

    def get_state_msg_types(self) -> List[Type]:
        """returns a list of state types in a list from the set"""
        state_types = []
        for state in self._states:
            state_types.append(state._msg_type)

    def activate_states(self, node: Node, qos: Optional[QoSProfile], cb_group: Optional[CallbackGroup]) -> None:
        """activate states, this is for whhen hybrid automaton model moves to activate state"""
        if not self._are_state_active:
            raise RuntimeError('attempted to activate states but they are already active')
        
        for state in self._states:
            state.activate_state(node, qos, cb_group)
        
    def deactivate_states(self, node:Node, qos: Optional[QoSProfile] = None, cb_group: Optional[CallbackGroup] = None) -> None:
        """deactivate the states, this is for when hybrid automaton model moves to inactive state"""
        if self._are_state_active:
            raise RuntimeError('attemped to deactivate states but they are already active.')
        
        for state in self._states:
            state.deactivate_state(node)
    
    @classmethod
    def register_state(cls, state_name: str, state_dict) -> State:
        return State.load_state_from_famd(state_name, state_dict)

    @classmethod
    def register_states(cls, state_dict: dict) -> Set[State]:
        state_set = set()
        if state_dict is not None:
            for state_name, state_value in state_dict.items():
                set.add(cls.register_state)

        return state_set

    def load_state_registry_from_famd(cls, states_dict: dict) -> 'StateRegistry':
        return StateRegistry(
            _states=cls.register_states(states_dict)
        )


# class InvariantRegistry:
#     _invariants: Dict[str, InvariantWrapper]
    
#     def register_invariant(name: str, invariant: InvariantWrapper):
#         pass

#     def get_invariant(name: str) -> InvariantWrapper:
#         pass

#     def check_invariant(name: str, context: EvaluationContext) -> bool:
#         pass

# class ResetsRegistry: 
#     _resets: Dict[str, ResetWrapper]

#     def register_reset(name: str, reset: ResetWrapper):
#         pass

#     def get_reset(name: str) -> ResetWrapper:
#         pass

#     def apply_reset(name: str, context: EvaluationContext) -> ResetResult:
#         pass

# class GuardsRegistry:
#     _guards: Dict[str, GuardWrapper]
    
#     def register_guard(name: str, guard: GuardWrapper):
#         pass
 
#     def get_guard(name: str) -> GuardWrapper:
#         pass

#     def evaluate_guard(name: str, context: EvaluationContext) -> GuardEvaluation:
#         pass

# class StateRegistry:
#     _states: Dict[str, State]
#     _state_dependencies: Dict[str, List[str]]

#     def register_state(state: State):
#         pass

#     def get_state(name: str) -> State:
#         pass

#     def get_active_states() -> List[State]:
#         pass

#     def validate_state_consistency() -> bool:
#         bool

# class ModeRegistry:
#     modes: Dict[int, Mode]
#     mode_graph: Dict[int, List[int]]

#     def register_mode(mode: Mode):
#         pass

#     def get_mode(mode_id: int) -> Mode:
#         pass

#     def get_reachable_modes(from_mode: int) -> List[int]:
#         pass

#     def validate_mode_connectivity() -> bool: 
#         pass