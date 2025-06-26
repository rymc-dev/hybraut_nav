from .guard import Guard
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from math import dist as euclidean_distance

class WaypointReachedGuard(Guard):
    def __call__(self, agent_state: ROSAgentState, waypoints_state: ROSWaypointsState) -> bool:
        super().__call__([agent_state, waypoints_state])  # only keep if base method has side effects

        agent_coords = [agent_state.pose.position.x, agent_state.pose.position.y]
        waypoint_coords = [
            waypoints_state.current_waypoint.position.x,
            waypoints_state.current_waypoint.position.y
        ]
        
        return euclidean_distance(agent_coords, waypoint_coords) <= \
               waypoints_state.current_waypoint.acceptance_radius
    
    def _validate_state_inputs(self, *state_inputs):
        super()._validate_state_inputs(*state_inputs)
    
        agent_state: ROSAgentState = state_inputs[0]
        waypoints_state: ROSWaypointsState = state_inputs[1]

        if not isinstance(agent_state, ROSAgentState):
            raise TypeError('agent_state invalid type')
        if not isinstance(waypoints_state, ROSWaypointsState):
            raise TypeError('waypoints_state invalid type')

        try:
            if not isinstance(waypoints_state.current_waypoint, ROSWaypoint):
                raise ValueError('current waypoint is invalid.')
        except Exception as e: 
            raise e 
