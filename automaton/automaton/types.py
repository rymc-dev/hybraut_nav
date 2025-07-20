from dataclasses import dataclass
from .automaton_registrys import StateRegistry
from builtin_interfaces.msg import Time, Duration
from typing import Dict, Any

@dataclass
class MsgType:
    """
    Data structure for ROS2 message type specification.
    
    Attributes:
        pkg (str): Package path for the message (e.g., "geometry_msgs.msg")
        msg (str): Message class name (e.g., "Twist")
    """
    pkg: str
    msg: str
    
    def __post_init__(self):
        """Validate message type specification after initialization."""
        if not self.pkg or not self.msg:
            raise ValueError("Both pkg and msg must be non-empty strings")
        
@dataclass
class EvaluationContext:
    """
    Context class that holds evaluation state and parameters.
    initialized on automaton evaluation time, and passed to evaluation
    functions.
    """
    states: StateRegistry
    current_mode: int
    stamp: Time
    metadata: Dict[str, Any]

    def get_state_values(state_names) -> Dict[str, Any]:
        pass

    def get_state_age(state_name) -> Duration:
        pass

    def get_event_history() -> None:
        """not sure how to implement this yet."""
        pass