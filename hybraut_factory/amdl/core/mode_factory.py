# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the ModeFactory class for creating and managing modes in a robotic automaton system.
It includes functionality for loading modes from a configuration dictionary and creating Mode instances.
"""

from typing import Dict, Any

from hybraut_models.core.modes import Mode, ModeRegistry


class ModeFactory:

    @classmethod
    def load_mode_from_amdl(cls, mode_idx, mode_dict):
        id = mode_idx
        name = mode_dict["name"]
        description = mode_dict.get("description")
        dynamics = mode_dict.get("dynamics")
        invariants = mode_dict.get("invariants")
        transitions = mode_dict.get("transitions")
        entry_actions = []
        exit_actions = []
        # not sure yet how I should load entry and exit actions, by default for not will keep them as empty lists
        is_goal_mode = False

        return Mode(
            id=id,
            name=name,
            description=description,
            dynamics_ref=dynamics,
            invariant_refs=invariants,
            transition_refs=transitions,
            entry_actions=entry_actions,
            exit_actions=exit_actions,
            is_goal_mode=is_goal_mode,
        )

    @classmethod
    def load_modes_registry_from_amdl(cls, mode_dict: dict):
        modes: Dict[int, Mode] = {}
        for mode_idx, mode_conf in mode_dict.items():
            modes[mode_idx] = cls.load_mode_from_amdl(
                mode_idx=mode_idx, mode_dict=mode_conf
            )

        return ModeRegistry(modes=modes)
