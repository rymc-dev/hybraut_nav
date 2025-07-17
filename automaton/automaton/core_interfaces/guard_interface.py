"""
Hybrid Automaton Guard Interface

This interface defines the contract for guard functions in the hybrid automaton framework.
Guard functions are used to determine whether a transition between modes should occur.

All guard implementations must inherit from this interface and implement the required methods.
Guards are evaluated during the hybrid automaton's execution to determine if transition
conditions are met based on the current system state.

Example Usage:
    class DistanceThresholdGuard(GuardInterface):
        _init_input_spec = [
            InputSpec.create_input_spec("distance_threshold", float)
        ]
        _state_input_spec = [
            InputSpec.create_input_spec("agent_state", AgentState),
            InputSpec.create_input_spec("waypoints_state", WaypointsState)
        ]
        
        def __call__(self, **state_kwargs) -> bool:
            super().__call__(**state_kwargs)
            # Implementation logic here
            distance = self._calculate_distance(
                state_kwargs["agent_state"], 
                state_kwargs["waypoints_state"]
            )
            return distance <= self.distance_threshold
"""

from abc import abstractmethod
from .hybrid_automaton_component_interface import HybridAutomatonComponentInterface


class GuardInterface(HybridAutomatonComponentInterface):
    """
    Interface for hybrid automaton guard functions.
    
    Guard functions evaluate transition conditions during hybrid automaton execution.
    They determine whether a transition from one mode to another should occur based
    on the current system state.
    
    This interface extends the base HybridAutomatonComponentInterface to provide
    guard-specific functionality.
    
    Attributes:
        logger: ROS2 logger instance for debugging and information output
        is_initialized: Flag indicating if the guard has been properly initialized
    """

    _evaluation_output_type = bool
    _component_type = "Guard"

    @abstractmethod
    def _evaluate(self, **state_kwargs) -> bool:
        """
        here you implement the evaluation you wish to perform for you guard,
        this will be utilized by the __call__ function on runtime
        """
        pass
