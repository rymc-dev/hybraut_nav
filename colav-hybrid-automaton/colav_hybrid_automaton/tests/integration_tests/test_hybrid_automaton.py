"""
Integration tests of the entire system running

Validates functionality from an outsiders perspective
"""

import os
import sys
import time

import unittest
import pytest
import rclpy
from launch import LaunchDescription
import launch_ros
import launch_testing.actions
from parameterized import parameterized

from colav_interfaces.srv import Reset
from colav_interfaces.msg import Waypoint, Waypoints
from hybrid_automaton.config.qos_config import QOS_PROFILE

@pytest.mark.rostest
def generate_test_description():
    """
    Launch reset feature node for testing
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'hybrid_automaton') 

    guards_node = launch_ros.actions.Node(
        executable=sys.executable, 
        arguments=[os.path.join(file_path, 'guards_node.py' )],
        additional_env={'PYTHONBUFFERED':'1'},
    )
    dynamics_node = launch_ros.actions.Node(
        executable=sys.executable, # sys.executable python interpreted
        arguments=[os.path.join(file_path, 'execute_dynamics_node.py')],
        additional_env={'PYTHONBUFFERED':'1'}, 
    )
    reset_node = launch_ros.actions.Node(
        executable=sys.executable, 
        arguments=[os.path.join(file_path, 'execute_resets_node.py')],
        additional_env={'PYTHONBUFFERED':'1'},
    )
    chart_node = launch_ros.actions.Node(
        executable=sys.executable, 
        arguments=[os.path.join(file_path, 'execute_chart_node.py')],
        additional_env={'PYTHONBUFFERED':'1'},
    )

    return (
        LaunchDescription([guards_node, dynamics_node, reset_node, chart_node, launch_testing.actions.ReadyToTest()]), 
        {'guards_node': guards_node, 'dynamics_node': dynamics_node, 'chart_node': chart_node,'reset_node': reset_node}
    )

class TestHybridAutomaton(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        if rclpy.ok():
            rclpy.shutdown()

    def setUp(self):
        self.mock_automaton_interface = rclpy.create_node('test_chart_node')

    def test_init():
        pass

    def test_hybrid_automaton_start_srv():
        pass

    
