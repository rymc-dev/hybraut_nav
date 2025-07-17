from dataclasses import dataclass
from .core_interfaces import ResetInterface
from .states import States
from typing import List
from automaton_interfaces.msg import AutomatonReset as Reset, AutomatonResets 
from utils.now_to_ros_time_msg import now_to_ros_time_msg
from typing import Dict

class ResetWrapper:
    _reset: ResetInterface

    def evaluate_reset(self, states: States) -> Reset:
        msg = Reset()

    def load_reset_from_famd(cls, reset_data: Dict[str, any]):
        pass

if __name__ == '__main__':
    reset = ''

@dataclass
class Resets:
    _resets = List[ResetWrapper]

    def perform_resets(self, triggering_transition: str, states: States) -> AutomatonResets:
        resets: AutomatonResets = AutomatonResets(
            triggering_transition=triggering_transition,
            stamp=now_to_ros_time_msg()
        )

        for reset in self._resets:
            resets.resets.append(
                reset.perform_reset(states)
            )
            