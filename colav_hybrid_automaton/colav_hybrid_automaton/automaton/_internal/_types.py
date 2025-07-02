from dataclasses import dataclass
from colav_hybrid_automaton.automaton.guards.guard import Guard as GuardABC
from typing import Any, List
from colav_hybrid_automaton.automaton.resets.reset import Reset as ResetABC
from typing import TypedDict

# We utilize data classes to define the hybrid automaton in the automaton lifecycle to simplify the storage
# instead of always using dicts defined on the fly.

@dataclass
class State: 
    name: str
    state: Any

@dataclass
class Guard: 
    name: str
    instance: GuardABC
    state_inputs: List[State] 

@dataclass
class Reset:
    name: str   
    instance: ResetABC
    state_inputs: List[State]
    reset_targets: List[State]

@dataclass
class Transition:
    name: str
    guard: Guard
    reset: Reset

@dataclass
class Transitions: 
    transitions: List[Transition]

@dataclass
class Mode:
    idx: int
    name: str
    description: str

@dataclass
class HybridAutomaton:
    name: str
    description: str
    transition_evaluation_frequency_hz: int
    control_frequency_hz: int

    current_mode_idx: int 
    automaton_modes: List[Mode]
    goal_modes_idx: int
    initial_modes_idx: int
    

