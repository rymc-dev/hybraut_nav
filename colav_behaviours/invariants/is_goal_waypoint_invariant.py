from automaton_models.hybrid.aci_interfaces import InvariantInterface
from colav_interfaces.msg import (
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from nodes._internal.types import InputSpec

class IsGoalWaypointInvariant(InvariantInterface): 

    _state_input_spec = [
        InputSpec(name='waypoints_state', type=ROSWaypointsState)
    ]

    def __call__(self, **state_kwargs) -> bool:
        super().__call__(**state_kwargs)
        
        waypoints_state:ROSWaypointsState = state_kwargs.get('waypoints_state')
        if len(waypoints_state.virtual_waypoints) > 0:
            return False
        elif waypoints_state.current_waypoint == waypoints_state.goal_waypoint:
            return True
        else:
            raise Exception(f"exception occured in 'colav_hybrid_automaton.automaton.invariants.Invariants.is_at_final_waypoint', unexpected waypoint state.")
        
if __name__ == '__main__':
    invariant: InvariantInterface = IsGoalWaypointInvariant()
    state_input_names = IsGoalWaypointInvariant.state_input_names()
    state_kwargs = {
        state_input_names[0]: ROSWaypointsState()
    }

    invariant_value: bool = invariant.__call__(**state_kwargs)
    print (invariant_value)
        

