from hybraut_model.states import State, StateRegistry
from typing import Dict, Any, List
import logging
from hybraut_model.automaton_types import MsgType


logger = logging.getLogger(__name__)

from hybraut_model.dynamics import DynamicsWrapper, DynamicsRegistry
from hybraut_model.automaton_types import ComponentPath
from hybraut_model.constants.urgency import UrgencyEnums
from hybraut_model.transitions import Transition, TransitionRegistry


class _InvariantFactory: ...


class _GuardFactory: ...


class _ResetFactory: ...


class _TransitionFactory:
    component_cls = Transition


class _ModeFactory:
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
            _transition_refs=transitions,
            _entry_actions=entry_actions,
            _exit_actions=exit_actions,
            _is_goal_mode=is_goal_mode,
        )


class HybridAutomatonFactory: ...
