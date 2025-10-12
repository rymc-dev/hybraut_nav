from enum import IntEnum
from typing import Union

class HybridAutomatonStatusEnum(IntEnum):
    INITIALIZING = 0
    ACTIVE_MODE = 1
    TRANSITIONING = 2
    COMPLETED = 3
    DEACTIVATING = 4
    ERROR = 5

# Use this for type hints
HybridAutomatonStatusValue = Union[HybridAutomatonStatusEnum, int]