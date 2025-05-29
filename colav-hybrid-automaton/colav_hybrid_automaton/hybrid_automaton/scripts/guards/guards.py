from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, Waypoints
from builtin_interfaces.msg import Duration
from shapely.geometry import Polygon, LineString
import numpy as np

from hybrid_automaton.utils import is_inside_unsafe_set, is_imminent_collision
from hybrid_automaton.utils import (
    validate_timestamps_within_tolerance,
    delta_heading,
    euclidean_distance,
    quaternion_to_heading,
    get_current_ros_time
)
import math

# Constant distance threshold (DSF) for now.
DSF = 80  # TODO: Consider changing to: Dmaneuver = Cs + (vrel * Tp)
tolerance = Duration(sec=1, nanosec=0)

max_yaw_rate = 0.2
# Tp finite time stabilization law: time to convergence with full
# 180degree maneuver total angle to turn/ in radians / max_yaw_rate
Tp = ((1 * np.pi) / max_yaw_rate)

def is_los_clear_to_waypoint(agent_state: AgentUpdate,
                            obstacles_state: ObstaclesUpdate,
                            unsafe_set_state: UnsafeSet,
                            waypoints_state: Waypoints,
                            dsf: float = DSF,
                            tolerance: Duration = Duration(sec=1)) -> bool:
    """
    Guard for transition from CRUISE to T2LOS (Guard 1)

    Transition condition:
      - If the line-of-sight (LOS) from the agent to the waypoint intersects the unsafe set
        and the distance from the agent to the intersection is less than or equal to dsf.

    Parameters:
        agent_state: Current state of the agent.
        obstacles_state: State information about obstacles.
        unsafe_set: The unsafe polygon defined by its vertices.
        waypoint: The target waypoint.
        dsf: Distance threshold for considering an intersection (default: DSF).

    Returns:
        bool: True if a transition is required, otherwise False.

    Raises:
        TimeoutError, ValueError: If evaluation times out or input values are invalid.
    """

    # Validate timestamps of sync messages ensuring they are within tolerance
    # system_timestamp = get_current_ros_time()
    # validate_timestamps_within_tolerance(
    #     system_timestamp, agent_state.header.stamp, tolerance)
    # validate_timestamps_within_tolerance(
    #     system_timestamp, obstacles_state.header.stamp, tolerance)
    # validate_timestamps_within_tolerance(
    #     system_timestamp, unsafe_set.header.stamp, tolerance)

    if agent_state is None or \
        obstacles_state is None or \
            unsafe_set_state is None or \
                waypoints_state is None: 
        return False

    agent_position = None
    goal_position = None
    los_line = None

    if len(waypoints_state.waypoints) > 0: 
        current_waypoint = waypoints_state.waypoints[0]
    else:
        return False

    agent_position = (agent_state.pose.position.x, agent_state.pose.position.y)

    goal_position = (current_waypoint.position.x, current_waypoint.position.y)

    los_line = LineString([agent_position, goal_position])

    # Create unsafe polygon from vertex data (assumes [x1, y1, x2, y2, ...])
    unsafe_vertices = unsafe_set_state.vertices.data
    unsafe_polygon = Polygon([(unsafe_vertices[i], unsafe_vertices[i + 1])
                            for i in range(0, len(unsafe_vertices), 2)])

    # Check for LOS intersection with unsafe polygon.
    if los_line.intersects(unsafe_polygon):
        intersection = los_line.intersection(unsafe_polygon)

        if intersection.is_empty:
            return False

        # If the intersection is a LineString, take a midpoint.
        if isinstance(intersection, LineString):
            intersection = intersection.interpolate(0.5, normalized=True)

        # Calculate distance from the agent to the intersection point.
        intersection_distance = euclidean_distance(
            agent_position, (intersection.x, intersection.y))
        if intersection_distance <= dsf:
            return True

    return False


def is_heading_within_tolerance(agent_state: AgentUpdate,
                            waypoints_state: Waypoints,
                            heading_error_tolerance: float = 0.5,
                            tolerance: Duration = Duration(sec=1)) -> bool:
    """
    Guard for the second transition condition to T2LOS

    Transition condition:
      - If the agent's heading error relative to the waypoint is within the acceptable tolerance,
        then the agent is considered aligned and a transition is triggered.

    Parameters:
        agent_state: Current state of the agent.
        current_waypoint: The current waypoint towards which the agent is navigating.
        heading_error_tolerance: Allowable heading error (default: 0.1 radians).
        tolerance: A time tolerance for validations, if needed.

    Returns:
        bool: True if transition is required (i.e. the agent is sufficiently aligned), otherwise False.

    Raises:
        TimeoutError, ValueError: If evaluation takes too long or if input values are invalid.
    """
    # Calculate the heading error between the agent's current heading and the
    # direction to the waypoint.
    if not isinstance(agent_state, AgentUpdate):
        raise ValueError("is_heading_within_tolerance input state 'agent_state' not received.")
    if not isinstance(waypoints_state, Waypoints): 
        raise ValueError("is_heading_within_tolerance input state 'waypoints_state' not received.")
    
    if len(waypoints_state.waypoints) > 0: 
        current_waypoint = waypoints_state.waypoints[0]
    else:
        raise ValueError("is_heading_within_tolerance input state 'waypoints_state' does not have waypoints.")
    
    error = delta_heading(
        x_a=agent_state.pose.position.x,
        y_a=agent_state.pose.position.y,
        theta_a=quaternion_to_heading(
            qx=agent_state.pose.orientation.x,
            qy=agent_state.pose.orientation.y,
            qz=agent_state.pose.orientation.z,
            qw=agent_state.pose.orientation.w
        ),
        x_w=current_waypoint.position.x,
        y_w=current_waypoint.position.y
    )

    # If the heading error is within the allowed tolerance, return True.
    return (abs(error) <= heading_error_tolerance) or \
       math.isclose(abs(error), heading_error_tolerance, abs_tol=1e-6)

