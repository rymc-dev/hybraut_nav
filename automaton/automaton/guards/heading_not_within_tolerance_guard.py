import math
from automaton.guards.guard import GuardABC
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from automaton._internal.utils import (
    delta_heading,
    quaternion_to_heading,
)
from automaton._internal.types import InputSpec


class HeadingNotWithinToleranceGuard(GuardABC):
    """
    A guard condition for a hybrid automaton that evaluates whether the agent's heading 
    is within a specified tolerance of the heading to the current waypoint.

    When called, returns True if the heading error is outside the tolerance.
    """

    _init_input_spec  = [InputSpec(name='heading_tolerance', type=float)]
    _state_input_spec  = [
        InputSpec(name='agent_state', type=ROSAgentState),
        InputSpec(name='waypoints_state', type=ROSWaypointsState)
    ]

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)
        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')

        # Extract positions
        ax = agent_state.pose.position.x
        ay = agent_state.pose.position.y
        wx = waypoints_state.current_waypoint.position.x
        wy = waypoints_state.current_waypoint.position.y

        # If waypoint at agent, aligned
        if ax == wx and ay == wy:
            return False

        # Compute headings
        wrapped_yaw = quaternion_to_heading(
            qx=agent_state.pose.orientation.x,
            qy=agent_state.pose.orientation.y,
            qz=agent_state.pose.orientation.z,
            qw=agent_state.pose.orientation.w
        )
        desired_heading = math.atan2(wy - ay, wx - ax)

        # For large tolerances, detect raw yaw > 180° via quaternion.w sign
        if self.__getattribute__('heading_tolerance') >= math.pi:
            # if quaternion half-angle cos < 0, original yaw > π
            if agent_state.pose.orientation.w < 0:
                raw_yaw = wrapped_yaw + 2 * math.pi
            else:
                raw_yaw = wrapped_yaw
            error = raw_yaw - desired_heading
        else:
            # use wrapped error in [-π, π]
            error = delta_heading(
                x_a=ax, y_a=ay,
                theta_a=wrapped_yaw,
                x_w=wx, y_w=wy
            )

        # consider floating-point boundary: treat near-equal as within tolerance
        outside = abs(error) > self.__getattribute__('heading_tolerance')
        if outside and not math.isclose(abs(error), self.__getattribute__('heading_tolerance')):
            return True
        return False

    def _validate_initialization(self, **init_kwargs):
        super()._validate_initialization(**init_kwargs)


        heading_tol = init_kwargs['heading_tolerance']  # Now safe: key guaranteed present
        if heading_tol < 0.0:
            raise ValueError('heading tolerance cannot be less than 0.0')

if __name__ == "__main__":
    from geometry_msgs.msg import Point
    init_input_names = HeadingNotWithinToleranceGuard.init_input_names()
    init_kwargs = {init_input_names[0]: 0.2} 
    guard:GuardABC = HeadingNotWithinToleranceGuard(**init_kwargs)
    state_input_names = HeadingNotWithinToleranceGuard.state_input_names()
    state_kwargs = {
        state_input_names[0]: ROSAgentState(),
        state_input_names[1]: ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=20.0, y=100.0))) 
    }   
    guard_evaluation: bool = guard.__call__(**state_kwargs)

    print (guard_evaluation)
