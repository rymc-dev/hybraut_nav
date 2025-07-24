from typing import List, Dict
from automaton_interfaces.msg import HybridAutomatonMode

def validate_mode(available_modes: Dict[int, str], mode: HybridAutomatonMode) -> str:
    if not isinstance(mode, HybridAutomatonMode):
        raise TypeError(f"Invalid mode type: expected 'hybrid_automaton_interfaces.msg.HybridAutomatonMode', but got '{type(mode).__name__}' instead.")
    if mode.type not in list(available_modes.keys()):
        raise ValueError(f"mode type id received: '{mode}', is not one of the available hybrid automaton modes: '{available_modes}'")
    
    return mode