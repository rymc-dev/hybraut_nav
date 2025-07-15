"""
Test file for HeadingNotWithinToleranceGuard with in an implementation of GuardABC 
for COLAV Hybrid Automaton
"""

import pytest
import math
from geometry_msgs.msg import Pose, Point, Quaternion
from automaton.guards import HeadingNotWithinToleranceGuard, GuardABC
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)


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

@pytest.fixture
def guard_instance():
    return HeadingNotWithinToleranceGuard(heading_tolerance=0.2)

class TestHeadingNotWithinToleranceGuard:
    """Test suite for HeadingNotWithinTolerance Guard"""

    def test_initialization_and_specs(self, guard_instance: GuardABC):
        """test the initialization and specifications of the class instance are valid"""
        assert guard_instance.init_input_spec_names() == ['heading_tolerance']
        assert guard_instance.init_input_spec_types() == [float]
        assert guard_instance.state_input_spec_names() == ['agent_state', 'waypoints_state']
        assert guard_instance.state_input_spec_types() == [ROSAgentState, ROSWaypointsState] 

    def test_string_representations(self, guard_instance: GuardABC):
        """test the string representations of the guard instance"""
        assert repr(guard_instance) == 'HeadingNotWithinToleranceGuard(initialized=True)'
        assert str(guard_instance) == 'Guard Function: HeadingNotWithinToleranceGuard'

    @pytest.mark.parametrize(
        "heading_tolerance, agent_x, agent_y, agent_yaw, waypoint_x, waypoint_y, expected_guard_evaluation",
        [
            # Agent pointing directly at waypoint (within tolerance)
            (0.2, 0.0, 0.0, 0.0, 1.0, 0.0, False),
            (0.2, 0.0, 0.0, math.pi/2, 0.0, 1.0, False),
            (0.2, 0.0, 0.0, math.pi, -1.0, 0.0, False),
            (0.2, 0.0, 0.0, -math.pi/2, 0.0, -1.0, False),
            
            # Agent pointing within tolerance of waypoint
            (0.2, 0.0, 0.0, 0.1, 1.0, 0.0, False),
            (0.2, 0.0, 0.0, -0.1, 1.0, 0.0, False),
            (0.2, 0.0, 0.0, 0.2, 1.0, 0.0, False),
            (0.2, 0.0, 0.0, -0.2, 1.0, 0.0, False),
            
            # Agent pointing outside tolerance (should return True)
            (0.2, 0.0, 0.0, 0.25, 1.0, 0.0, True),
            (0.2, 0.0, 0.0, -0.25, 1.0, 0.0, True),
            (0.2, 0.0, 0.0, 0.5, 1.0, 0.0, True),
            (0.2, 0.0, 0.0, math.pi, 1.0, 0.0, True),
            
            # Zero tolerance cases
            (0.0, 0.0, 0.0, 0.0, 1.0, 0.0, False),
            (0.0, 0.0, 0.0, 0.001, 1.0, 0.0, True),
            
            # Very small tolerance
            (1e-6, 0.0, 0.0, 0.0, 1.0, 0.0, False),
            (1e-6, 0.0, 0.0, 1e-7, 1.0, 0.0, False),
            (1e-6, 0.0, 0.0, 1e-5, 1.0, 0.0, True),
            
            # Large tolerance
            (math.pi, 0.0, 0.0, 0.0, 1.0, 0.0, False),
            (math.pi, 0.0, 0.0, math.pi - 0.1, 1.0, 0.0, False),
            (math.pi, 0.0, 0.0, math.pi + 0.1, 1.0, 0.0, True),
            
            # Diagonal waypoints (45-degree angles)
            (0.2, 0.0, 0.0, math.pi/4, 1.0, 1.0, False),
            (0.2, 0.0, 0.0, math.pi/4 + 0.1, 1.0, 1.0, False),
            (0.2, 0.0, 0.0, math.pi/4 + 0.3, 1.0, 1.0, True),
            (0.2, 0.0, 0.0, -3*math.pi/4, -1.0, -1.0, False),
            
            # Wraparound cases near ±π
            (0.2, 0.0, 0.0, math.pi - 0.1, -1.0, 0.0, False),
            (0.2, 0.0, 0.0, -math.pi + 0.1, -1.0, 0.0, False),
            (0.2, 0.0, 0.0, math.pi - 0.3, -1.0, 0.0, True),
            
            # Agent at different positions
            (0.2, 5.0, 3.0, 0.0, 6.0, 3.0, False),
            (0.2, 5.0, 3.0, math.pi/2, 5.0, 4.0, False),
            (0.2, 5.0, 3.0, math.pi/4, 6.0, 4.0, False),
            (0.2, 5.0, 3.0, 0.0, 5.0, 4.0, True),
            
            # Edge case: waypoint at same position as agent
            (0.2, 0.0, 0.0, 0.0, 0.0, 0.0, False),
            (0.2, 5.0, 3.0, math.pi/4, 5.0, 3.0, False),
            
            # Very close waypoints (testing numerical precision)
            (0.2, 0.0, 0.0, 0.0, 1e-10, 0.0, False),
            (0.2, 0.0, 0.0, math.pi/2, 0.0, 1e-10, False),
            (0.2, 0.0, 0.0, math.pi/4, 1e-10, 1e-10, False),
            
            # Negative coordinates
            (0.2, -1.0, -1.0, math.pi/4, 0.0, 0.0, False),
            (0.2, 0.0, 0.0, -3*math.pi/4, -1.0, -1.0, False),
            (0.2, -2.0, -1.0, 0.0, -1.0, -1.0, False),
            
            # Large distance waypoints
            (0.2, 0.0, 0.0, 0.0, 1000.0, 0.0, False),
            (0.2, 0.0, 0.0, 0.1, 1000.0, 0.0, False),
            (0.2, 0.0, 0.0, 0.3, 1000.0, 0.0, True),

            # Common tolerance values with practical scenarios
            (math.pi/18, 0.0, 0.0, 0.0, 1.0, 0.0, False),  # 10 degrees
            (math.pi/18, 0.0, 0.0, math.pi/18, 1.0, 0.0, False),
            (math.pi/18, 0.0, 0.0, math.pi/18 + 0.01, 1.0, 0.0, True),
            (math.pi/36, 0.0, 0.0, math.pi/36, 1.0, 0.0, False),   # 5 degrees
            (math.pi/180, 0.0, 0.0, math.pi/180, 1.0, 0.0, False), # 1 degree
            
            # Floating point precision edge cases
            (0.1, 0.0, 0.0, 0.1000000000000001, 1.0, 0.0, False),
            (1e-15, 0.0, 0.0, 1e-16, 1.0, 0.0, False),
            (1e-15, 0.0, 0.0, 1e-14, 1.0, 0.0, True),
        ],
        ids=[
            "agent_pointing_directly_at_waypoint_east",
            "agent_pointing_directly_at_waypoint_north",
            "agent_pointing_directly_at_waypoint_west",
            "agent_pointing_directly_at_waypoint_south",
            "agent_within_tolerance_small_deviation",
            "agent_within_tolerance_negative_deviation",
            "agent_exactly_at_tolerance_boundary",
            "agent_exactly_at_negative_tolerance_boundary",
            "agent_slightly_outside_tolerance",
            "agent_slightly_outside_negative_tolerance",
            "agent_well_outside_tolerance",
            "agent_pointing_opposite_direction",
            "zero_tolerance_perfect_alignment",
            "zero_tolerance_tiny_deviation",
            "tiny_tolerance_perfect_alignment",
            "tiny_tolerance_within_bounds",
            "tiny_tolerance_outside_bounds",
            "large_tolerance_perfect_alignment",
            "large_tolerance_almost_opposite",
            "large_tolerance_beyond_opposite",
            "diagonal_northeast_perfect_alignment",
            "diagonal_northeast_within_tolerance",
            "diagonal_northeast_outside_tolerance",
            "diagonal_southwest_perfect_alignment",
            "near_negative_pi_within_tolerance",
            "near_positive_pi_within_tolerance",
            "near_negative_pi_outside_tolerance",
            "agent_at_different_position_aligned_east",
            "agent_at_different_position_aligned_north",
            "agent_at_different_position_aligned_northeast",
            "agent_at_different_position_misaligned",
            "waypoint_at_agent_position",
            "waypoint_at_agent_position_different_location",
            "very_close_waypoint_east",
            "very_close_waypoint_north",
            "very_close_waypoint_northeast",
            "negative_agent_position_to_origin",
            "origin_to_negative_waypoint",
            "negative_coordinates_aligned_east",
            "large_distance_waypoint_aligned",
            "large_distance_waypoint_slight_misalignment",
            "large_distance_waypoint_outside_tolerance",
            "10_degree_tolerance_perfect_alignment",
            "10_degree_tolerance_at_boundary",
            "10_degree_tolerance_just_outside",
            "5_degree_tolerance_at_boundary",
            "1_degree_tolerance_at_boundary",
            "floating_point_precision_within",
            "machine_epsilon_level_difference",
            "beyond_machine_epsilon_difference",

        ]
    )
    def test_heading_not_within_tolerance_guard_comprehensive(
        self,
        heading_tolerance: float,
        agent_x: float,
        agent_y: float,
        agent_yaw: float,
        waypoint_x: float,
        waypoint_y: float,
        expected_guard_evaluation: bool,
        request
    ):
        """Comprehensive test for HeadingNotWithinToleranceGuard with boundary conditions.
        
        Args:
            heading_tolerance (float): The heading tolerance value.
            agent_x, agent_y (float): Agent position coordinates.
            agent_yaw (float): The agent's yaw angle in radians.
            waypoint_x, waypoint_y (float): Waypoint position coordinates.
            expected_guard_evaluation (bool): Expected result of guard evaluation.
            request
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
            f"Test case '{request.node.callspec.id}' failed: expected {expected_guard_evaluation}, got {actual_guard_evaluation}"

    @pytest.mark.parametrize(
        "init_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'heading_tolerance': int(1)}, TypeError),
            ({'heading_tolerance': -0.1}, ValueError)
        ],
        ids=[
            'heading error tolerance arg not given -> pytest.raise(KeyError)',
            'heading error tolerance not float datatype -> pytest.raise(TypeError)',
            'heading error tolerance has invalid negative valued -> pytest.raise(ValueError)'
        ]
    )
    def test_invalid_initialization(self, init_kwargs, expected_exception):
        """test invalid intiialization args"""
        with pytest.raises(expected_exception): 
            HeadingNotWithinToleranceGuard(**init_kwargs)

    @pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            ({}, KeyError),            
            ({'waypoints_state': ROSWaypointsState()}, KeyError),            
            ({'agent_state': ROSAgentState()}, KeyError),
            ({'agent_state': "wrong_type", 'waypoints_state': ROSWaypointsState()}, TypeError),
            ({'agent_state': ROSAgentState(), 'waypoints_state': "wrong_type"}, TypeError),
            ({'agent_state': 123, 'waypoints_state': 456}, TypeError),
            ({'agent_state': None, 'waypoints_state': ROSWaypointsState()}, TypeError),
            ({'agent_state': ROSAgentState(), 'waypoints_state': None}, TypeError),
        ],
        ids=[
            'no state inputs given -> KeyError("agent_state value not given in **call**")',
            'agent_state missing -> KeyError("agent_state value not given in **call**")',
            'waypoints_state missing -> KeyError("waypoints_state key not given in **call**")',
            'agent_state wrong type -> TypeError("agent_state data passed in **call** invalid type")',
            'waypoints_state wrong type -> TypeError("waypoints_state data passed in **call** invalid type")',
            'both states wrong type -> TypeError("agent_state data passed in **call** invalid type")',
            'agent_state is None -> TypeError("agent_state data passed in **call** invalid type")',
            'waypoints_state is None -> TypeError("waypoints_state data passed in **call** invalid type")'
        ]
    )
    def test_invalid_state_inputs(self,state_kwargs, expected_exception):
        """
        Tests invalid state inputs when __call__ is utilized
        """
        guard = HeadingNotWithinToleranceGuard(heading_tolerance=0.2)

        with pytest.raises(expected_exception):
            guard.__call__(**state_kwargs)  # Note: should be **state_kwargs, not *state_kwargs

if __name__ == '__main__':
    pytest.main([__file__])