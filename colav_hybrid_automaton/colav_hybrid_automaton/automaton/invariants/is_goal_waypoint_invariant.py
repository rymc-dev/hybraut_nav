from .invariant import InvariantABC
from colav_interfaces.msg import (
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)

class IsGoalWaypointInvariant(InvariantABC): 

    def __call__(self, **state_kwargs) -> bool:
        super().__call__(**state_kwargs)
        
        waypoints_state:ROSWaypointsState = state_kwargs.get('waypoints_state')
        if len(waypoints_state.virtual_waypoints) > 0:
            return False
        elif waypoints_state.current_waypoint == waypoints_state.goal_waypoint:
            return True
        else:
            raise Exception(f"exception occured in 'colav_hybrid_automaton.automaton.invariants.Invariants.is_at_final_waypoint', unexpected waypoint state.")

    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)

        try: 
            if not isinstance(state_kwargs['waypoints_state'], ROSWaypointsState):
                raise TypeError('waypoints_state invalid type')
            
            if not isinstance(state_kwargs['waypoints_state'].current_waypoint, ROSWaypoint):
                raise ValueError('invalid current waypoint value')
        except KeyError:
            raise KeyError('waypoints state not given in __call__')
        

