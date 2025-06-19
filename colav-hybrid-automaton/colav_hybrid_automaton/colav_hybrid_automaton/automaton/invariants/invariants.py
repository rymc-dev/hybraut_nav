from colav_interfaces.msg import WaypointsState
from .invariant_abstract import HybridAutomatonInvariant
from colav_interfaces.msg import Waypoint

class IsGoalWaypoint(HybridAutomatonInvariant): 

    def __call__(waypoints_state: WaypointsState) -> bool:
        super.__call__([waypoints_state])
        
        if len(waypoints_state.virtual_waypoints) > 0:
            return False
        elif waypoints_state.current_waypoint == waypoints_state.goal_waypoint:
            return True
        else:
            raise Exception(f"exception occured in 'colav_hybrid_automaton.automaton.invariants.Invariants.is_at_final_waypoint', unexpected waypoint state.")

    def _validate_state_inputs(self, *state_inputs):
        super()._validate_state_inputs(*state_inputs)

        waypoints_state: WaypointsState = state_inputs[0]
        if not isinstance(waypoints_state, WaypointsState):
            raise TypeError('waypoints state invalid type')
        
        if not isinstance(waypoints_state.current_waypoint, Waypoint):
            raise ValueError('invalid current waypoint value')

class TrivialInvariant(HybridAutomatonInvariant):
    def __call__(self):
        return True

class FailingInvariant(HybridAutomatonInvariant):
    def __call__(self, *state_inputs):
        return False