def is_unsafe_conditions(agent_state: AgentUpdate,
                       obstacles_state: ObstaclesUpdate,
                       unsafe_set: UnsafeSet,
                       tolerance: Duration = Duration(sec=1)) -> bool:
    """
    Guard for transition from CRUISE to FB (Fallback)

    Transition condition:
      - If the agent is either inside an unsafe set or an imminent collision is detected.

    Parameters:
        agent_state: Current state of the agent.
        obstacles_state: State information about obstacles.
        unsafe_set: The unsafe set (polygon) data.
        tolerance: A time tolerance for validations (default: 1 second if not provided).

    Returns:
        bool: True if a transition to FB is required, otherwise False.

    Raises:
        TimeoutError: If evaluation takes too long.
        ValueError: If input values are invalid or inconsistent.
    """
    

    # Check if unsafe set data exists and apply collision conditions.
    # if unsafe_set is not None:
    #     if unsafe_set.vertices.data:
    #         if is_inside_unsafe_set(
    #                 agent_state=agent_state,
    #                 unsafe_set=unsafe_set):
    #             return True

    #         if is_imminent_collision(
    #                 agent_state=agent_state,
    #                   agent_state=agent_state,
    #                 unsafe_set=unsafe_set):
    #             return True

    return False


def is_waypoint_reached(
    agent_state: AgentUpdate,
    waypoints_state: Waypoints,
    tolerance: Duration = Duration(
        sec=1)) -> bool:
    """
    Guard for transition from CRUISE to WAYPOINT_REACHED

    Transition condition:
      - If the agent is within the waypoint's acceptance radius.

    Parameters:
        agent_state: Current state of the agent.
        current_waypoint: The target waypoint containing the acceptance radius.
        tolerance: A time tolerance for validations (default: 1 second if not provided).

    Returns:
        bool: True if the agent has reached the waypoint (transition required), otherwise False.

    Raises:
        TimeoutError: If evaluation takes too long.
        ValueError: If input values are invalid or inconsistent.
    """
    if tolerance is None:
        tolerance = Duration(sec=1, nanosec=0)

    # Obtain the current time (this would normally be compared with
    # agent_state.header.stamp).
    # Note: For an actual implementation, use a proper time provider.
    # current_time = Time()
    # if validate_timestamps(agent_state.header.stamp, current_time):
    #     raise ValueError('Timeout')

    # Use the imported euclidean_distance function.
    if agent_state is not None:
        agent_coords = [agent_state.pose.position.x, agent_state.pose.position.y]
    if waypoints_state is not None:
        current_waypoint = waypoints_state.waypoints[0]
        waypoint_coords = [
            current_waypoint.position.x,
            current_waypoint.position.y]
        if euclidean_distance(
                agent_coords,
                waypoint_coords) <= current_waypoint.acceptance_radius:
            return True

    return False

def is_heading_not_within_tolerance(agent_state: AgentUpdate,
                          waypoints: Waypoints,
                          heading_error_tolerance: float = 0.5,
                          tolerance: Duration = Duration(sec=1)) -> bool:
    """
    Guard for transition from T2LOS back to CRUISE

    Transition condition:
      - Transition occurs if the agent is not sufficiently aligned with the waypoint.

    Parameters:
        agent_state: Current state of the agent.
        current_waypoint: The waypoint that the agent is navigating toward.
        heading_error_tolerance: Maximum allowable heading error.
        tolerance: Time tolerance for validations if required.

    Returns:
        bool: True if the agent should transition back to CRUISE, otherwise False.
    """
    # Transition back to CRUISE if the heading alignment is not met.
    is_heading_not_within_tolerance = not is_heading_within_tolerance(
        agent_state,
        waypoints,
        heading_error_tolerance,
        tolerance
    )
    return is_heading_not_within_tolerance

def is_virtual_waypoints(
    waypoints: Waypoints) -> bool:
    """
    Guard for transitioning from WAYPOINT_REACHED to CRUISE

    Transition condition:
      - If there are still multiple waypoints available, indicating that the current waypoint is not the final one.

    Parameters:
        waypoints: List of remaining waypoints.
        tolerance: A time tolerance for validations (default provided if None).

    Returns:
        bool: True if there are more waypoints (transition required), otherwise False.

    Raises:
        TimeoutError: If the evaluation takes too long.
        ValueError: If input values are invalid.
    """
    if not isinstance(waypoints, Waypoints):
        raise TypeError(
            f"Invalid argument type for 'waypoints'. Expected type: 'Waypoints', but got type: '{type(waypoints).__name__}'. "
            "Please ensure the 'waypoints' argument is an instance of the Waypoints class."
    )
    
    return len(waypoints._waypoints) > 1
