from automaton.resets import ResetABC
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint
from automaton._internal.types import InputSpec

class RemoveVirtualWaypointReset(ResetABC):
    """
    Reset utilized on the transition from waypoint reached back to cruise
    this reset removes the current virtual waypoint in the list and assigns the 
    new current waypoint as the next value in the virtual waypoints list or the
    goal waypoint.
    """

    _state_input_spec = [InputSpec(name='waypoints_state', type=ROSWaypointsState)]
    _reset_targets_spec = [InputSpec(name='waypoints_state', type=ROSWaypointsState)]
    
    def __call__(self, **state_kwargs):
        """Pops the first virtual waypoint and sets the new current waypoint in waypoints state"""
        # Validate input - this calls the parent's validation method
        self._validate_states(**state_kwargs)
        
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        # Remove the first virtual waypoint
        waypoints_state.virtual_waypoints = waypoints_state.virtual_waypoints[1:]
        
        # Update current waypoint
        if len(waypoints_state.virtual_waypoints) > 0:
            waypoints_state.current_waypoint = waypoints_state.virtual_waypoints[0]
        else:
            waypoints_state.current_waypoint = waypoints_state.goal_waypoint
        
        output = {'waypoints_state': waypoints_state}
        super()._validate_reset_output(output)
        return output
    
    def _validate_states(self, **state_kwargs) -> None:
        """Validate the state inputs for the callback"""
        # Call parent validation first
        super()._validate_states(**state_kwargs)

        if len(state_kwargs['waypoints_state'].virtual_waypoints) < 1:
            raise AttributeError('invalid reset attempted, there should be more than 0 virtual waypoints for this transition to occur.')
        
if __name__ == '__main__':
    reset:ResetABC = RemoveVirtualWaypointReset()
    state_kwargs = {
        'waypoints_state': ROSWaypointsState(virtual_waypoints=[ROSWaypoint()])
    }
    try:
        reset_outputs = reset.__call__(**state_kwargs)
    except Exception as e:
        print (e)

    print (reset_outputs)