from .guard import Guard
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
import math
from colav_hybrid_automaton.automaton.utils import (
    delta_heading,
    quaternion_to_heading,
)


class HeadingNotWithinToleranceGuard(Guard):
    """
    A guard condition for a hybrid automaton that evaluates whether the agent's heading 
    is within a specified tolerance of the heading to the current waypoint.

    When called, returns True if the heading error is outside the tolerance.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.heading_tolerance = kwargs.get('heading_tolerance', 0.2)

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
        if self.heading_tolerance >= math.pi:
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
        outside = abs(error) > self.heading_tolerance
        if outside and not math.isclose(abs(error), self.heading_tolerance):
            return True
        return False

    def _validate_initialization(self, **kwargs):

        try:
            try:
                if not isinstance(kwargs['heading_tolerance'], float):
                    raise TypeError('heading tolerance is invalid type')
                if kwargs.get('heading_tolerance') < 0.0:
                    raise ValueError('heading tolerance cannot be less than 0.0')
            except KeyError:
                raise KeyError('heading tolerance not given in __init__')
        except Exception as e:
            raise e

    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)
        
        try:
            try:
                if not isinstance(state_kwargs['agent_state'], ROSAgentState):
                    raise TypeError(f"agent_state data passed in __call__ invalid type")
            except KeyError:
                raise KeyError(f"agent_state value not given in __call__")
            
            try:
                if not isinstance(state_kwargs['waypoints_state'], ROSWaypointsState):
                    raise TypeError(f"waypoints_state data passed in __call__ invalid type")
            except KeyError:
                raise KeyError(f"waypoints_state key not given in __call__")
        except Exception as e: 
            raise e
