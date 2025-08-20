# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the Mode and ModeRegistry classes for managing modes in a robotic automaton system.
It includes functionality for defining modes, their transitions, and invariants, as well as methods for
entering and exiting modes, and retrieving enabled transitions.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from hybraut_model._evaluation_context import EvaluationContext
from hybraut_model._transitions import Transition


@dataclass
class Mode:
    """
    Represents a mode in the automaton, which can have transitions, invariants, and actions.
    Each mode can be entered or exited, and it can define which transitions are enabled.
    """

    _id: int = field(init=True)
    _name: str = field(init=True)
    _dynamics_ref: str = field(init=True)
    _invariants_refs: List[str] = field(init=True)

    _description: str = field(init=True, default="no description")
    _transitions_ref: Dict[int, Transition] = field(init=True, default=None)
    _entry_actions: List[str] = field(init=True, default=None)
    _exit_actions: List[str] = field(init=True, default=None)
    _is_goal_mode: bool = field(init=True, default=False)

    def on_enter(self, context: EvaluationContext): ...

    def on_exit(self, context: EvaluationContext): ...

    def get_enabled_transition_refs(self) -> List[str]: ...

    def get_dynamics_ref(self) -> str:
        return self._dynamics_ref

    def get_transition_refs(self) -> List[str]:
        return self._transitions_ref

    def get_invariant_refs(self) -> List[str]:
        return self._invariants_refs

    @classmethod
    def load_mode_from_amdl(cls, mode_idx, mode_dict):
        id = mode_idx
        name = mode_dict["name"]
        description = mode_dict.get("description")
        dynamics = mode_dict.get("dynamics")
        invariants = mode_dict.get("invariants")
        transitions = mode_dict.get("transitions")
        entry_actions = None
        exit_actions = None
        is_goal_mode = False

        return cls(
            _id=id,
            _name=name,
            _description=description,
            _dynamics_ref=dynamics,
            _invariants_refs=invariants,
            _transitions_ref=transitions,
            _entry_actions=entry_actions,
            _exit_actions=exit_actions,
            _is_goal_mode=is_goal_mode,
        )


@dataclass
class ModeRegistry:
    _modes: Dict[int, Mode] = field(init=True)
    _mode_graph: Dict[int, List[int]] = field(init=False, default_factory=dict)

    @classmethod
    def register_mode(cls, mode: Mode):
        pass

    def get_mode(self, mode_id: int):
        return self._modes.get(mode_id)
    
    def is_mode(self, mode_id: int):
        if mode_id in self._modes.keys():
            return True
        
        return False

    def get_reachable_modes(self, from_mode: int) -> Mode: ...

    def get_reachable_modes(self, from_mode: int) -> List[Mode]: ...

    def validate_mode_connectivity(self) -> bool: ...

    @classmethod
    def load_modes_registry_from_amdl(cls, mode_dict: dict):
        modes: Dict[int, Mode] = {}
        for mode_idx, mode_conf in mode_dict.items():
            modes[mode_idx] = Mode.load_mode_from_amdl(
                mode_idx=mode_idx, mode_dict=mode_conf
            )

        return cls(_modes=modes)


"""main function for testing purposes, not for production use"""


def main():
    pass


if __name__ == "__main__":
    main()
