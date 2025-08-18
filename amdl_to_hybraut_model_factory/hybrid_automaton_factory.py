from hybraut_model import HybridAutomaton
from hybraut_model.


@classmethod
def register_automaton(cls, amdl_dict: dict) -> HybridAutomaton:
    name = amdl_dict["automaton_name"]
    description = amdl_dict["automaton_description"]
    version = amdl_dict["version"]

    initial_mode = amdl_dict["initial_mode"]
    goal_modes = amdl_dict["goal_modes"]

    states = StateRegistry.load_state_registry_from_amdl(
        node=node, states_dict=amdl_dict["states"]
    )
    guards = GuardRegistry.load_guard_registry_from_amdl(amdl_dict["guards"])
    resets = ResetRegistry.load_reset_registry_from_amdl(amdl_dict.get("resets"))
    dynamics = DynamicsRegistry.load_dynamics_registry_from_amdl(amdl_dict["dynamics"])
    invariants = InvariantRegistry.load_invariant_registry_from_amdl(
        amdl_dict["invariants"]
    )
    transitions = TransitionRegistry.load_transition_registry_from_amdl(
        amdl_dict["transitions"]
    )
    modes = ModeRegistry.load_modes_registry_from_amdl(amdl_dict["modes"])

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
