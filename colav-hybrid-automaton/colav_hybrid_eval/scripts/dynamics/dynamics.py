# This files determines the dynamics of the system/ aka the mode behavior/control policies
# while in each mode.

from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, Waypoint
from colav_interfaces.msg import CRUISEDynamics, T2LOSDynamics, T2ThetaDynamics, WaypointReachedDynamic, FBDynamics
import math
from utils import quaternion_to_heading

TARGET_VELOCITY = 25 * 0.514444  # constant target velocity for now but in the future would like to change this t obe based on agent static dynamic params Convert knots to meters per second (1 knot = 0.514444 m/s)
MAX_ACCELERATION = 1.0 # TODO: Get this value from colav_params/agent_constraints Limit acceleration to (m/s^2)

def dynamics_CRUISE(agent_state: AgentUpdate, dt: float = 0.1) -> CRUISEDynamics:
    """ # TODO: MAYBE SHOULD CHANGE CRUISE INTERFACE TO ONLY RETURN VELOCITY SINCE YAW_RATE IS CONSTANT 0
        These are the dynamics within the cruise mode for each timestep of the hybrid automaton
    """
    current_velocity = agent_state.velocity
    velocity_change = TARGET_VELOCITY - current_velocity
    acceleration = max(min(velocity_change / dt, MAX_ACCELERATION), -MAX_ACCELERATION) # should change -MAX_ACCELERATION to MAX_DECELERATION RETRIEVED FROM AGENT_PARAMS
    new_velocity = current_velocity + acceleration * dt
    # yaw_rate should be set to 0 since we want the vessel to go straight
    yaw_rate = 0

    cruise_dynamics = CRUISEDynamics(
        velocity = new_velocity,
        yaw_rate = yaw_rate
    )
    return cruise_dynamics

def dynamics_T2LOS(agent_state: AgentUpdate, waypoint: Waypoint, dt: float = 0.1, error_tolerance: float = 0.01, proportional_gain: float = 1.0) -> T2LOSDynamics:
    """ Time proportional controller to steer the vessel towards the waypoint. 
        The yaw_rate is adjusted smoothly based on the heading error.
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

def dynamics_T2Theta():
    """this mode dynamics generates a new waypoint based on current environment and returns it"""
    pass

def dynamics_WAYPOINT_REACHED():
    # slow vessel down until yaw_rate and velocity are 0 waypoint reached mode holds until invariant of vessel speed and yaw_rate being greater than 0 holds
    pass

def dynamics_FB():
    pass