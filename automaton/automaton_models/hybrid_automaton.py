# from typing import Set, List, Optional
# from dataclasses import dataclass


# class ValidationResult:
#     pass

# class EventBus: 
#     pass

# class AutomatonRenderer:
#     """renders the automaton in mmd format"""
#     pass

# @dataclass
# class Transition:
#     _name: str
#     _source_mode: int
#     _target_mode: int
#     _guard_ref: str
#     _reset_ref: Optional[str]
#     _priority: int
#     _urgency: UrgencyLevel
#     _metadata: Dict[str, Any]
    
#     def is_enabled(self, context: EvaluationContext) -> bool:
#         pass

#     def execute(self, context: EvaluationContext) -> TransitionResult:
#         pass

#     def load_transition_from_famd(cls, name, config, guard_ref, reset_ref) -> Transition:
#         pass

# class EvaluationContext:
#     _states: StateRegistry
#     _current_mode: int
#     _timestamp: float
#     _event_history: List[AutomatonEvent]
#     _metadata: Dict[str, Any]
    
#     def get_state_value(name: str) -> Any:
#         pass

#     def get_state_age(name: str) -> float:
#         pass

#     def add_metadata(key: str, value: Any):
#         pass

# @dataclass
# class ValidationResult:
#     _is_valid: bool
#     _errors: List[str]
#     _warnings: List[str]

# @dataclass
# class TransitionResult:
#     _success: bool
#     _new_mode: int
#     _reset_applied: bool
#     _error_message: Optional[str]

# @dataclass
# class GuardEvaluation:
#     _enabled: bool
#     _confidence: float
#     _metadata: Dict[str, Any]









# class HybridAutomaton:
#     _id: str
#     _name: str
#     _description: str
#     _version: str
#     _initial_mode: int
#     _goal_modes: Set[int]
#     _modes: ModeRegistry
#     _states: StateRegistry
#     _guards: GuardsRegistry
#     _resets: ResetRegistry
#     _invariants: InvariantRegistry
#     _transition_evaluation_frequency: int 
#     _control_frequency: int
#     _event_bus: EventBus 
    
#     def validate(self) -> ValidationResult:
#         pass

#     def get_mode(self, mode_id: int) -> Mode:  
#         pass

#     def get_active_transitions(self, current_mode) -> List[Transition]:
#         pass

# @dataclass
# class AutomatonEvent: 
#     _timestamp: float
#     _event_type: EventType 
#     _source: str 
#     _data: Dict[str, Any] 

# class EventBus:
#     _subscribers: Dict[EventType, List[callable]]
    
#     def publish(event: AutomatonEvent): pass
#     def subscribe(event_type: EventType, callback: Callable): pass

# class AutomatonExecutor:
#     _automaton: HybridAutomaton
#     _current_mode: int
#     _execution_state: ExecutionState # execution state is the watchdog automaton state, I need to move this component to runtime directory

#     def start_execution(self):
#         pass

#     def stop_execution(self):
#         pass

#     def step(self):
#         pass

#     def handle_mode_transition(transition: Transition):
#         pass