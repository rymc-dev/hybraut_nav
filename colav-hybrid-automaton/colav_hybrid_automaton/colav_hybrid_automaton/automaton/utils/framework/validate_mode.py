from typing import List

def validate_mode(available_modes: List[str], mode: str) -> str:
    if not isinstance(mode, str):
        raise TypeError('mode is not of correct type string')
    if mode not in available_modes:
        raise ValueError('current mode is not in automaton modes')
    
    return mode