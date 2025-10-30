# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the Mode and ModeRegistry classes for managing modes in a robotic automaton system.
It includes functionality for defining modes, their transitions, and invariants, as well as methods for
entering and exiting modes, and retrieving enabled transitions.
"""

from dataclasses import dataclass, field
from typing import Dict, List

from hybraut_nav_tactical.tactical_models.ctx.evaluation_context import EvaluationContext
from hybraut_nav_tactical.tactical_models.core.transitions import Transition

from typing import Optional, Callable


class Mode:
    """
    Represents a mode in the automaton, which can have transitions, invariants, and actions.
    Each mode can be entered or exited, and it can define which transitions are enabled.
    """

    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        dynamics_ref: str,
        invariant_refs: List[str],
        transition_refs: Dict[int, str],
        is_goal_mode: Optional[bool] = False,
        entry_actions: Optional[List[Callable[["Mode", EvaluationContext], None]]] = [],
        exit_actions: Optional[List[Callable[["Mode", EvaluationContext], None]]] = [],
    ):
        self._id = id
        self._name = name
        self._description = description
        self._dynamics_ref = dynamics_ref
        self._invariant_refs = invariant_refs
        self._transition_refs = transition_refs
        self._is_goal_mode = is_goal_mode
        self._entry_actions = entry_actions
        self._exit_actions = exit_actions

    """ === access modifiers === """

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_entry_actions(self):
        return self._entry_actions

    def get_exit_actions(self):
        return self._exit_actions

    def get_is_goal_mode(self):
        return self._is_goal_mode

    def get_dynamics_ref(self) -> str:
        return self._dynamics_ref

    def get_transition_refs(self) -> List[str]:
        if not self._transition_refs:
            return []
        return list(self._transition_refs.values())

    def get_transition_refs_and_priorities(self) -> Dict[str, Transition]:
        return self._transition_refs

    def get_invariant_refs(self) -> List[str]:
        return self._invariant_refs

    def get_entry_actions(self) -> List[Callable[["Mode", EvaluationContext], None]]:
        """Return a copy of the entry actions to prevent external mutation."""
        return list(self._entry_actions)

    def get_exit_actions(self) -> List[Callable[["Mode", EvaluationContext], None]]:
        """Return a copy of the exit actions to prevent external mutation."""
        return list(self._exit_actions)

    """ === mode logic ==="""

    def on_enter(self, ctx: EvaluationContext):
        for fn in self._entry_actions:
            fn(self, ctx)

    def on_exit(self, ctx: EvaluationContext):
        for fn in self._exit_actions:
            fn(self, ctx)

    """string representation functions"""

    def __repr__(self) -> str:
        return (
            f"Mode(id={self._id!r}, name={self._name!r}, dynamics_ref={self._dynamics_ref!r}, "
            f"invariant_refs={self._invariant_refs!r}, description={self._description!r}, "
            f"transition_refs={list(self._transition_refs.keys()) if self._transition_refs else []}, "
            f"entry_actions={self._entry_actions!r}, exit_actions={self._exit_actions!r}, "
            f"is_goal_mode={self._is_goal_mode!r})"
        )

    def __str__(self) -> str:
        return (
            f"Mode '{self._name}' (ID: {self._id})\n"
            f"  Dynamics: {self._dynamics_ref}\n"
            f"  Invariants: {', '.join(self._invariant_refs) if self._invariant_refs else 'None'}\n"
            f"  Description: {self._description}\n"
            f"  Entry actions: {', '.join(self._entry_actions) if self._entry_actions else 'None'}\n"
            f"  Exit actions: {', '.join(self._exit_actions) if self._exit_actions else 'None'}\n"
            f"  Goal mode: {self._is_goal_mode}\n"
            f"  Transitions: {list(self._transition_refs.keys()) if self._transition_refs else 'None'}"
        )


class ModeRegistry:
    """
    a registry for modes, provides utility functions
    for access visualization of modes within the automaton
    """

    def __init__(self, modes: Dict[int, Mode]):
        """"""
        self._modes: Dict[int, Mode] = modes
        self._mode_graph: Dict[int, List[int]] = self._build_graph()

    """ === mode graph generation function === """

    def _build_graph(self) -> Dict[int, List[int]]:
        """Construct the mode transition graph."""
        graph = {}
        for mode_id, mode in self._modes.items():
            # mode.get_transition_refs() returns the transition targets
            if isinstance(mode.get_transition_refs_and_priorities(), dict):
                targets = list(mode.get_transition_refs_and_priorities().keys())
            else:
                targets = []
            graph[mode_id] = targets
        return graph

    def get_reachable_modes(self, from_mode: int) -> List[Mode]:
        """Return all modes reachable from `from_mode` (DFS/BFS)."""
        visited = set()
        stack = [from_mode]
        reachable = []

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                if current != from_mode:
                    reachable.append(self._modes[current])
                stack.extend(self._mode_graph.get(current, []))

        return reachable

    def validate_mode_connectivity(self) -> bool:
        """Check if all modes are in one weakly connected component."""
        if not self._modes:
            return True

        # Build undirected adjacency
        undirected = {mid: set() for mid in self._modes}
        for src, targets in self._mode_graph.items():
            for t in targets:
                undirected[src].add(t)
                undirected[t].add(src)

        # DFS/BFS from first node
        start = next(iter(self._modes))
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                stack.extend(undirected[node] - visited)

        return len(visited) == len(self._modes)

    def register_mode(cls, mode: Mode):
        pass

    """ === access modifiers === """

    def get_mode(self, mode_id: int):
        return self._modes.get(mode_id)

    def is_mode(self, mode_id: int):
        if mode_id in self._modes.keys():
            return True

        return False

    def get_mode_ids(self) -> List[int]:
        return list(self._modes.keys())

    def get_num_modes(self) -> int:
        return len(self._modes)

    """ === utility functions === """

    def get_reachable_mode_ids(self, from_mode: int) -> List[int]:
        return self._mode_graph.get(from_mode, [])

    def is_to_mode_reachable_from(self, from_mode: int, to_mode: int) -> bool:
        """validates if to_mode is reachable from_mode"""
        to_modes: List[int] = self._mode_graph.get(from_mode)
        return to_mode in to_modes

    """ === string representation === """

    def __str__(self) -> str:
        mode_lines = []
        for mode_id, mode in self._modes.items():
            transitions = self._mode_graph.get(mode_id, [])
            transitions_str = (
                ", ".join(map(str, transitions)) if transitions else "None"
            )
            mode_lines.append(
                f"Mode {mode_id}: {mode.get_name()} -> [{transitions_str}]"
            )
        return f"ModeRegistry with {len(self._modes)} modes\n" + "\n".join(mode_lines)

    def __repr__(self) -> str:
        return (
            f"ModeRegistry(modes={list(self._modes.keys())!r}, "
            f"graph={self._mode_graph!r})"
        )


"""main function for testing purposes, not for production use"""


def main():
    # Mode 0: Idle
    idle_mode = Mode(
        id=0,
        name="Idle",
        description="Waiting for mission start",
        dynamics_ref="dyn_idle",
        invariant_refs=["battery_ok"],
        transition_refs={1: "to_navigation"},  # Transition to mode 1
    )

    # Mode 1: Navigate
    navigate_mode = Mode(
        id=1,
        name="Navigate",
        description="Following waypoints to goal",
        dynamics_ref="dyn_navigation",
        invariant_refs=["gps_ok", "collision_free"],
        transition_refs={},  # No outgoing transitions
        is_goal_mode=True,  # This is the goal mode
    )
    # Put them in a registry for easy access
    modes = {0: idle_mode, 1: navigate_mode}

    registry = ModeRegistry(modes)

    print(registry)


if __name__ == "__main__":
    main()
