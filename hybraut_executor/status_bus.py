from dataclasses import dataclass
from hybraut_interfaces.msg import AutomatonStatus
from enum import Enum

class StatusEnum(Enum):
    INACTIVE: AutomatonStatus.INACTIVE
    ACTIVE: AutomatonStatus.ACTIVE
    TRANSITIONING: AutomatonStatus.TRANSITIONING
    WARNING: AutomatonStatus.WARNING
    ERROR: AutomatonStatus.ERROR
    RECOVERING: AutomatonStatus.RECOVERING
    FATAL: AutomatonStatus.FATAL
    MISSION_COMPLETE: AutomatonStatus.MISSION_COMPLETE

@dataclass
class StatusBus:
    pass