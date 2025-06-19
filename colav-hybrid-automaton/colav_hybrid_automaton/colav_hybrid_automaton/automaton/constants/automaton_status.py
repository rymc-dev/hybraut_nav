from enum import IntEnum
from typing import Union

class HybridAutomatonStatusEnum(IntEnum):
    INITIALIZING = 1
    ACTIVE_MODE = 2
    TRANSITIONING = 3
    COMPLETED = 4
    DEACTIVATING = 5
    ERROR = 6

# Use this for type hints
HybridAutomatonStatusValue = Union[HybridAutomatonStatusEnum, int]