# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the ModeFactory class for creating and managing modes in a robotic automaton system.
It includes functionality for loading modes from a configuration dictionary and creating Mode instances.
"""

from typing import Dict, Any

from hybraut_model.modes import Mode, ModeRegistry


class ModeFactory:

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

        return Mode(
            _id=id,
            _name=name,
            _description=description,
            _dynamics_ref=dynamics,
            _invariant_refs=invariants,
            _transition_refs=transitions,
            _entry_actions=entry_actions,
            _exit_actions=exit_actions,
            _is_goal_mode=is_goal_mode,
        )

    @classmethod
    def load_modes_registry_from_amdl(cls, mode_dict: dict):
        modes: Dict[int, Mode] = {}
        for mode_idx, mode_conf in mode_dict.items():
            modes[mode_idx] = cls.load_mode_from_amdl(
                mode_idx=mode_idx, mode_dict=mode_conf
            )

        return ModeRegistry(_modes=modes)
