from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, Waypoints
from builtin_interfaces.msg import Duration
from shapely.geometry import Polygon, LineString
import numpy as np

from hybrid_automaton.utils.unsafe_set_utils import is_inside_unsafe_set, is_imminent_collision
from hybrid_automaton.utils import (
    validate_timestamps_within_tolerance,
    delta_heading,
    euclidean_distance,
    quaternion_to_heading,
    get_current_ros_time
)


# Constant distance threshold (DSF) for now.
DSF = 80  # TODO: Consider changing to: Dmaneuver = Cs + (vrel * Tp)
tolerance = Duration(sec=1, nanosec=0)

max_yaw_rate = 0.2
# Tp finite time stabilization law: time to convergence with full
# 180degree maneuver total angle to turn/ in radians / max_yaw_rate
Tp = ((1 * np.pi) / max_yaw_rate)

"""1. CRUISE Guard Functions"""


def guard_CRUISE_to_T2LOS_1(agent_state: AgentUpdate,
                            obstacles_state: ObstaclesUpdate,
                            unsafe_set: UnsafeSet,
                            waypoint: Waypoint,
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
    system_timestamp = get_current_ros_time()
    validate_timestamps_within_tolerance(
        system_timestamp, agent_state.header.stamp, tolerance)
    validate_timestamps_within_tolerance(
        system_timestamp, obstacles_state.header.stamp, tolerance)
    validate_timestamps_within_tolerance(
        system_timestamp, unsafe_set.header.stamp, tolerance)

    agent_position = (agent_state.pose.position.x, agent_state.pose.position.y)
    goal_position = (waypoint.position.x, waypoint.position.y)
    los_line = LineString([agent_position, goal_position])

    # Create unsafe polygon from vertex data (assumes [x1, y1, x2, y2, ...])
    unsafe_vertices = unsafe_set.vertices.data
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


def guard_CRUISE_to_T2LOS_2(agent_state: AgentUpdate,
                            current_waypoint: Waypoint,
                            heading_error_tolerance: float = 0.1,
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
    waypoint_heading_error = delta_heading(
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
    return bool(waypoint_heading_error < heading_error_tolerance)


def guard_CRUISE_to_FB(agent_state: AgentUpdate,
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
    if tolerance is None:
        tolerance = Duration(sec=1, nanosec=0)

    # Check if unsafe set data exists and apply collision conditions.
    if unsafe_set.vertices.data:
        if is_inside_unsafe_set(
                agent_state=agent_state,
                unsafe_set=unsafe_set):
            return True

        if is_imminent_collision(
                agent_state=agent_state,
                unsafe_set=unsafe_set):
            return True

    return False


def guard_CRUISE_to_WAYPOINT_REACHED(
    agent_state: AgentUpdate,
    current_waypoint: Waypoint,
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
    agent_coords = [agent_state.pose.position.x, agent_state.pose.position.y]
    waypoint_coords = [
        current_waypoint.position.x,
        current_waypoint.position.y]
    if euclidean_distance(
            agent_coords,
            waypoint_coords) < current_waypoint.acceptance_radius:
        return True

    return False


"""2. T2LOS Guard Functions"""


def guard_T2LOS_to_CRUISE(agent_state: AgentUpdate,
                          current_waypoint: Waypoint,
                          heading_error_tolerance: float,
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
    return not guard_CRUISE_to_T2LOS_2(
        agent_state,
        current_waypoint,
        heading_error_tolerance,
        tolerance)


def guard_T2LOS_to_FB(agent_state: AgentUpdate,
                      obstacles_state: ObstaclesUpdate,
                      unsafe_set: UnsafeSet,
                      tolerance: Duration = Duration(sec=1)) -> bool:
    """
    Guard for transition from T2LOS to FB (Fallback)

    Transition condition:
      - Reuses the CRUISE to FB condition for imminent danger detection.

    Parameters:
        agent_state: Current state of the agent.
        obstacles_state: State information about obstacles.
        unsafe_set: The unsafe polygon data.
        tolerance: A time tolerance for validations (default provided if None).

    Returns:
        bool: True if a transition to fallback is required, otherwise False.
    """
    return guard_CRUISE_to_FB(
        agent_state,
        obstacles_state,
        unsafe_set,
        tolerance)


def guard_T2LOS_to_WAYPOINT_REACHED(
    agent_state: AgentUpdate,
    current_waypoint: Waypoint,
    tolerance: Duration = Duration(
        sec=1)) -> bool:
    """
    Guard for transition from T2LOS to WAYPOINT_REACHED

    Transition conditions:
     - Reuses the CRUISE to WAYPOINT_REACHED condition to check if agent_state is within current_waypoints acceptance radius

    Parameters:
        agent_state (AgentUpdate): Current state of the agent.
        current_waypoint (Waypoint): current waypoint for the hybrid automaton
        tolerance (float): tolerance duration for valid messages.

    Returns:
        bool: True is transition to WAYPOINT_REACHED is required, otherwise False
    """
    return bool(
        guard_CRUISE_to_WAYPOINT_REACHED(
            agent_state=agent_state,
            current_waypoint=current_waypoint,
            tolerance=tolerance))


"""3. FB Guard Functions"""
# Currently no transitions out of the fallback state; therefore, no guards
# are implemented.


"""4. WAYPOINT_REACHED Guard Functions"""


def guard_WAYPOINT_REACHED_to_CRUISE(
    waypoints: Waypoints,
    tolerance: Duration = Duration(
        sec=1)) -> bool:
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
    return len(waypoints._waypoints) > 1
