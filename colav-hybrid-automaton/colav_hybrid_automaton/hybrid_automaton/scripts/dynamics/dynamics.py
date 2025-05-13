# This files determines the dynamics of the system/ aka the mode behavior/control policies
# while in each mode.

from colav_interfaces.msg import AgentUpdate, Waypoints
from hybrid_automaton_interfaces.msg import DynamicParameter
import math
from hybrid_automaton.utils import quaternion_to_heading
from hybrid_automaton.utils import get_current_ros_time, validate_timestamps_within_tolerance
from builtin_interfaces.msg import Duration

# constant target velocity for now but in the future would like to change
# this t obe based on agent static dynamic params Convert knots to meters
# per second (1 knot = 0.514444 m/s)
TARGET_VELOCITY = 30 * 0.514444
# TODO: Get this value from colav_params/agent_constraints Limit
# acceleration to (m/s^2)
MAX_ACCELERATION = 1.0
from typing import Tuple


def proportional_velocity_controller(agent_state: AgentUpdate, dt: float = 0.1, tolerance: Duration = Duration(sec=1, nanosec=0)) -> Tuple[float, float]:
    """
    Computes the dynamics for the CRUISE control mode of the agent.

    In this mode, a proportional velocity controller is used to adjust the agent's speed
    toward a predefined TARGET_VELOCITY. The controller computes the required acceleration
    based on the velocity error and clamps it within the maximum allowable acceleration
    and deceleration limits, ensuring that the agent adheres to its dynamic constraints.

    During CRUISE mode, the yaw rate is fixed to zero, assuming that the agent is moving
    along a straight line (e.g., line-of-sight path following).

    Parameters:
        agent_state (AgentUpdate): The current state of the agent.
        dt (float): Time step for the update (default is 0.1 seconds).

    Returns:
        CRUISEDynamics: Updated velocity and yaw rate for the next time step.

    Raises:
        ValueError: (Not currently raised, placeholder for future use if needed.)
    """
    if not isinstance(agent_state, AgentUpdate):
        raise ValueError("agent state received is of none type not type AgentUpdate")

    if not isinstance(dt, float):
        raise ValueError("delta time must be type float")
    if dt < 0.01:
        raise ValueError("delta time must be greater than or equal to 0.01")
    if not isinstance(tolerance, Duration):
        raise ValueError('tolerance must be Duration type')
    
    # NOTE: GETTING RID OF THIS FOR TESTING
    # try:
    #     validate_timestamps_within_tolerance(
    #         agent_state.header.stamp,
    #         get_current_ros_time(),
    #         tolerance
    #     )
    # except TimeoutError:
    #     raise TimeoutError("timeout occurred in dynamics cruise")
    # except Exception as e:
    #     raise

    current_velocity = agent_state.velocity
    velocity_change = TARGET_VELOCITY - current_velocity
    # TODO: Replace -MAX_ACCELERATION with MAX_DECELERATION from agent
    # parameters
    acceleration = max(
        min(velocity_change / dt, MAX_ACCELERATION), -MAX_ACCELERATION)
    new_velocity = current_velocity + acceleration * dt

    return [new_velocity, 0.0]


def proportional_yaw_rate_controller(
        agent_state: AgentUpdate,
        waypoints: Waypoints,
        dt: float = 0.1,
        error_tolerance: float = 0.01,
        proportional_gain: float = 1.0,
        max_yaw_rate: float = 0.5,
        tolerance: Duration = Duration(sec=1, nanosec=0)) -> Tuple[float, float]:
    # TODO: Need to implmenet this as a continuous proporitional controller P-control with a low-pass filter on the rudder
    """
    Computes the dynamics of the COLAV Hybrid Automaton T2LOS control mode

    In this mode, a time-propotional P-controller for heading correction is implemented utilizing
    the waypoint arg passed in as the target bearing. Invariant for this function is while yaw_rate is greater
    than 0 and guard condition for leaving to cruise is when we are within within a bearing tolerance of the waypoint

    Parameter:
        agent_state (AgentUpdate): The current state of the agent
        waypoint (Waypoint): The current waypoint
        dt (float): Time step for the update (default is 0.1 seconds)

    Returns:
         T2LOSDynamics: updated velocity/yaw_rate for agent vessel

    Raises:
        ValueError: (TODO: Not currently set.)
    """
    if not isinstance(agent_state, AgentUpdate):
        raise ValueError("agent state received is of none type not type AgentUpdate")
    
    if not isinstance(waypoints, Waypoints):
        raise ValueError("waypoints not an instance of Waypoints")

    if not isinstance(dt, float):
        raise ValueError("delta time must be type float")
    if dt < 0.01:
        raise ValueError("delta time must be greater than or equal to 0.01")
    
    if not isinstance(error_tolerance, float):
        raise ValueError('Heading error tolerance invalid, should be type float')

    if error_tolerance < 0.001:
        raise ValueError('Heading error tolerance invalid, should be greater than or equal to 0.001')

    if not isinstance(proportional_gain, float):
        raise ValueError("proportional gain must be type float")
    
    if proportional_gain <= 0.0 or proportional_gain > 10:
        raise ValueError('proportional gain must be greater than 0 and less than 10')

    if not isinstance(tolerance, Duration):
        raise ValueError('tolerance must be Duration type')

    # NOTE: GETTING RID OF THIS FOR TESTING
    # try:
    #     validate_timestamps_within_tolerance(
    #         agent_state.header.stamp,
    #         get_current_ros_time(),
    #         tolerance
    #     )
    # except TimeoutError:
    #     raise TimeoutError("timeout occurred in dynamics cruise")
    # except Exception as e:
    #     raise

    # Current agent heading
    current_heading = quaternion_to_heading(
        qx=agent_state.pose.orientation.x,
        qy=agent_state.pose.orientation.y,
        qz=agent_state.pose.orientation.z,
        qw=agent_state.pose.orientation.w,
    )

    try:
        current_waypoint = waypoints.waypoints[0]
    except Exception: 
        raise ValueError('invalid waypoints received for this controller, There is no current waypoint for us to navigate to.')
    # Calculate the heading towards the waypoint (assumes 2D position)
    dx = current_waypoint.position.x - agent_state.pose.position.x
    dy = current_waypoint.position.y - agent_state.pose.position.y
    desired_heading = math.atan2(dy, dx)  # Desired heading to the waypoint

    # Calculate heading error (difference between current heading and desired
    # heading)
    heading_error = desired_heading - current_heading
    heading_error = (heading_error + math.pi) % (2 * math.pi) - math.pi
    # Normalize the error to the range [-pi, pi]
    if heading_error > math.pi:
        heading_error -= 2 * math.pi
    elif heading_error < -math.pi:
        heading_error += 2 * math.pi

    # If the heading error is smaller than the tolerance, stop adjusting
    if abs(heading_error) < error_tolerance:
        yaw_rate = 0
    else:
        # Raw P-controller output
        raw_yaw_rate = proportional_gain * heading_error / dt
        # Clamp it
        yaw_rate = max(-max_yaw_rate, min(raw_yaw_rate, max_yaw_rate))
        alpha = 0.1  # smoothing factor between 0 (slow) and 1 (fast)
        yaw_rate = alpha * yaw_rate + (1 - alpha) * agent_state.yaw_rate

    return [float(agent_state.velocity), float(yaw_rate)]


def no_op_controller() -> Tuple[float, float]:
    # Initially controller for fallback will return 0,0 commands therefore
    # enabling the controller on ATL vessel to ramp down by itself

    return [0.0, 0.0]
