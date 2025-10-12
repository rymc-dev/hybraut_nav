# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluation context for the Hybraut framework.
"""

from dataclasses import dataclass
from typing import Any, Dict, List
from builtin_interfaces.msg import Time, Duration


@dataclass
class EvaluationContext:
    """
    Context class that holds evaluation state and parameters.
    Initialized on automaton evaluation time, and passed to evaluation
    functions.
    """

    current_mode: int
    stamp: float
    metadata: Dict[str, Any]

    mode_registry: (
        Any  # Any is a placeholder for registry due to circular import violations.
    )
    transition_registry: Any
    states_registry: Any
    guard_registry: Any
    reset_registry: Any
    invariant_registry: Any

    def get_state_values(self, state_names: List[str]) -> Dict[str, Any]:
        return self.states_registry.get_current_states_by_state_names(state_names)

    def get_states(self, state_names: List[str]) -> Dict[str, Any]:
        return self.states_registry.get_states_by_name(state_names)

    def get_state_age(self, state_name: str) -> float:
        """Returns the duration since the state was last entered."""
        return self.states_registry.get_state_age_by_state_name(state_name)

    def get_event_history(self) -> List[Any]:
        """Returns the history of events observed (stub for now)."""
        return self.metadata.get("event_history", [])
