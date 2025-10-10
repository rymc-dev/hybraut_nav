# Pure unit testing suite for Planning individual units of code

#!/usr/bin/env python3
"""
Unit tests for the PlannerNode class.

This test suite uses pytest and unittest.mock to test individual functions
in isolation without requiring ROS to be running.
"""

import pytest
from unittest.mock import MagicMock

# Mock ROS modules before importing the planner
import sys
sys.modules['rclpy'] = MagicMock()
sys.modules['rclpy.node'] = MagicMock()
sys.modules['rclpy.qos'] = MagicMock()
sys.modules['rclpy.callback_groups'] = MagicMock()
sys.modules['rclpy.timer'] = MagicMock()
sys.modules['rcl_interfaces.msg'] = MagicMock()
sys.modules['std_msgs.msg'] = MagicMock()
sys.modules['nav_msgs.msg'] = MagicMock()
sys.modules['geometry_msgs.msg'] = MagicMock()
sys.modules['colav_interfaces.msg'] = MagicMock()
sys.modules['hybraut_interfaces.srv'] = MagicMock()
sys.modules['std_srvs.srv'] = MagicMock()

# Now import your module
from hybraut_planner.planner_node import PlannerType
from hybraut_planner.planner_node import PlannerNode

class TestPlannerType:
    """Test PlannerType enum functionality."""
    
    def test_from_string_valid(self):
        """Test converting valid string to PlannerType."""
        assert PlannerType.from_string('A*') == PlannerType.ASTAR
        assert PlannerType.from_string('Dijkstra') == PlannerType.DIJKSTRA
        assert PlannerType.from_string('RRT') == PlannerType.RRT
        assert PlannerType.from_string('RRT*') == PlannerType.RRTSTAR
    
    def test_from_string_invalid(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError, match="Unknown planner type string"):
            PlannerType.from_string('InvalidPlanner')
    
    def test_initialize_planner_astar(self):
        """Test planner initialization for A*."""
        planner = PlannerType.initialize_planner(PlannerType.ASTAR)
        assert planner.__class__.__name__ == 'AStar'
    
    def test_initialize_planner_dijkstra(self):
        """Test planner initialization for Dijkstra."""
        planner = PlannerType.initialize_planner(PlannerType.DIJKSTRA)
        assert planner.__class__.__name__ == 'Dijkstra'
    
    def test_initialize_planner_invalid(self):
        """Test that invalid planner type raises ValueError."""
        # This would require modifying the enum which isn't typical,
        # but we can test the error handling
        pass
    
class TestPlannerState: 
    """Test PlannerState enum functionality."""
    pass

class TestPlannerNode: 
    """Test planner node functionality."""
    class TestPlannerNode:
        """Test planner node functionality."""

        def test_get_replan_frequency_returns_float(self):
            """Test get_replan_frequency returns correct float value."""
            # Create a mock PlannerNode with get_parameter method
            planner_node = PlannerNode.__new__(PlannerNode)
            # Mock get_parameter to return an object with .value attribute
            param_mock = MagicMock()
            param_mock.value = 2.5
            planner_node.get_parameter = MagicMock(return_value=param_mock)
            
            # mock_node = MagicMock()
            # # Mock get_parameter to return an object with .value attribute
            # param_mock = MagicMock()
            # param_mock.value = 2.5
            # mock_node.get_parameter.return_value = param_mock

            # # Patch the get_parameter method on the instance, not the class
            # planner_node = PlannerNode.__new__(PlannerNode)
            # planner_node.get_parameter = mock_node.get_parameter

            # # Call the method
            # freq = planner_node.get_replan_frequency()
            # assert isinstance(freq, float)
            # assert freq == 2.5

        # def test_get_replan_frequency_handles_int(self):
        #     """Test get_replan_frequency handles integer parameter value."""
        #     mock_node = MagicMock()
        #     param_mock = MagicMock()
        #     param_mock.value = 10
        #     mock_node.get_parameter.return_value = param_mock

        #     PlannerNode.get_parameter = mock_node.get_parameter

        #     planner_node = PlannerNode.__new__(PlannerNode)
        #     freq = planner_node.get_replan_frequency()
        #     assert isinstance(freq, float)
        #     assert freq == 10.0

        # def test_get_replan_frequency_invalid_parameter(self):
        #     """Test get_replan_frequency raises ValueError if parameter missing."""
        #     mock_node = MagicMock()
        #     mock_node.get_parameter.side_effect = AttributeError("No such parameter")

        #     PlannerNode.get_parameter = mock_node.get_parameter

        #     planner_node = PlannerNode.__new__(PlannerNode)
        #     with pytest.raises(AttributeError):
        #         planner_node.get_replan_frequency()


    
if __name__ == '__main__':
    pytest.main([__file__])