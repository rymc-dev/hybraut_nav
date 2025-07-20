


# @dataclass
# class Mode:
#     _id: int
#     _name: str
#     _description: str
#     _dynamics: DynamicsWrapper
#     _transitions: List[Transition]
#     _invariant_refs: List[str]
#     _entry_actions: List[str]
#     _exit_actions: List[str]
#     _is_goal_mode: bool

#     def on_enter(context: EvaluationContext):
#         pass

#     def on_exit(context: EvaluationContext):
#         pass

#     def evaluate_invariants(context: EvaluationContext) -> bool:
#         pass

#     from automaton_interfaces.msg import AutomatonTransitionEvaluations
#     def evalute_transitions() -> AutomatonTransitionEvaluations:
#         pass

# @dataclass
# class EvaluationContext:
#     _state: StateRegistry
#     _current_mode: Mode
#     _timestamp: float
#     _event_history: List[AutomatonEvent]
#     _metadata: Dict[str, Any]

#     def get_state_value(name: str):
#         # will return the state values based on the key
#         pass

#     def get_state_age(name: str):
#         # gets the age of the state
#         pass

#     def add_metadata(key: str, value: any):
#         pass

# class TransitionResult:
#     _success: bool
#     _new_mode: int
#     _errors: List[str]
#     _warnings: List[str]


# from automaton.automaton_registrys import GuardsRegistry
# from automaton.automaton_registrys import ResetsRegistry
# from automaton_interfaces.msg import AutomatonTransitionEvaluation
# from automaton_interfaces.msg import AutomatonReset, AutomatonResets
# from typing import Tuple

# @dataclass
# class Transition:
#     _name: str
#     _target_mode: int
#     _guard_ref: str
#     _reset_ref: Optional[str]
#     _priority: int
#     _metadata: Dict[str, Any]

    
#     def evaluate(context: EvaluationContext, guards_registry: GuardsRegistry) -> AutomatonTransitionEvaluation:
#         # here we perform a transition evaluation to check if the transition is enabled
#         pass

#     def execute(self, context: EvaluationContext, resets_registry: ResetsRegistry) -> Tuple[TransitionResult, AutomatonResets]: 
#         # the guard for this transition has been evaluated as being true, therefore we attempt to execute the transition
#         pass

