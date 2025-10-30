""" 

"""
from enum import Enum, auto

class UrgencyEnums(Enum):
    EAGER = auto()
    LAZY = auto()
    DELAYED = auto()

    @staticmethod
    def urgency_descriptions(urgency: 'UrgencyEnums') -> str:
        match urgency:
            case UrgencyEnums.EAGER:
                return "Transition must occur immediately when enabled — time cannot pass."
            case UrgencyEnums.LAZY:
                return "Transition may occur at any time after it's enabled — time can pass."
            case UrgencyEnums.DELAYED:
                return "Transition can occur only after a specific delay or guard condition."
            case _:
                return "Invalid Urgency Type"
