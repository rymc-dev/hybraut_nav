# status.py

from enum import Enum, auto

class HybridAutomatonStatus(Enum):
    ACTIVE = auto()       # Actively evaluating modes, invariants, and transitions
    COMPLETED = auto()    # Reached a final mode or goal condition
    FAILED = auto()       # Invariant violation with no valid transition
    ABORTED = auto()      # Stopped externally
    TRANSITIONING = auto()
    AWAITING_MODE = auto()
    AWAITING_STATE = auto()
