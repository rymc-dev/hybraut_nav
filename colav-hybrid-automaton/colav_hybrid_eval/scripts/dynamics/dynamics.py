# This files determines the dynamics of the system/ aka the mode behavior/control policies
# while in each mode.

from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, Waypoint
from colav_interfaces.msg import CruiseDynamics, T2LOSDynamics, WaypointReachedDynamics, FBDynamics
import math
from utils import quaternion_to_heading

TARGET_VELOCITY = 25 * 0.514444  # constant target velocity for now but in the future would like to change this t obe based on agent static dynamic params Convert knots to meters per second (1 knot = 0.514444 m/s)
MAX_ACCELERATION = 1.0 # TODO: Get this value from colav_params/agent_constraints Limit acceleration to (m/s^2)

def dynamics_CRUISE(agent_state: AgentUpdate, dt: float = 0.1) -> CruiseDynamics:
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
    current_velocity = agent_state.velocity
    velocity_change = TARGET_VELOCITY - current_velocity
    acceleration = max(min(velocity_change / dt, MAX_ACCELERATION), -MAX_ACCELERATION)  # TODO: Replace -MAX_ACCELERATION with MAX_DECELERATION from agent parameters
    new_velocity = current_velocity + acceleration * dt

    # In cruise mode, the vessel maintains a straight trajectory (no turning)
    yaw_rate = 0

    cruise_dynamics = CRUISEDynamics(
        velocity=new_velocity,
        yaw_rate=yaw_rate
    )
    return cruise_dynamics

def dynamics_T2LOS(agent_state: AgentUpdate, waypoint: Waypoint, dt: float = 0.1, error_tolerance: float = 0.01, proportional_gain: float = 1.0) -> T2LOSDynamics:
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
    # Current agent heading
    current_heading = quaternion_to_heading(
        qx=agent_state.pose.orientation.x, 
        qy=agent_state.pose.orientation.y, 
        qz=agent_state.pose.orientation.z, 
        qw=agent_state.pose.orientation.w, 
    )

    # Calculate the heading towards the waypoint (assumes 2D position)
    dx = waypoint.position.x - agent_state.pose.position.x
    dy = waypoint.position.y - agent_state.pose.position.y
    desired_heading = math.atan2(dy, dx)  # Desired heading to the waypoint

    # Calculate heading error (difference between current heading and desired heading)
    heading_error = desired_heading - current_heading

    # Normalize the error to the range [-pi, pi]
    if heading_error > math.pi:
        heading_error -= 2 * math.pi
    elif heading_error < -math.pi:
        heading_error += 2 * math.pi

    # If the heading error is smaller than the tolerance, stop adjusting
    if abs(heading_error) < error_tolerance:
        yaw_rate = 0
    else:
        # Time proportional controller for yaw rate
        yaw_rate = proportional_gain * heading_error / dt

    # Keep the velocity unchanged since we're just controlling the heading
    new_velocity = agent_state.velocity
    t2los_dynamics = T2LOSDynamics(
        velocity=new_velocity,
        yaw_rate=yaw_rate
    )
    
    return t2los_dynamics

def dynamics_WAYPOINT_REACHED():
    # slow vessel down until yaw_rate and velocity are 0 waypoint reached mode holds until invariant of vessel speed and yaw_rate being greater than 0 holds
    pass

def dynamics_FB():
    pass