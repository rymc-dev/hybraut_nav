# from dataclasses import dataclass
# from .core_interfaces import ResetABC
# from .states import States
# from typing import List
# from automaton_interfaces.msg import AutomatonReset as Reset, AutomatonResets 
# from utils.now_to_ros_time_msg import now_to_ros_time_msg

# class ResetWrapper:
#     _inst: ResetABC

#     def perform_reset(self, states: States) -> Reset:
#         pass

# @dataclass
# class Resets:
#     _resets = List[ResetWrapper]

#     def perform_resets(self, triggering_transition: str, states: States) -> AutomatonResets:
#         resets: AutomatonResets = AutomatonResets(
#             triggering_transition=triggering_transition,
#             stamp=now_to_ros_time_msg()
#         )

#         for reset in self._resets:
#             resets.resets.append(
#                 reset.perform_reset(states)
#             )
            