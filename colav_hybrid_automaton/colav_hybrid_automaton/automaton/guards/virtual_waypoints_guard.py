from .guard import Guard
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint
from typing import List

class VirtualWaypointsGuard(Guard):
    """
    guard class on call which check if current waypoints 
    state contains a virtual waypoint
    """

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)

        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        virtual_waypoints: List[ROSWaypoint] = waypoints_state.virtual_waypoints 
        return len(virtual_waypoints) > 0 
    
    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)
        
        try: 
            try:
                if not isinstance(state_kwargs['waypoints_state'], ROSWaypointsState):
                    raise TypeError('waypoints state invalid type') 
            except KeyError:
                raise KeyError('waypoints_state value not given in __call__')
        except Exception as e:
            raise e