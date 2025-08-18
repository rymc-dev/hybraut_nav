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
    def load_modes_registry_from_amdl(cls, mode_dict: dict):
        modes: Dict[int, Mode] = {}
        for mode_idx, mode_conf in mode_dict.items():
            modes[mode_idx] = Mode.load_mode_from_amdl(
                mode_idx=mode_idx, mode_dict=mode_conf
            )

        return cls(_modes=modes)
