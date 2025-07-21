
from dataclasses import dataclass
from ..automaton_registrys import StateRegistry
from builtin_interfaces.msg import Time, Duration
from typing import Dict, Any

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