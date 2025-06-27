from .reset import Reset
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint

class RemoveFirstWaypoint(Reset):
    """
    Reset utilized on the transition from waypoint reached back to cruise
    this reset removes the current virtual waypoint in the list and assigns the 
    new current waypoint as the next value in the virtual waypoints list or the
    goal waypoint.
    """

    def __init__(self, **init_kwargs):
        # Call parent constructor to properly initialize the reset
        reset_targets = {
            'waypoints_state': ROSWaypointsState
        }
        super().__init__(reset_targets, **init_kwargs)
    
    def __call__(self, **state_kwargs):
        """Pops the first virtual waypoint and sets the new current waypoint in waypoints state"""
        # Validate input - this calls the parent's validation method
        self._validate_states(waypoints_state)
        
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        # Remove the first virtual waypoint
        waypoints_state.virtual_waypoints = waypoints_state.virtual_waypoints[1:]
        
        # Update current waypoint
        if len(waypoints_state.virtual_waypoints) > 0:
            waypoints_state.current_waypoint = waypoints_state.virtual_waypoints[0]
        else:
            waypoints_state.current_waypoint = waypoints_state.goal_waypoint
        
        return super()._validate_reset_output({'waypoints_state': waypoints_state})
    
    def _validate_states(self, **state_kwargs) -> None:
        """Validate the state inputs for the callback"""
        # Call parent validation first
        super()._validate_states(**state_kwargs)

        try:
            try:
                if not isinstance(state_kwargs['waypoints_state'], ROSWaypointsState):
                    raise TypeError()
                if len(state_kwargs['waypoints_state'].virtual_waypoints) < 1:
                    raise AttributeError()
            except KeyError:
                raise KeyError()
        except Exception as e: 
            raise e