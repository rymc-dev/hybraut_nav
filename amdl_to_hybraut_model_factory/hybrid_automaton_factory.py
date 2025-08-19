# !/usr/bin/python3
"""
factory class for generating a hybrid automaton model fomr
an AMDL file.
"""

from hybraut_models import HybridAutomaton

from amdl_to_hybraut_model_factory.state_factory import StateFactory
from amdl_to_hybraut_model_factory.guard_factory import GuardFactory
from amdl_to_hybraut_model_factory.reset_factory import ResetFactory
from amdl_to_hybraut_model_factory.dynamics_factory import DynamicsFactory
from amdl_to_hybraut_model_factory.invariant_factory import InvariantFactory
from amdl_to_hybraut_model_factory.transition_factory import TransitionFactory
from amdl_to_hybraut_model_factory.mode_factory import ModeFactory


class HybridAutomatonFactory:
    """
    factory class for generating a hybrid automaton model from
    an AMDL file
    """

    @classmethod
    def register_automaton(cls, amdl_dict: dict) -> HybridAutomaton:
        name = amdl_dict["automaton_name"]
        description = amdl_dict["automaton_description"]
        version = amdl_dict["version"]

        initial_mode = amdl_dict["initial_mode"]
        goal_modes = amdl_dict["goal_modes"]

        states = StateFactory.load_state_registry_from_amdl(amdl_dict.get("states"))
        guards = GuardFactory.load_guards_registry_from_amdl(amdl_dict.get("guards"))
        resets = ResetFactory.load_reset_registry_from_amdl(amdl_dict.get("resets"))
        dynamics = DynamicsFactory.load_dynamics_registry_from_amdl(
            amdl_dict.get("dynamics")
        )
        invariants = InvariantFactory.load_invariant_registry_from_amdl(
            amdl_dict.get("invariants")
        )
        transitions = TransitionFactory.load_transition_registry_from_amdl(
            amdl_dict.get("transitions")
        )
        modes = ModeFactory.load_modes_registry_from_amdl(amdl_dict.get("modes"))

        return cls(
            _name=name,
            _description=description,
            _version=version,
            _initial_mode=initial_mode,
            _goal_modes=goal_modes,
            _states=states,
            _guards=guards,
            _modes=modes,
            _resets=resets,
            _dynamics=dynamics,
            _invariants=invariants,
            _transitions=transitions,
        )
