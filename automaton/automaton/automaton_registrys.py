from typing import Dict, List
from .automaton_wrappers import (
    InvariantWrapper, 
    ResetWrapper,
    GuardWrapper,
)

class InvariantRegistry:
    _invariants: Dict[str, InvariantWrapper]
    
    def register_invariant(name: str, invariant: InvariantWrapper):
        pass

    def get_invariant(name: str) -> InvariantWrapper:
        pass

    def check_invariant(name: str, context: EvaluationContext) -> bool:
        pass

class ResetsRegistry: 
    _resets: Dict[str, ResetWrapper]

    def register_reset(name: str, reset: ResetWrapper):
        pass

    def get_reset(name: str) -> ResetWrapper:
        pass

    def apply_reset(name: str, context: EvaluationContext) -> ResetResult:
        pass

class GuardsRegistry:
    _guards: Dict[str, GuardWrapper]
    
    def register_guard(name: str, guard: GuardWrapper):
        pass
 
    def get_guard(name: str) -> GuardWrapper:
        pass

    def evaluate_guard(name: str, context: EvaluationContext) -> GuardEvaluation:
        pass

class StateRegistry:
    _states: Dict[str, State]
    _state_dependencies: Dict[str, List[str]]

    def register_state(state: State):
        pass

    def get_state(name: str) -> State:
        pass

    def get_active_states() -> List[State]:
        pass

    def validate_state_consistency() -> bool:
        bool

class ModeRegistry:
    modes: Dict[int, Mode]
    mode_graph: Dict[int, List[int]]

    def register_mode(mode: Mode):
        pass

    def get_mode(mode_id: int) -> Mode:
        pass

    def get_reachable_modes(from_mode: int) -> List[int]:
        pass

    def validate_mode_connectivity() -> bool: 
        pass