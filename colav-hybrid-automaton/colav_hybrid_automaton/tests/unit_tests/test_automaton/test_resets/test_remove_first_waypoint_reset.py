"""
Tests for RemoveFirstWaypoint reset class.

This module contains comprehensive tests for the RemoveFirstWaypoint reset function,
including initialization, validation, and execution tests.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Import the classes under test
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint
from colav_hybrid_automaton.automaton.resets.resets import RemoveFirstWaypoint  # Replace with actual import path


class TestRemoveFirstWaypoint:
    """Test suite for RemoveFirstWaypoint reset class."""

    @pytest.fixture
    def mock_waypoint(self):
        """Create a mock waypoint for testing."""
        waypoint = Mock(spec=ROSWaypoint)
        waypoint.position = Mock()
        waypoint.position.x = 1.0
        waypoint.position.y = 2.0
        waypoint.position.z = 0.0
        return waypoint

    @pytest.fixture
    def mock_waypoints_state(self, mock_waypoint):
        """Create a mock waypoints state for testing."""
        state = Mock(spec=ROSWaypointsState)
        
        # Create multiple waypoints for testing
        waypoint1 = Mock(spec=ROSWaypoint)
        waypoint1.position = Mock()
        waypoint1.position.x = 1.0
        waypoint1.position.y = 1.0
        waypoint1.position.z = 0.0
        
        waypoint2 = Mock(spec=ROSWaypoint)
        waypoint2.position = Mock()
        waypoint2.position.x = 2.0
        waypoint2.position.y = 2.0
        waypoint2.position.z = 0.0
        
        waypoint3 = Mock(spec=ROSWaypoint)
        waypoint3.position = Mock()
        waypoint3.position.x = 3.0
        waypoint3.position.y = 3.0
        waypoint3.position.z = 0.0
        
        goal_waypoint = Mock(spec=ROSWaypoint)
        goal_waypoint.position = Mock()
        goal_waypoint.position.x = 10.0
        goal_waypoint.position.y = 10.0
        goal_waypoint.position.z = 0.0
        
        state.virtual_waypoints = [waypoint1, waypoint2, waypoint3]
        state.current_waypoint = waypoint1
        state.goal_waypoint = goal_waypoint
        
        return state

    @pytest.fixture
    def empty_waypoints_state(self):
        """Create a waypoints state with no virtual waypoints."""
        state = Mock(spec=ROSWaypointsState)
        
        goal_waypoint = Mock(spec=ROSWaypoint)
        goal_waypoint.position = Mock()
        goal_waypoint.position.x = 10.0
        goal_waypoint.position.y = 10.0
        goal_waypoint.position.z = 0.0
        
        state.virtual_waypoints = []
        state.current_waypoint = None
        state.goal_waypoint = goal_waypoint
        
        return state

    def test_initialization_success(self):
        """Test successful initialization of RemoveFirstWaypoint."""
        reset = RemoveFirstWaypoint()
        
        assert reset.is_initialized is True
        assert len(reset.reset_targets) == 1
        assert reset.reset_targets[0]['name'] == 'waypoints_state'
        assert reset.reset_targets[0]['type'] == ROSWaypointsState

    def test_initialization_with_kwargs(self):
        """Test initialization with additional keyword arguments."""
        reset = RemoveFirstWaypoint(debug=True, max_iterations=100)
        
        assert reset.is_initialized is True
        assert len(reset.reset_targets) == 1

    @patch('rclpy.logging.get_logger')
    def test_logger_initialization(self, mock_get_logger):
        """Test that logger is properly initialized."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        reset = RemoveFirstWaypoint()
        
        mock_get_logger.assert_called_with('RemoveFirstWaypoint')
        assert reset.logger == mock_logger

    def test_call_with_multiple_waypoints(self, mock_waypoints_state):
        """Test calling reset with multiple virtual waypoints."""
        reset = RemoveFirstWaypoint()
        
        # Store original state for comparison
        original_length = len(mock_waypoints_state.virtual_waypoints)
        original_second_waypoint = mock_waypoints_state.virtual_waypoints[1]
        
        # Call the reset function
        result = reset(waypoints_state=mock_waypoints_state)
        
        # Verify the result
        assert 'waypoints_state' in result
        updated_state = result['waypoints_state']
        
        # Check that first waypoint was removed
        assert len(updated_state.virtual_waypoints) == original_length - 1
        
        # Check that current waypoint is now the second waypoint
        assert updated_state.current_waypoint == original_second_waypoint
        
        # Check that the first waypoint in the list is now the original second waypoint
        assert updated_state.virtual_waypoints[0] == original_second_waypoint

    def test_call_with_single_waypoint(self):
        """Test calling reset when there's only one virtual waypoint."""
        reset = RemoveFirstWaypoint()
        
        # Create state with single waypoint
        state = Mock(spec=ROSWaypointsState)
        waypoint = Mock(spec=ROSWaypoint)
        goal_waypoint = Mock(spec=ROSWaypoint)
        
        state.virtual_waypoints = [waypoint]
        state.current_waypoint = waypoint
        state.goal_waypoint = goal_waypoint
        
        # Call the reset function
        result = reset(waypoints_state=state)
        
        # Verify the result
        updated_state = result['waypoints_state']
        
        # Check that virtual waypoints list is empty
        assert len(updated_state.virtual_waypoints) == 0
        
        # Check that current waypoint is now the goal waypoint
        assert updated_state.current_waypoint == goal_waypoint

    def test_call_with_empty_waypoints_list(self, empty_waypoints_state):
        """Test calling reset when virtual waypoints list is empty."""
        reset = RemoveFirstWaypoint()
        
        # This should raise an AttributeError due to validation
        with pytest.raises(AttributeError):
            reset(waypoints_state=empty_waypoints_state)

    def test_validate_states_success(self, mock_waypoints_state):
        """Test successful state validation."""
        reset = RemoveFirstWaypoint()
        
        # This should not raise any exceptions
        reset._validate_states(waypoints_state=mock_waypoints_state)

    def test_validate_states_missing_waypoints_state(self):
        """Test state validation with missing waypoints_state."""
        reset = RemoveFirstWaypoint()
        
        with pytest.raises(KeyError):
            reset._validate_states()

    def test_validate_states_wrong_type(self):
        """Test state validation with wrong type for waypoints_state."""
        reset = RemoveFirstWaypoint()
        
        with pytest.raises(TypeError):
            reset._validate_states(waypoints_state="not_a_waypoints_state")

    def test_validate_states_empty_virtual_waypoints(self, empty_waypoints_state):
        """Test state validation with empty virtual waypoints list."""
        reset = RemoveFirstWaypoint()
        
        with pytest.raises(AttributeError):
            reset._validate_states(waypoints_state=empty_waypoints_state)

    def test_validate_states_not_initialized(self, mock_waypoints_state):
        """Test state validation when reset is not initialized."""
        # Create reset but don't initialize it properly
        reset = RemoveFirstWaypoint.__new__(RemoveFirstWaypoint)
        reset.is_initialized = False
        
        with pytest.raises(RuntimeError):
            reset._validate_states(waypoints_state=mock_waypoints_state)

    def test_call_not_initialized(self, mock_waypoints_state):
        """Test calling reset when not initialized."""
        # Create reset but don't initialize it properly
        reset = RemoveFirstWaypoint.__new__(RemoveFirstWaypoint)
        reset.is_initialized = False
        
        with pytest.raises(RuntimeError):
            reset(waypoints_state=mock_waypoints_state)

    def test_call_with_extra_kwargs(self, mock_waypoints_state):
        """Test calling reset with extra keyword arguments."""
        reset = RemoveFirstWaypoint()
        
        # Should work fine, extra kwargs should be ignored
        result = reset(
            waypoints_state=mock_waypoints_state,
            extra_param="ignored"
        )
        
        assert 'waypoints_state' in result

    def test_get_reset_info(self):
        """Test getting reset information."""
        reset = RemoveFirstWaypoint()
        
        info = reset.get_reset_info()
        
        assert info['class_name'] == 'RemoveFirstWaypoint'
        assert info['is_initialized'] is True
        assert info['target_count'] == 1
        assert 'waypoints_state' in info['target_names']

    def test_repr(self):
        """Test string representation of reset."""
        reset = RemoveFirstWaypoint()
        
        repr_str = repr(reset)
        
        assert 'RemoveFirstWaypoint' in repr_str
        assert 'initialized=True' in repr_str
        assert 'waypoints_state' in repr_str

    def test_str(self):
        """Test human-readable string representation."""
        reset = RemoveFirstWaypoint()
        
        str_repr = str(reset)
        
        assert 'RemoveFirstWaypoint' in str_repr
        assert 'targets: 1' in str_repr

    def test_waypoint_removal_order(self):
        """Test that waypoints are removed in correct order (FIFO)."""
        reset = RemoveFirstWaypoint()
        
        # Create state with known waypoints
        state = Mock(spec=ROSWaypointsState)
        waypoint1 = Mock(spec=ROSWaypoint)
        waypoint1.id = 1
        waypoint2 = Mock(spec=ROSWaypoint)
        waypoint2.id = 2
        waypoint3 = Mock(spec=ROSWaypoint)
        waypoint3.id = 3
        goal_waypoint = Mock(spec=ROSWaypoint)
        goal_waypoint.id = 'goal'
        
        state.virtual_waypoints = [waypoint1, waypoint2, waypoint3]
        state.current_waypoint = waypoint1
        state.goal_waypoint = goal_waypoint
        
        # First call
        result1 = reset(waypoints_state=state)
        updated_state1 = result1['waypoints_state']
        
        assert len(updated_state1.virtual_waypoints) == 2
        assert updated_state1.virtual_waypoints[0].id == 2
        assert updated_state1.current_waypoint.id == 2
        
        # Second call
        result2 = reset(waypoints_state=updated_state1)
        updated_state2 = result2['waypoints_state']
        
        assert len(updated_state2.virtual_waypoints) == 1
        assert updated_state2.virtual_waypoints[0].id == 3
        assert updated_state2.current_waypoint.id == 3
        
        # Third call
        result3 = reset(waypoints_state=updated_state2)
        updated_state3 = result3['waypoints_state']
        
        assert len(updated_state3.virtual_waypoints) == 0
        assert updated_state3.current_waypoint.id == 'goal'

    def test_goal_waypoint_assignment(self):
        """Test that goal waypoint is correctly assigned when no virtual waypoints remain."""
        reset = RemoveFirstWaypoint()
        
        # Create state with single waypoint
        state = Mock(spec=ROSWaypointsState)
        last_waypoint = Mock(spec=ROSWaypoint)
        goal_waypoint = Mock(spec=ROSWaypoint)
        goal_waypoint.position = Mock()
        goal_waypoint.position.x = 100.0
        
        state.virtual_waypoints = [last_waypoint]
        state.current_waypoint = last_waypoint
        state.goal_waypoint = goal_waypoint
        
        # Call reset
        result = reset(waypoints_state=state)
        updated_state = result['waypoints_state']
        
        # Verify goal waypoint is assigned
        assert updated_state.current_waypoint == goal_waypoint
        assert updated_state.current_waypoint.position.x == 100.0

    @pytest.mark.parametrize("invalid_input", [
        None,
        "string",
        123,
        [],
        {},
        Mock()  # Mock without ROSWaypointsState spec
    ])
    def test_invalid_waypoints_state_types(self, invalid_input):
        """Test various invalid types for waypoints_state parameter."""
        reset = RemoveFirstWaypoint()
        
        with pytest.raises((TypeError, AttributeError)):
            reset(waypoints_state=invalid_input)


