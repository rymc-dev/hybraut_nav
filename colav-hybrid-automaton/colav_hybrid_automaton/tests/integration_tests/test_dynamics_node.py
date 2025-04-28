#!/usr/bin/python3
"""
Integration Test Suite for COLAV dynamics_node.

This module contains Integration tests to validate the behavior of the dynamics node
used in the COLAV Hybrid Automaton. This test class extends upon the unit tests for
the guard conditions, this is mainly used for the purpose of ensuring that the communication
interfaces are working as expected

:author: Ryan McKee
:date: April 28, 2025
"""

# NOTE: Ensure guards_node not already running on ROS system otherwise there will be test conflicts

import os
import sys
import time
import unittest
from typing import List, Tuple
from std_msgs.msg import String

import pytest
import rclpy
from launch import LaunchDescription
import launch_ros
import launch_ros.actions
import launch_testing.actions
from parameterized import parameterized
from colav_interfaces.msg import DynamicsUpdate

from hybrid_automaton.config.qos_config import QOS_PROFILE
from std_srvs.srv import Trigger

from colav_interfaces.msg import GuardsStatus, UnsafeSet, AgentUpdate, ObstaclesUpdate, Waypoints
from std_msgs.msg import String

EXPECTED_NODE_NAME = 'dynamics_node'
EXPECTED_NAMESPACE = '/hybrid_automaton'


