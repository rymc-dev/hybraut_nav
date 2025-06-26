from .guard import Guard
from colav_interfaces.msg import WaypointsState as ROSWaypointsState

class VirtualWaypointsGuard(Guard):
    """
    guard class on call which check if current waypoints 
    state contains a virtual waypoint
    """

    def __call__(self, waypoints_state: ROSWaypointsState):
        super().__call__([waypoints_state])

        virtual_waypoints = waypoints_state.virtual_waypoints
        return len(virtual_waypoints) > 0 
    
    def _validate_state_inputs(self, *state_inputs):
        super()._validate_state_inputs(*state_inputs)

        waypoints_state: ROSWaypointsState = state_inputs[0]
        if not isinstance(waypoints_state, ROSWaypointsState):
            raise TypeError('waypoints state invalid type')