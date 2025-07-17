# from .core_interfaces import GuardABC, ResetABC
# from typing import Optional, Dict, Any
# from dataclasses import dataclass
# from utils import import_class
# from typing import List
# from automaton_interfaces.msg import AutomatonGuardEvaluation as GuardEvaluation, AutomatonTransitionEvaluation as TransitionEvaluation, AutomatonTransitionEvaluations as TransitionEvaluations, AutomatonMode as Mode
# from .states import States
# from utils import now_to_ros_time_msg

# class Transitions: 
#     _transitions: List['Transition']

#     def evaluate_transitions(self, current_mode: Mode, states: States) -> List[TransitionEvaluations]:
#         transition_evaluations:TransitionEvaluations = TransitionEvaluations(
#             current_mode=Mode,
#             stamp=now_to_ros_time_msg()
#         )

#         for transition in self._transitions: 
#             transition_evaluations.transition_evaluations.append(
#                 transition.evaluate_transition()
#             )

#     def perform_reset(self, transition_name: str):
#         pass
  
# @dataclass
# class Transition:
#     """
#     Transition is a blueprint for an instance of 
#     a hybrid automaton transition as defined in the
#     Hybrid Automaton FAMD, transition contains details 
#     required for transition evaluation including the name
#     of the transition which is also a describer of that transition
#     target_mode which is the mode int value this transition goes to
#     guard and reset, guard being a function which inherits from 
#     GuardABC abstract class and reset being Optional and extending
#     from ResetABC abstract class, priority being the priority of that 
#     transition.
#     """
#     _name: str
#     _target_mode: int
#     _guards: 'Guards'
#     _resets: Optional['Resets']
#     _priority: int = 0

#     def evaluate_transition(self, states: States) -> TransitionEvaluation:
#         transition_evaluation: TransitionEvaluation = TransitionEvaluation(
#             name = self._name,
#             target_mode = self._target_mode,
#             priority = self._priority,
#         )

#         for guard in self._guards:
#             pass
            


#     def perform_reset(self):
#         pass

#     def is_reset(self):
#         if not self._reset is None:
#             return False

#         return True 
    
#     def get_name(self):
#         return self._name
    
#     def get_priority(self):
#         return self._priority
    
#     @classmethod
#     def load_transition_from_famd(
#         cls,
#         name: str,
#         cfg: Dict[str, Any],
#         guards: Dict[str, Dict[str, Any]],
#         resets: Dict[str, Dict[str, Any]],
#     ) -> "Transition":
#         """
#         load the transition guards
#         and initialize them
#         """
#         priority = cfg.get('priority', 0)
#         guard_cfg = guards[cfg['guard']]
#         guard_cls = import_class(guard_cfg['module'], guard_cfg['class_name'])
#         guard_inst: GuardABC = guard_cls(**guard_cfg.get('configuration', {}))

#         reset_inst: Optional[ResetABC] = None
#         if cfg.get('reset'):
#             rst_cfg = resets[cfg['reset']]
#             rst_cls = import_class(rst_cfg['module'], rst_cfg['class_name'])
#             reset_inst = rst_cls(**rst_cfg.get('configuration', {}))

#         return cls(
#             name=name,
#             target_mode=cfg['target_mode'],
#             guard=guard_inst,
#             reset=reset_inst,
#             priority=priority,
#         )