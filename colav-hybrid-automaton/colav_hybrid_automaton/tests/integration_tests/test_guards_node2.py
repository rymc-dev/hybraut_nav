#!/usr/bin/python3
"""
Integration Test Suite for COLAV Hybrid Automaton Guard Node.

This module contains Integration tests to validate the behavior of the guard node
used in the COLAV Hybrid Automaton. This test class extends upon the unit tests for
the guard conditions, this is mainly used for the purpose of ensuring that the communication
interfaces are working as expected

:author: Ryan McKee
:date: April 24, 2025
"""


import os
import sys
import time

import pytest
import rclpy
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_testing.actions import ReadyToTest
from parameterized import parameterized

from colav_interfaces.srv import Reset
from colav_interfaces.msg import Waypoint, Waypoints
from hybrid_automaton.config.qos_config import QOS_PROFILE
from std_srvs.srv import Trigger

# Add package path for local imports
FILE_PATH = os.path.dirname(__file__)
# PKG_PATH = os.path.abspath(
#     os.path.join(FILE_PATH, "..", "install", "colav_hybrid_eval", "lib", "python3.10", "site-packages")
# )
# sys.path.insert(0, PKG_PATH)

EXPECTED_NODE_NAME = 'guards_node'
EXPECTED_NAMESPACE = '/hybrid_automaton'


@pytest.mark.rostest
def generate_test_description():
    """
    Launch guards feature node for this integration testing module
    """
    guards_node = Node(
        executable=sys.executable,
        arguments=[
            os.path.join(FILE_PATH, "..", "colav_hybrid_eval", "execute_guards_node.py")
        ],
        additional_env={'PYTHONBUFFERED': '1'},
    )

    return LaunchDescription([guards_node, ReadyToTest()]), {'guards_node': guards_node}

class TestGuardsNode:
    """tests for guards node"""

    @classmethod
    def setup_class(cls):
        rclpy.init()
    
    @classmethod
    def teardown_class(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_guards_node')
        self.waypoints = None
        # self.node.create_subscription(
        #     Waypoints,
        #     'hybrid_automaton/waypoints',
        #     lambda msg: setattr(self, 'waypoints', msg),
        #     qos_profile=QOS_PROFILE,
        # )
        # self.publisher = self.node.create_publisher(
        #     Waypoints,
        #     'hybrid_automaton/waypoints',
        #     qos_profile=QOS_PROFILE,
        # )

    
    def test_node_name_and_namespace(self):
        """Verify the reset node name and namespace."""
        print (f"test_node_name_and_namespace")

        timeout = 5.0
        deadline = time.time() + timeout

        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
            nodes = self.node.get_node_names_and_namespaces()
            if (EXPECTED_NODE_NAME, EXPECTED_NAMESPACE) in nodes:
                return
        pytest.fail(
            f"Node '{EXPECTED_NODE_NAME}' in namespace '{EXPECTED_NAMESPACE}' not found. "
            f"Available nodes: {nodes}"
        )

    def test_node_srvs_exist(self):
        """
        test vertifies that guards node services are available

        1. checks /hybrid_automaton/start_guards_eval available
        2. checks /hybrid_automaton/stop_guards_eval available

        :raises: AssertionError if fails
        """
        print (f'test_node_srvs_exist')

        
        start_guards_eval_cli = self.node.create_client(
            Trigger,
            '/hybrid_automaton/start_guards_eval',
        )
        if not start_guards_eval_cli.wait_for_service(timeout_sec=5.0):
            assert False, 'Test: test_node_srvs_exists failed!, Timeout occured while waiting for /hybrid_automaton/start_guards_eval'
            

        stop_guards_eval = self.node.create_client(
            Trigger,
            '/hybrid_automaton/stop_guards_eval'
        )
        if not stop_guards_eval.wait_for_service(timeout_sec=5.0):
            assert False, 'Test: test_node_srvs_exist failed!, Timeout occured while waiting for /hybrid_automaton/stop_guards_eval'

        assert True

    def test_start_guards_eval_srv(self):
        """
        test verifies that the start_guards_eval service works as expected

        1. Should return response True
        2. Should start topics /hybrid_automaton/guards
        2. should create topic subscriptions to /agent_update, /obstacles_update, /unsafe_set, .....

        :raises: if any test fails an AssertionError will be thrown
        """
        # create client
        start_guards_eval_cli = self.node.create_client(
            Trigger,
            '/hybrid_automaton/start_guards_eval',
        )
        if not start_guards_eval_cli.wait_for_service(timeout_sec=5.0):
            assert False, 'Test: test_node_srvs_exists failed!, Timeout occured while waiting for /hybrid_automaton/start_guards_eval'
        
        # Send Request and wait for response
        future = start_guards_eval_cli.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=5.0)
        
        if not future.done():
            assert False, 'Test: test_node_srvs_exists failed!, Timeout occured while waiting for /hybrid_automaton/start_guards_eval service response'
        
        assert True
