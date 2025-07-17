"""
Hybrid Automaton Invariant Interface

This interface defines the contract for invariant functions in the hybrid automaton framework.
Invariant functions are used to determine whether a transition staying in a mode without transitioning is valid.

All invariant implementations must inherit from this interface and implement the required methods.
Invariants are evaluated during the hybrid automaton's execution to determine if it is allowed
to stay in a mode without transitioning every evaluation.

Example Usage:
    class CanIStayInModeInvariant(InvariantInterface):
        _init_input_spec = [
            InputSpec.create_input_spec("distance_threshold", float)
        ]
        _state_input_spec = [
            InputSpec.create_input_spec("agent_state", AgentState),
            InputSpec.create_input_spec("waypoints_state", WaypointsState)
        ]

        def __call__(self, **state_kwargs) -> bool:
            super().__call__(**state_kwargs)
            # Your invariant logic here
            return True
"""

from abc import abstractmethod
from .hybrid_automaton_component_interface import  HybridAutomatonComponentInterface


class InvariantInterface(HybridAutomatonComponentInterface):
    """
    Interface for hybrid automaton invariant functions.
    
    Invariant functions evaluate if we can stay in the current mode based on
    the system state. This interface extends the base HybridAutomatonComponentInterface
    to provide invariant-specific functionality.
    
    Attributes:
        logger: ROS2 logger instance for debugging and information output
        is_initialized: Flag indicating if the invariant has been properly initialized
    """

    _component_type = "Invariant"
    _evaluation_output_type = bool

    @abstractmethod
    def _evaluate(self, **state_kwargs) -> bool:
        """here we implement the evaluation for the invariant, this is called in the guard
        an invariants args are keyword args, in this we expect the name of a state as well as it's current value.
        """
        pass