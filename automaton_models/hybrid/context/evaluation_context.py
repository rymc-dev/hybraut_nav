
from dataclasses import dataclass
# from states import StateRegistry
from typing import Any
from builtin_interfaces.msg import Time, Duration
from typing import Dict, Any, List
# from guards import GuardRegistry
# from resets import ResetRegistry
# from invariants import InvariantRegistry

@dataclass
class EvaluationContext:
    """
    Context class that holds evaluation state and parameters.
    initialized on automaton evaluation time, and passed to evaluation
    functions.
    """
    states: Any
    current_mode: int
    stamp: Time
    metadata: Dict[str, Any]
    # guard_registry: GuardRegistry
    # reset_registry: ResetRegistry
    # invariant_registry: InvariantRegistry

    def get_state_values(self, state_names: List[str]) -> Dict[str, Any]:
        return self.states.get_current_states(state_names)

    def get_states(self, state_names: List[str]) -> Dict[str, Any]:
        return self.states.get_components_by_names(state_names)

    def get_state_age(self, state_name) -> Duration:
        pass

    def get_event_history() -> None:
        """not sure how to implement this yet."""
        pass