@pytest.mark.rostest
def generate_test_description():
    """
    Launch dynamics_node feature node for testing
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'hybrid_automaton', 'execute_dynamics_node.py') 

    dynamics_node = launch_ros.actions.Node(
        executable=sys.executable, # sys.executable python interpreted
        arguments=[file_path],
        additional_env={'PYTHONBUFFERED':'1'}, # std::out std::error streams being sent straight to terminal in real time
    )
    return (LaunchDescription([dynamics_node, launch_testing.actions.ReadyToTest()]), {'dynamics_node': dynamics_node})


class TestDynamicsNode(unittest.TestCase):
    """tests for dynamics node"""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        if rclpy.ok():
            rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_dynamics_node')
        self.dynamics = None

    def tearDown(self):
        self.node.destroy_node()
    
    @pytest.mark.run(order=1)
    def test_node_name_and_namespace(self):
        """verifies dynamics node name and namespace"""
        timeout = 5.0
        deadline = time.time() + timeout

        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            nodes = self.node.get_node_names_and_namespaces()
            if (EXPECTED_NODE_NAME, EXPECTED_NAMESPACE) in nodes:
                assert True
                return
        pytest.fail(
            f"Node '{EXPECTED_NODE_NAME}' in namespace '{EXPECTED_NAMESPACE}' not found. "
            f"Available nodes: {nodes}"
        )
        
    @pytest.mark.run(order=2)
    def test_node_srvs_exist(self):
        """
        test verifies that dynamics node services are available

        1. checks /hybrid_automaton/start_dynamics_eval available
        2. checks /hybrid_automaton/stop_dynamics_eval available

        :raises: AssertionError if fails
        """
        print (f'test_node_srvs exists')

        start_dynamics_eval_cli = self.node.create_client(
            Trigger,
            '/hybrid_automaton/start_dynamics_eval'
        )
        if not start_dynamics_eval_cli.wait_for_service(timeout_sec=5.0):
            assert False, 'Test: test_node_srvs exists failed!, Timeout occured while waiting for /hybrid_automaton/start_dynamics_eval'

        stop_dynamics_eval_cli = self.node.create_client(
            Trigger,
            '/hybrid_automaton/stop_dynamics_eval'
        )
        if not stop_dynamics_eval_cli.wait_for_service(timeout_sec=5.0):
            assert False, 'Test: test_node_srvs exists failed! Timeout occured while waiting for /hybrid_automaton/stop_dynamics_eval'
        
        assert True

    @pytest.mark.run(order=3)
    def test_dynamics_pub(self):
        """
        This test verifies the communication of the dynamics node!

        This test verifies:
        1. 
        2. 

        :raises: AssertionError if any test fail
        """
        start_dynamics_eval_cli = self.node.create_client(
            Trigger,
            '/hybrid_automaton/start_dynamics_eval'
        )
        if not start_dynamics_eval_cli.wait_for_service(timeout_sec=5.0):
            assert False, 'Test: test_node_srvs exists failed!, Timeout occured while waiting for /hybrid_automaton/start_dynamics_eval'
        future = start_dynamics_eval_cli.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(node=self.node, future=future, timeout_sec=5.0)
        if not future.done():
            assert False, 'Test: test_dynamics_pub srv call timeout occured!'

        if not future.result()._success:
            assert False, f'/hybrid_automaton/start_dynamics_eval service call failed: {future.result()._message}'
        
        # create a subscription and then to /hybrid_automaton/guards_status
        self.node.create_subscription(
            msg_type=DynamicsUpdate,
            topic='/hybrid_automaton/dynamics',
            callback=lambda msg: self.__setattr__('dynamics', msg),
            qos_profile=QOS_PROFILE
        )
        timeout_sec = 10.0
        start_time = time.time()
        is_dynamics_received = False
        
        # Loop until timeout is reached or dynamics are received
        while (time.time() - start_time) < timeout_sec:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.dynamics is not None:
                is_dynamics_received = True
                break
        
        # TODO: VALIDATE TIMESTAMP WITHIN TESTING TOLERANCE
        assert is_dynamics_received, f"Dynamics not received within {timeout_sec} seconds."
        assert self.dynamics.error == True, \
            "error occured"
        assert self.dynamics.error_message == "Error occured: control mode received: None not in MODES", \
            "error occured"
        
        mode_pub = self.node.create_publisher(
            msg_type=String,
            topic='/hybrid_automaton/mode',
            qos_profile=QOS_PROFILE
        )

        # Validate CRUISE without state updates
        self.dynamics = None
        mode_pub.publish(String(data="CRUISE"))
        start_time = time.time()
        while (time.time() - start_time) < timeout_sec:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.dynamics is not None:
                is_dynamics_received = True
                break
        # TODO: VALIDATE TIMESTAMP WITHIN TESTING TOLERANCE
        assert self.dynamics.control_mode == 'CRUISE', \
            f"dynamics control mode node updates, expected 'CRUISE', got: {self.dynamics.control_mode}"
        assert self.dynamics.error == True, \
            f"dynamics control mode updated, but error should have occured since there is no state updates"
        
        error_message = 'error_occured'
        assert self.dynamics.error_message == "Error occured: agent state received is of none type not type AgentUpdate", \
            f"dynamics control mode updates, but errro message should be been given, expected: {error_message}, got: {self.dynamics.error_message}"


        # validate T2LOS without state updates
        self.dynamics = None
        mode_pub.publish(String(data='T2LOS'))
        start_time = time.time()
        while (time.time() - start_time) < timeout_sec:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.dynamics is not None:
                is_dynamics_received = True
                break
        # TODO: VALIDATE TIMESTAMP WITHIN TESTING TOLERANCE
        assert self.dynamics.control_mode == 'T2LOS', \
            f"dynamics control mode node updates, expected 'T2LOS', got: {self.dynamics.control_mode}"
        assert self.dynamics.error == True, \
            f"dynamics control mode updated, but error should have occured since there is no state updates"
        
        error_message = 'error_occured'
        assert self.dynamics.error_message == "Error occured: agent state received is of none type not type AgentUpdate", \
            f"dynamics control mode updates, but errro message should be been given, expected: {error_message}, got: {self.dynamics.error_message}"
        
        # validate FALLBACK without state updates
        mode_pub.publish(String(data='FALLBACK'))
        
        # validate WAYPOINT_REACHED without state updates
        mode_pub.publish(String(data='WAYPOINT_REACHED'))


        

        # print(self.node.dynamics)
        #
        # rclpy.spin_once(self.node, timeout_sec=1.0)

        # if self.dynamics is None:
        #     assert False, f'/hybrid_automaton/dynamics service publisher failed!'
        
        # assert self.dynamics.error == True, \
        #     'something went wrong'
        # assert self.dynamics.error_message == 'Error occured: control mode received: None not in MODES', \
        #     'something went wrong'
        
        # assert True
        
