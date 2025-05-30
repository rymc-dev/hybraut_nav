# automaton_status

from enum import Enum, auto

class HybridAutomatonStatus(Enum):
    """Enumeration of internal states for a hybrid automaton lifecycle."""

    INITIALIZING = auto()
    """Used when moving from configured state to active"""

    EXECUTING_MODE = auto()
    """Currently executing within an active mode (continuous evolution)."""

    TRANSITIONING = auto()
    """A transition is occurring between modes (guard condition triggered, reset in progress)."""

    COMPLETED = auto()
    """Final goal or terminal condition has been reached; automaton is shutting down cleanly."""

    DEACTIVATING = auto()
    """Automaton is being externally stopped or deactivated."""

    ERROR = auto()
    """An unrecoverable error occurred during execution, transition, or mode evaluation."""
