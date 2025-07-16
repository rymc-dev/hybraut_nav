from nodes.guards import GuardABC
from colav_interfaces.msg import (
    WaypointsState as ROSWaypointsState,     
    Waypoint as ROSWaypoint
)
from nodes._internal.types import InputSpec
from typing import List


class VirtualWaypointsGuard(GuardABC):
    """
    guard class on call which check if current waypoints 
    state contains a virtual waypoint
    """

    _state_input_spec = [
        InputSpec(name='waypoints_state', type=ROSWaypointsState)
    ]

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)

        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        virtual_waypoints: List[ROSWaypoint] = waypoints_state.virtual_waypoints 
        return len(virtual_waypoints) > 0 
    
if __name__ == '__main__':
    init_kwarg_names = VirtualWaypointsGuard.init_input_names()
    guard: GuardABC = VirtualWaypointsGuard()
    state_kwarg_names = VirtualWaypointsGuard.state_input_names()
    state_kwargs = {
        state_kwarg_names[0]: ROSWaypointsState()
    }
    guard_evaluation:bool = guard.__call__(**state_kwargs)
    print (guard_evaluation)
