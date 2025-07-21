
from dataclasses import dataclass
from typing import List
from .aci_interfaces import ResetInterface
from automaton_interfaces.msg import AutomatonReset, AutomatonResets
from utils import now_to_ros_time_msg
from .context import EvaluationContext

@dataclass
class ResetWrapper:
    pass

@dataclass
class ResetsRegistry:
    _resets = List[ResetWrapper]

    def perform_resets(self, triggering_transition: str, evaluation_context: EvaluationContext) -> AutomatonResets:
        resets: AutomatonResets = AutomatonResets(
            triggering_transition=triggering_transition,
            stamp=now_to_ros_time_msg()
        )

        for reset in self._resets:
            resets.resets.append(
                reset.perform_reset(evaluation_context.states)
            )


            