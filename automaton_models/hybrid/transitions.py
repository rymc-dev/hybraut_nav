from dataclasses import dataclass, field
from typing import Any, Dict, List

from rclpy.callback_groups import CallbackGroup
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile, qos_profile_default

from automaton_interfaces.msg import TransitionEvaluationMSG
from component_interfaces.registry_interface import ComponentRegistry
from constants.urgency import UrgencyEnums
from context import EvaluationContext
from guards import GuardWrapper



# @dataclass 
# class TransitionEvaluationBus:
#     _transition_evaluation_publisher: Publisher
#     _topic: str = field(init=False, default='/automaton/transition_evaluation')
#     _qos: QoSProfile = field(
#         init=True,
#         default='/automaton/transition_evaluation'
#     )
    

class TransitionRegistry(ComponentRegistry):

    @classmethod
    def load_transition_registry_from_amdl(cls, transition_dict: dict):
        transitions: Dict[str, Transition] = {}
        for transition_name, transition_value in transition_dict.items():
            transitions[transition_name] = Transition.load_transition_from_amdl(
                transition_name=transition_name,
                transition_value=transition_value
            )

        return cls(
            cls(_components=transitions)
        )

@dataclass
class Transition:
    _name: str = field(init=True)
    _target_mode: int = field(init=True)
    _guard_refs: List[str] = field(init=True)
    _reset_refs: List[str] = field(init=True, default=None)
    _urgency: UrgencyEnums = field(init=True, default_factory=lambda: UrgencyEnums.EAGER) # EAGER urgency for transition means the transition occurs automatically.
    _metadata: Dict[str, Any] = field(init=True, default_factory=lambda: {})

    def __post_init__(self):
        pass

    def get_target_mode(self):
        return self._target_mode

    def get_guard_refs(self):
        return self._guard_refs
    
    def get_reset_refs(self):
        return self._reset_refs
    
    def get_urgency(self):
        return self._urgency

    def evaluate_transition(self, ctx: EvaluationContext):
        """ 
        evaluates the guard condition for transition, if any 
        return as true we get the reset refs and return for the priority 
        transition
        """
        msg:TransitionEvaluationMSG = TransitionEvaluationMSG()
        msg.name = self._name
        msg.target_mode = self._target_mode
        msg._priority = self._priority
        msg._should_transition = True

        try:
            guards: List[GuardWrapper] = ctx.guard_registry.get_components_by_names(self._guard_refs)


            guard_evaluations = []
            for guard in guards:
                try:
                    eval: bool = guard._evaluate(ctx)
                except Exception as e:
                    msg.error = True
                    msg.message.append(f"guard evaluation failed: {str(e)}")
                if not eval:
                    msg._should_transition = False
                
            msg._expected_resets = self._reset_refs

        except Exception as e:
            msg.error = True
            msg.message = f"exception occured: {str(e)}"

        return msg
    
    @classmethod
    def load_transition_from_amdl(cls, transition_name: str, transition_value: Dict[str, Any]):
        print (f"{transition_name}, {transition_value}")
        name = transition_name
        target_mode = transition_value['target_mode']
        guard_ref = transition_value['guard']
        reset_ref = transition_value.get('reset')
        urgency = transition_value.get('urgency')

        if urgency is None:
            return cls(
                _name=name,
                _target_mode=target_mode,
                _guard_refs=guard_ref,
                _reset_refs=reset_ref,
            )
        
        urgency = UrgencyEnums.EAGER
        
        return cls(
            _name=name,
            _target_mode=target_mode,
            _guard_refs=guard_ref,
            _reset_refs=reset_ref,
            _urgency=urgency
        )

    
    def execute_transition(self, ctx: EvaluationContext):
        """ 
        This executes the transition, performing the reset and publishing the new mode.
        """
        pass