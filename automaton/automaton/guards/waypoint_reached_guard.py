from automaton.guards import GuardABC
from automaton._internal.types import InputSpec
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from math import dist as euclidean_distance


class WaypointReachedGuard(GuardABC):
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

    _state_input_spec = [
        InputSpec(name='agent_state', type=ROSAgentState),
        InputSpec(name='waypoints_state', type=ROSWaypointsState)
    ]

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

if __name__ == '__main__':
    from geometry_msgs.msg import Point 
    init_kwarg_names = WaypointReachedGuard.init_input_names()
    init_kwargs = {}
    guard: GuardABC = WaypointReachedGuard(**init_kwargs)

    state_kwarg_names = WaypointReachedGuard.state_input_names()
    state_kwargs = {
        state_kwarg_names[0]: ROSAgentState(),
        state_kwarg_names[1]: ROSWaypointsState()
    } 
    guard_evaluation: bool = guard.__call__(**state_kwargs)
    print (guard_evaluation)