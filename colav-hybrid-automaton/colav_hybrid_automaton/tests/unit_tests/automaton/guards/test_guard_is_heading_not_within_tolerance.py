from colav_hybrid_automaton.automaton.guards import HeadingNotWithinToleranceGuard
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from geometry_msgs.msg import Pose, Point, Quaternion
import pytest
import math


def quaternion_from_euler(roll, pitch, yaw):
    """Helper function to create quaternion from euler angles."""
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    
    return Quaternion(x=x, y=y, z=z, w=w)


@pytest.mark.parametrize(
    "heading_tolerance, agent_x, agent_y, agent_yaw, waypoint_x, waypoint_y, expected_guard_evaluation, test_description",
    [
        # Agent pointing directly at waypoint (within tolerance)
        (0.2, 0.0, 0.0, 0.0, 1.0, 0.0, False, "agent_pointing_directly_at_waypoint_east"),
        (0.2, 0.0, 0.0, math.pi/2, 0.0, 1.0, False, "agent_pointing_directly_at_waypoint_north"),
        (0.2, 0.0, 0.0, math.pi, -1.0, 0.0, False, "agent_pointing_directly_at_waypoint_west"),
        (0.2, 0.0, 0.0, -math.pi/2, 0.0, -1.0, False, "agent_pointing_directly_at_waypoint_south"),
        
        # Agent pointing within tolerance of waypoint
        (0.2, 0.0, 0.0, 0.1, 1.0, 0.0, False, "agent_within_tolerance_small_deviation"),
        (0.2, 0.0, 0.0, -0.1, 1.0, 0.0, False, "agent_within_tolerance_negative_deviation"),
        (0.2, 0.0, 0.0, 0.2, 1.0, 0.0, False, "agent_exactly_at_tolerance_boundary"),
        (0.2, 0.0, 0.0, -0.2, 1.0, 0.0, False, "agent_exactly_at_negative_tolerance_boundary"),
        
        # Agent pointing outside tolerance (should return True)
        (0.2, 0.0, 0.0, 0.25, 1.0, 0.0, True, "agent_slightly_outside_tolerance"),
        (0.2, 0.0, 0.0, -0.25, 1.0, 0.0, True, "agent_slightly_outside_negative_tolerance"),
        (0.2, 0.0, 0.0, 0.5, 1.0, 0.0, True, "agent_well_outside_tolerance"),
        (0.2, 0.0, 0.0, math.pi, 1.0, 0.0, True, "agent_pointing_opposite_direction"),
        
        # Zero tolerance cases
        (0.0, 0.0, 0.0, 0.0, 1.0, 0.0, False, "zero_tolerance_perfect_alignment"),
        (0.0, 0.0, 0.0, 0.001, 1.0, 0.0, True, "zero_tolerance_tiny_deviation"),
        
        # Very small tolerance
        (1e-6, 0.0, 0.0, 0.0, 1.0, 0.0, False, "tiny_tolerance_perfect_alignment"),
        (1e-6, 0.0, 0.0, 1e-7, 1.0, 0.0, False, "tiny_tolerance_within_bounds"),
        (1e-6, 0.0, 0.0, 1e-5, 1.0, 0.0, True, "tiny_tolerance_outside_bounds"),
        
        # Large tolerance
        (math.pi, 0.0, 0.0, 0.0, 1.0, 0.0, False, "large_tolerance_perfect_alignment"),
        (math.pi, 0.0, 0.0, math.pi - 0.1, 1.0, 0.0, False, "large_tolerance_almost_opposite"),
        (math.pi, 0.0, 0.0, math.pi + 0.1, 1.0, 0.0, True, "large_tolerance_beyond_opposite"),
        
        # Diagonal waypoints (45-degree angles)
        (0.2, 0.0, 0.0, math.pi/4, 1.0, 1.0, False, "diagonal_northeast_perfect_alignment"),
        (0.2, 0.0, 0.0, math.pi/4 + 0.1, 1.0, 1.0, False, "diagonal_northeast_within_tolerance"),
        (0.2, 0.0, 0.0, math.pi/4 + 0.3, 1.0, 1.0, True, "diagonal_northeast_outside_tolerance"),
        (0.2, 0.0, 0.0, -3*math.pi/4, -1.0, -1.0, False, "diagonal_southwest_perfect_alignment"),
        
        # Wraparound cases near ±π
        (0.2, 0.0, 0.0, math.pi - 0.1, -1.0, 0.0, False, "near_negative_pi_within_tolerance"),
        (0.2, 0.0, 0.0, -math.pi + 0.1, -1.0, 0.0, False, "near_positive_pi_within_tolerance"),
        (0.2, 0.0, 0.0, math.pi - 0.3, -1.0, 0.0, True, "near_negative_pi_outside_tolerance"),
        
        # Agent at different positions
        (0.2, 5.0, 3.0, 0.0, 6.0, 3.0, False, "agent_at_different_position_aligned_east"),
        (0.2, 5.0, 3.0, math.pi/2, 5.0, 4.0, False, "agent_at_different_position_aligned_north"),
        (0.2, 5.0, 3.0, math.pi/4, 6.0, 4.0, False, "agent_at_different_position_aligned_northeast"),
        (0.2, 5.0, 3.0, 0.0, 5.0, 4.0, True, "agent_at_different_position_misaligned"),
        
        # Edge case: waypoint at same position as agent
        (0.2, 0.0, 0.0, 0.0, 0.0, 0.0, False, "waypoint_at_agent_position"),
        (0.2, 5.0, 3.0, math.pi/4, 5.0, 3.0, False, "waypoint_at_agent_position_different_location"),
        
        # Very close waypoints (testing numerical precision)
        (0.2, 0.0, 0.0, 0.0, 1e-10, 0.0, False, "very_close_waypoint_east"),
        (0.2, 0.0, 0.0, math.pi/2, 0.0, 1e-10, False, "very_close_waypoint_north"),
        (0.2, 0.0, 0.0, math.pi/4, 1e-10, 1e-10, False, "very_close_waypoint_northeast"),
        
        # Negative coordinates
        (0.2, -1.0, -1.0, math.pi/4, 0.0, 0.0, False, "negative_agent_position_to_origin"),
        (0.2, 0.0, 0.0, -3*math.pi/4, -1.0, -1.0, False, "origin_to_negative_waypoint"),
        (0.2, -2.0, -1.0, 0.0, -1.0, -1.0, False, "negative_coordinates_aligned_east"),
        
        # Large distance waypoints
        (0.2, 0.0, 0.0, 0.0, 1000.0, 0.0, False, "large_distance_waypoint_aligned"),
        (0.2, 0.0, 0.0, 0.1, 1000.0, 0.0, False, "large_distance_waypoint_slight_misalignment"),
        (0.2, 0.0, 0.0, 0.3, 1000.0, 0.0, True, "large_distance_waypoint_outside_tolerance"),
        
        # Common tolerance values with practical scenarios
        (math.pi/18, 0.0, 0.0, 0.0, 1.0, 0.0, False, "10_degree_tolerance_perfect_alignment"),  # 10 degrees
        (math.pi/18, 0.0, 0.0, math.pi/18, 1.0, 0.0, False, "10_degree_tolerance_at_boundary"),
        (math.pi/18, 0.0, 0.0, math.pi/18 + 0.01, 1.0, 0.0, True, "10_degree_tolerance_just_outside"),
        (math.pi/36, 0.0, 0.0, math.pi/36, 1.0, 0.0, False, "5_degree_tolerance_at_boundary"),   # 5 degrees
        (math.pi/180, 0.0, 0.0, math.pi/180, 1.0, 0.0, False, "1_degree_tolerance_at_boundary"), # 1 degree
        
        # Floating point precision edge cases
        (0.1, 0.0, 0.0, 0.1000000000000001, 1.0, 0.0, False, "floating_point_precision_within"),
        (1e-15, 0.0, 0.0, 1e-16, 1.0, 0.0, False, "machine_epsilon_level_difference"),
        (1e-15, 0.0, 0.0, 1e-14, 1.0, 0.0, True, "beyond_machine_epsilon_difference"),
    ]
)
def test_heading_not_within_tolerance_guard_comprehensive(
    heading_tolerance: float,
    agent_x: float,
    agent_y: float,
    agent_yaw: float,
    waypoint_x: float,
    waypoint_y: float,
    expected_guard_evaluation: bool,
    test_description: str
):
    """Comprehensive test for HeadingNotWithinToleranceGuard with boundary conditions.
    
    Args:
        heading_tolerance (float): The heading tolerance value.
        agent_x, agent_y (float): Agent position coordinates.
        agent_yaw (float): The agent's yaw angle in radians.
        waypoint_x, waypoint_y (float): Waypoint position coordinates.
        expected_guard_evaluation (bool): Expected result of guard evaluation.
        test_description (str): Description of the test case.
    """
    # Create agent state
    agent_state = ROSAgentState(
        pose=Pose(
            position=Point(x=agent_x, y=agent_y, z=0.0),
            orientation=quaternion_from_euler(0.0, 0.0, agent_yaw)
        )
    )
    
    # Create current waypoint (this is what your guard expects)
    current_waypoint = ROSWaypoint(
        position=Point(x=waypoint_x, y=waypoint_y, z=0.0)
    )
    
    # Create waypoint state with current_waypoint attribute
    waypoints_state = ROSWaypointsState(
        current_waypoint=current_waypoint
    )
    
    # Test guard creation and evaluation
    init_kwargs = {"heading_tolerance": heading_tolerance}
    guard = HeadingNotWithinToleranceGuard(**init_kwargs)
    
    assert guard.__str__() == 'Guard Function: HeadingNotWithinToleranceGuard'
    assert guard.__repr__() == "HeadingNotWithinToleranceGuard(initialized=True)"
    
    state_kwargs = {
        'agent_state': agent_state,
        'waypoints_state': waypoints_state
    }
    
    actual_guard_evaluation = guard.__call__(**state_kwargs)
    assert actual_guard_evaluation == expected_guard_evaluation, \
        f"Test case '{test_description}' failed: expected {expected_guard_evaluation}, got {actual_guard_evaluation}"