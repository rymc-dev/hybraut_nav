from dataclasses import dataclass, field
from typing import Dict, List

from context.evaluation_context import EvaluationContext
from transitions import Transition


@dataclass
class Mode:
    _id: int = field(init=True)
    _name: str = field(init=True)
    _dynamics_ref: str = field(init=True)
    _invariants_ref: List[str] = field(init=True)

    _description: str = field(init=True, default="no description")
    _transitions_ref: Dict[int, Transition] = field(init=True, default=None)
    _entry_actions: List[str] = field(init=True, default=None)
    _exit_actions: List[str] = field(init=True, default=None)
    _is_goal_mode: bool = field(init=True, default=False)

    def on_enter(self, context: EvaluationContext):
        ...

    def on_exit(self, context: EvaluationContext):
        ...
    
    def get_enabled_transition_refs(self) -> List[str]:
        ...

    @classmethod
    def load_mode_from_amdl(cls, mode_idx, mode_dict):
        id = mode_idx
        name = mode_dict['name']
        description = mode_dict.get('description')
        dynamics = mode_dict.get('dynamics')
        invariants = mode_dict.get('invariants')
        transitions = mode_dict.get('transitions')
        entry_actions = None
        exit_actions = None
        is_goal_mode = False

        return cls(
            _id=id,
            _name=name,
            _description=description,
            _dynamics_ref=dynamics,
            _invariants_ref=invariants,
            _transitions_ref=transitions,
            _entry_actions=entry_actions,
            _exit_actions=exit_actions,
            _is_goal_mode=is_goal_mode
        )
    

@dataclass
class ModeRegistry():
    _modes: Dict[int, Mode] = field(init=True)
    _mode_graph: Dict[int, List[int]] = field(init=False)

    @classmethod
    def register_mode(cls, mode: Mode):
        pass

    def get_mode(self):
        ...

    def get_reachable_modes(self, from_mode: int) -> Mode:
        ...

    def get_reachable_modes(self, from_mode: int) -> List[Mode]:
        ...
    
    def validate_mode_connectivity(self) -> bool:
        ...

    @classmethod
    def load_modes_registry_from_amdl(cls, mode_dict: dict):
        modes: Dict[int, Mode] = {}
        for mode_idx, mode_conf in mode_dict.items():
            modes[mode_idx] = Mode.load_mode_from_amdl(
                mode_idx=mode_idx,
                mode_dict=mode_conf
            )

        return cls(
            _modes=modes
        )