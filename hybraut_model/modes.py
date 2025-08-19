# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the Mode and ModeRegistry classes for managing modes in a robotic automaton system.
It includes functionality for defining modes, their transitions, and invariants, as well as methods for
entering and exiting modes, and retrieving enabled transitions.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from hybraut_model.evaluation_context import EvaluationContext
from hybraut_model.transitions import Transition


@dataclass
class Mode:
    """
    Represents a mode in the automaton, which can have transitions, invariants, and actions.
    Each mode can be entered or exited, and it can define which transitions are enabled.
    """

    _id: int = field(init=True)
    _name: str = field(init=True)
    _dynamics_ref: str = field(init=True)
    _invariant_refs: List[str] = field(init=True)

    _description: str = field(init=True, default="no description")
    _transition_refs: Dict[int, Transition] = field(init=True, default=None)
    _entry_actions: List[str] = field(init=True, default=None)
    _exit_actions: List[str] = field(init=True, default=None)
    _is_goal_mode: bool = field(init=True, default=False)

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_dynamics_ref(self):
        return self._dynamics_ref

    def get_invariant_refs(self):
        return self._invariant_refs

    def get_transition_refs(self):
        return self._transition_refs

    def get_entry_actions(self):
        return self._entry_actions

    def get_exit_actions(self):
        return self._exit_actions

    def get_is_goal_mode(self):
        return self._is_goal_mode

    def on_enter(self, ctx: EvaluationContext): ...

    def on_exit(self, ctx: EvaluationContext): ...

    def get_dynamics_ref(self) -> str:
        return self._dynamics_ref

    def get_transition_refs_and_priorities(self) -> Dict[int, str]:
        return self._transition_refs

    def get_invariant_refs(self) -> List[str]:
        return self._invariant_refs


@dataclass
class ModeRegistry:
    _modes: Dict[int, Mode] = field(init=True)
    _mode_graph: Dict[int, List[int]] = field(init=False)

    def get_mode_ids(self):
        return list(self._modes.keys())

    def get_mode_names(self):
        return [mode.get_name() for mode in self._modes.values()]

    def get_num_nodes(self):
        return len(self._modes)

    @classmethod
    def register_mode(cls, mode: Mode):
        pass

    def get_mode(self, mode_id: int) -> Mode:
        return self._modes.get(mode_id)

    def is_mode(self, mode_id: int) -> bool:
        if mode_id in self._modes.keys():
            return True

        return False

    def get_reachable_modes(self, from_mode: int) -> List[Mode]:
        """
        returns a list of modes that are reachable from_mode id
        """
        ...

    def validate_from_to_mode(self, from_mode: int, to_mode: int) -> bool:
        """validates if a transition from from_mode to to_mode is valid based on the mode graph"""
        ...

    def validate_mode_connectivity(self) -> bool:
        """
        Validates the connectivity of modes in the registry.
        """
        ...


"""main function for testing purposes, not for production use"""


def main():
    mode_dict = {
        0: {
            "name": "Idle",
            "description": "The robot is idle.",
            "dynamics": "idle_dynamics",
            "invariants": ["idle_invariant"],
            "transitions": {1: "start_transition", 2: "stop_transition"},
        },
        1: {
            "name": "Active",
            "description": "The robot is active.",
            "dynamics": "active_dynamics",
            "invariants": ["active_invariant"],
            "transitions": {0: "stop_transition", 2: "pause_transition"},
        },
    }

    mode_registry = ModeRegistry.load_modes_registry_from_amdl(mode_dict)


if __name__ == "__main__":
    main()
