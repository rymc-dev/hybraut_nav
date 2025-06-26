from .guard import Guard
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from math import dist as euclidean_distance

class WaypointReachedGuard(Guard):
    """
    Guard condition that evaluates whether the agent has reached the current waypoint.

    This guard returns `True` if the Euclidean distance between the agent's position and the 
    current waypoint's position is less than or equal to the waypoint's acceptance radius. 
    It is typically used in a hybrid automaton to trigger a transition once the agent is close 
    enough to the target waypoint.

    Expected keyword arguments:
        agent_state (ROSAgentState): The current state of the agent, including its pose.
        waypoints_state (ROSWaypointsState): The state containing the current waypoint and its acceptance radius.

    Returns:
        bool: True if the agent is within the acceptance radius of the current waypoint, False otherwise.

    Raises:
        TypeError: If `agent_state` or `waypoints_state` is of the wrong type.
        ValueError: If `current_waypoint` inside `waypoints_state` is not valid.
    """

    def __call__(self, **state_kwargs) -> bool:
        super().__call__(**state_kwargs) 

        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')

        agent_coords = [agent_state.pose.position.x, agent_state.pose.position.y]
        waypoint_coords = [
            waypoints_state.current_waypoint.position.x,
            waypoints_state.current_waypoint.position.y
        ]
        
        return euclidean_distance(agent_coords, waypoint_coords) <= \
               waypoints_state.current_waypoint.acceptance_radius
    
    def _validate_states(self, **state_inputs):
        super()._validate_states(**state_inputs)

        if not isinstance(state_inputs.get('agent_state'), ROSAgentState):
            raise TypeError('agent_state invalid type')
        if not isinstance(state_inputs.get('waypoints_state'), ROSWaypointsState):
            raise TypeError('waypoints_state invalid type')

        try:
            if not isinstance(state_inputs.get('waypoints_state').current_waypoint, ROSWaypoint):
                raise ValueError('current waypoint is invalid.')
        except Exception as e: 
            raise e 