class TestRemoveFirstWaypointEdgeCases:
    """Test edge cases and error conditions for RemoveFirstWaypoint."""

    def test_modify_original_state_object(self):
        """Test that the original state object is modified (not copied)."""
        reset = RemoveFirstWaypoint()
        
        # Create state with waypoints
        state = Mock(spec=ROSWaypointsState)
        waypoint1 = Mock(spec=ROSWaypoint)
        waypoint2 = Mock(spec=ROSWaypoint)
        
        original_waypoints = [waypoint1, waypoint2]
        state.virtual_waypoints = original_waypoints.copy()
        state.current_waypoint = waypoint1
        state.goal_waypoint = Mock(spec=ROSWaypoint)
        
        # Call reset
        result = reset(waypoints_state=state)
        
        # Verify that the same object is returned and modified
        assert result['waypoints_state'] is state
        assert len(state.virtual_waypoints) == 1
        assert state.virtual_waypoints[0] is waypoint2

    def test_consecutive_calls_same_state(self):
        """Test multiple consecutive calls on the same state object."""
        reset = RemoveFirstWaypoint()
        
        # Create state with multiple waypoints
        state = Mock(spec=ROSWaypointsState)
        waypoints = [Mock(spec=ROSWaypoint) for _ in range(5)]
        for i, wp in enumerate(waypoints):
            wp.id = f"wp_{i}"
        
        goal_waypoint = Mock(spec=ROSWaypoint)
        goal_waypoint.id = "goal"
        
        state.virtual_waypoints = waypoints.copy()
        state.current_waypoint = waypoints[0]
        state.goal_waypoint = goal_waypoint
        
        # Make consecutive calls
        for i in range(5):
            result = reset(waypoints_state=state)
            updated_state = result['waypoints_state']
            
            expected_remaining = 5 - (i + 1)
            assert len(updated_state.virtual_waypoints) == expected_remaining
            
            if expected_remaining > 0:
                assert updated_state.current_waypoint.id == f"wp_{i + 1}"
            else:
                assert updated_state.current_waypoint.id == "goal"
        
        # Final state should have no virtual waypoints and goal as current
        assert len(state.virtual_waypoints) == 0
        assert state.current_waypoint is goal_waypoint

    def test_exception_handling_in_validation(self):
        """Test exception handling in custom validation method."""
        reset = RemoveFirstWaypoint()
        
        # Test with state that will cause AttributeError in validation
        state = Mock(spec=ROSWaypointsState)
        state.virtual_waypoints = []  # Empty list should cause AttributeError
        
        with pytest.raises(AttributeError):
            reset._validate_states(waypoints_state=state)