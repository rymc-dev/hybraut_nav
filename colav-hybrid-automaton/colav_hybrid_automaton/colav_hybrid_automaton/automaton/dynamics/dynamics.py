# This files determines the dynamics of the system/ aka the mode behavior/control policies
# while in each mode.

from colav_interfaces.msg import AgentUpdate, Waypoints
from hybrid_automaton_interfaces.msg import DynamicParameter
import math
from colav_hybrid_automaton.automaton.utils import quaternion_to_heading, get_current_ros_time, is_timestamps_within_tolerance
from builtin_interfaces.msg import Duration

# constant target velocity for now but in the future would like to change
# this t obe based on agent static dynamic params Convert knots to meters
# per second (1 knot = 0.514444 m/s)
TARGET_VELOCITY = 30 * 0.514444
# TODO: Get this value from colav_params/agent_constraints Limit
# acceleration to (m/s^2)
MAX_ACCELERATION = 1.0
MAX_DECELERATION = 0.5
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

    # current_velocity = agent_state.velocity
    # velocity_change = TARGET_VELOCITY - current_velocity
    # # TODO: Replace -MAX_ACCELERATION with MAX_DECELERATION from agent
    # # parameters
    # acceleration = max(
    #     min(velocity_change / dt, MAX_ACCELERATION), -MAX_ACCELERATION)
    # new_velocity = current_velocity + acceleration * dt

    new_velocity = TARGET_VELOCITY
    return [new_velocity, 0.0]


def proportional_yaw_rate_controller(
        agent_state: AgentUpdate,
        waypoints: Waypoints,
        dt: float = 0.1,
        error_tolerance: float = 0.01,
        proportional_gain: float = 3.0,
        max_yaw_rate: float = 0.5,
        tolerance: Duration = Duration(sec=1, nanosec=0)
) -> Tuple[float, float]:
    """
    Hybrid controller: simultaneously throttle velocity toward TARGET_VELOCITY
    and adjust yaw rate to steer toward the next waypoint.
    """

    # Input validation
    if not isinstance(agent_state, AgentUpdate):
        raise ValueError("agent_state must be AgentUpdate")
    if not isinstance(waypoints, Waypoints):
        raise ValueError("waypoints must be Waypoints")
    if not isinstance(dt, float) or dt < 0.01:
        raise ValueError("dt must be float >= 0.01")
    if not isinstance(error_tolerance, float) or error_tolerance < 0.001:
        raise ValueError("error_tolerance must be float >= 0.001")
    if not isinstance(proportional_gain, float) or proportional_gain <= 0 or proportional_gain > 10:
        raise ValueError("proportional_gain must be > 0 and <= 10")
    if not isinstance(max_yaw_rate, float) or max_yaw_rate <= 0:
        raise ValueError("max_yaw_rate must be float > 0")
    if not isinstance(tolerance, Duration):
        raise ValueError("tolerance must be Duration type")

    # Velocity control (P-controller)
    # current_vel = agent_state.velocity
    # vel_error = TARGET_VELOCITY - current_vel
    # accel_cmd = max(min(vel_error / dt, MAX_ACCELERATION), -MAX_DECELERATION)
    # updated_velocity = current_vel + accel_cmd * dt

    # Yaw control
    current_heading = quaternion_to_heading(
        qx=agent_state.pose.orientation.x,
        qy=agent_state.pose.orientation.y,
        qz=agent_state.pose.orientation.z,
        qw=agent_state.pose.orientation.w,
    )

    # Next waypoint
    try:
        wp = waypoints.waypoints[0]
    except IndexError:
        raise ValueError("No waypoint to navigate to")

    dx = wp.position.x - agent_state.pose.position.x
    dy = wp.position.y - agent_state.pose.position.y
    desired_heading = math.atan2(dy, dx)

    # Properly wrapped heading error [-pi, pi]
    heading_error = math.atan2(
        math.sin(desired_heading - current_heading),
        math.cos(desired_heading - current_heading)
    )

    # Proportional yaw control with smoothing
    if abs(heading_error) < error_tolerance:
        target_yaw_rate = 0.0
    else:
        raw_turn = proportional_gain * heading_error / dt
        target_yaw_rate = max(-max_yaw_rate, min(raw_turn, max_yaw_rate))

        # Optional low-pass filter to smooth yaw rate
        alpha = 0.1
        target_yaw_rate = alpha * target_yaw_rate + (1 - alpha) * agent_state.yaw_rate

    # return float(TARGET_VELOCITY), target_yaw_rate
    # Binary controller
    # if abs(heading_error) < error_tolerance:
    #     target_yaw_rate = 0.0
    # elif heading_error > 0:
    #     target_yaw_rate = max_yaw_rate  # turn left
    # else:
    #     target_yaw_rate = -max_yaw_rate  # turn right

    # return float(TARGET_VELOCITY), target_yaw_rate

def no_op_controller() -> Tuple[float, float]:
    # Initially controller for fallback will return 0,0 commands therefore
    # enabling the controller on ATL vessel to ramp down by itself

    return [0.0, 0.0]
