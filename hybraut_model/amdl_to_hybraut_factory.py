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

    @classmethod
    def load_transition_from_amdl(
        cls, transition_name: str, transition_value: Dict[str, Any]
    ) -> Transition:
        """
        Load a transition from a configuration dictionary.
        """
        name = transition_name
        target_mode = transition_value["target_mode"]
        guard_ref = transition_value["guard"]
        reset_ref = transition_value.get("reset")
        urgency = UrgencyEnums(transition_value.get("urgency", 1))

        return cls(
            _name=name,
            _target_mode=target_mode,
            _guard_refs=guard_ref,
            _reset_refs=reset_ref,
            _urgency=urgency,
        )

    @classmethod
    def register(cls, config_dict: Dict[str, Any]) -> Dict[str, Transition]:
        components = {}

        for name, conf in config_dict.items():
            try:
                component = cls.component_cls.load_transition_from_amdl(
                    transition_name=name, transition_value=conf
                )
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to load component '{name}': {e}"
                )
                raise
        return components

    @classmethod
    def load_transition_registry_from_amdl(
        cls, transition_dict: dict
    ) -> TransitionRegistry:
        logging.info("Loading TransitionRegistry")
        transitions = cls.register(transition_dict)
        registry = cls(_components=transitions)
        logger.info(f"Created TransitionRegistry with {len(transitions)} transitions")

        return registry


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
