from .guard import Guard
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState,
    WaypointsState as ROSWaypointsState
)

class LOSClearToWaypointGuard(Guard):
    """
    A guard condition for a hybrid automaton that evaluates whether the agent's line of 
    sight to the current waypoint is clear and not obstructed within a specified threshold.
    
    This class is typically used in a state machine or behavior tree context to determine 
    whether a transition condition is met clear line of sight (LOS) to goal waypoint

    When called with the agent state, waypoints state, unsafe set state obstacles state
    this class checks based on the los_distance_threshold if we intercept unsafe set 
    which is a safety region determined in real time for dynamic obstacles and if we intercept
    any static obstacles individually.

    Args:
        los_distance_threshold (float, optional): 
            The distance threshold for los of the agent not being clear.

    Raises:
        TypeError: If 'los_distance_threshold' is not a float.
        ValueError: If 'los_distance_threshold' is less than 0.01.
    """
    def __init__(self, **kwargs):
        """
            los_distance_threshold: float: represents the distance which we analyse los 
                                           to determine if los is clear to the waypoint
        """
        super().__init__(**kwargs)

        self.los_distance_threshold = kwargs.get('los_distance_threshold')
    
    def __call__(
        self,
        agent_state: ROSAgentState,
        obstacles_state: ROSObstaclesState,
        unsafe_set_state: ROSUnsafeSetState,
        waypoints_state: ROSWaypointsState     
     ):
        return super().__call__([agent_state, obstacles_state, unsafe_set_state, waypoints_state])
    
    def _validate_initialization(self, *args, **kwargs):

        if not isinstance(self.los_distance_threshold, float):
            raise TypeError('los_distance_threshold must be type float')
        if self.los_distance_threshold < 1.0: 
            raise ValueError('line of sight distance treshold must be greater than 1.0 meters')

        return super()._validate_initialization(*args, **kwargs)
    
    def _validate_state_inputs(self, *state_inputs):
        # if not len(state_inputs) == 4:
        #     raise Va 


        return super()._validate_state_inputs(*state_inputs)