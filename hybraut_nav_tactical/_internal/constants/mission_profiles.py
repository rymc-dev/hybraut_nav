# automaton_status

from enum import Enum, auto

# TODO: In future this could change behaviour of hybrid automaton depending on what state our agent vessel is in
# whether it be hybrofoiling or sailing

class HybridAutomatonMissionProfile(Enum):
    """Enumeration of internal states for a hybrid automaton lifecycle."""

    COLAV = auto() # FOR NOW ONLY ONE HYBRID MISSION PROFILE
    """Currently executing within an active mode (continuous evolution)."""
