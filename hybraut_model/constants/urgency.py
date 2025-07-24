""" 

"""
from enum import Enum, auto

class UrgencyEnums(Enum):
    """
    """
    EAGER = auto()
    LAZY = auto()
    DELAYED = auto()

    def urgency_descriptions(urgency: 'UrgencyEnums') -> str:
        """ 
        """
        match urgency:
            case UrgencyEnums.EAGER:
                result = "Transition must occur immediately when enabled — time cannot pass."
            case UrgencyEnums.LAZY:
                result = "Transition may occur at any time after it's enabled — time can pass."
            case UrgencyEnums.DELAYED:
                result = "Transition can occur only after a specific delay or guard condition."
            case _:
                result = "Invalid Urgency Type"

        return result