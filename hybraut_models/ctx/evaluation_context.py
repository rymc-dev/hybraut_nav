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
    states: Any
    current_mode: int
    stamp: Time
    metadata: Dict[str, Any]
    guard_registry: Any
    reset_registry: Any
    invariant_registry: Any

    def get_state_values(self, state_names: List[str]) -> Dict[str, Any]:
        return self.states.get_current_states(state_names)

    def get_states(self, state_names: List[str]) -> Dict[str, Any]:
        return self.states.get_components_by_names(state_names)

    def get_state_age(self, state_name: str) -> Duration:
        """Returns the duration since the state was last entered."""
        state_time: Time = self.states.get_state_time(state_name)
        duration = Duration()
        duration.sec = self.stamp.sec - state_time.sec
        duration.nanosec = self.stamp.nanosec - state_time.nanosec
        # Normalize negative nanoseconds
        if duration.nanosec < 0:
            duration.sec -= 1
            duration.nanosec += 1_000_000_000
        return duration

    def get_event_history(self) -> List[Any]:
        """Returns the history of events observed (stub for now)."""
        return self.metadata.get("event_history", [])
