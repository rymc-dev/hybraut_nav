from typing import List

def validate_mode(available_modes: List[str], mode: str) -> str:
    if not isinstance(mode, str):
        raise TypeError(f"Invalid mode type: expected 'str', but got '{type(mode).__name__}' instead.")
    if mode not in available_modes:
        raise ValueError(f"mode received: '{mode}', is not one of the available hybrid automaton modes: '{available_modes}'")
    
    return mode