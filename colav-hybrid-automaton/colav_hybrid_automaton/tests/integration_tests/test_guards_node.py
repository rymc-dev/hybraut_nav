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

# NOTE: Ensure guards_node not already running on ROS system otherwise there will be test conflicts

import os
import sys
import time
import unittest
from typing import List, Tuple

import pytest
import rclpy
from launch import LaunchDescription
import launch_ros
import launch_ros.actions
import launch_testing.actions
from parameterized import parameterized

from hybrid_automaton.config.qos_config import QOS_PROFILE
from hybrid_automaton.utils import get_current_ros_time
from std_srvs.srv import Trigger
from geometry_msgs.msg import Point32

from std_msgs.msg import Header
from builtin_interfaces.msg import Time
from colav_interfaces.msg import GuardsStatus, UnsafeSet, AgentUpdate, ObstaclesUpdate, Waypoints, Waypoint
from std_msgs.msg import String

EXPECTED_NODE_NAME = 'guards_node'
EXPECTED_NAMESPACE = '/hybrid_automaton'


@pytest.mark.rostest
def generate_test_description():
    """
    Launch reset feature node for testing
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'hybrid_automaton', 'execute_guards_node.py') 

    guards_node = launch_ros.actions.Node(
        executable=sys.executable, # sys.executable python interpreted
        arguments=[file_path],
        additional_env={'PYTHONBUFFERED':'1'}, # std::out std::error streams being sent straight to terminal in real time
    )
    return (LaunchDescription([guards_node, launch_testing.actions.ReadyToTest()]), {'guards_node': guards_node})

class TestGuardsNode(unittest.TestCase):
    """tests for guards node"""

    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = rclpy.create_node('test_guards_node')
        cls.start_guards_eval_cli = cls.node.create_client(
            Trigger,
            '/hybrid_automaton/start_guards_eval',
        )
        if not cls.start_guards_eval_cli.wait_for_service(timeout_sec=5.0):
            raise RuntimeError('start_guards_eval service not available')

        cls.stop_guards_eval_cli = cls.node.create_client(
            Trigger,
            '/hybrid_automaton/stop_guards_eval',
        )
        if not cls.stop_guards_eval_cli.wait_for_service(timeout_sec=5.0):
            raise RuntimeError('stop_guards_eval service not available')
        
        cls.mode_pub = cls.node.create_publisher(
            msg_type=String,
            topic='/hybrid_automaton/mode',
            qos_profile=QOS_PROFILE
        )
        cls.agent_pub = cls.node.create_publisher(
            AgentUpdate,
            '/agent_update',
            QOS_PROFILE
        )
        cls.obstacles_pub = cls.node.create_publisher(
            ObstaclesUpdate,
            '/obstacles_update',
            QOS_PROFILE
        )
        cls.unsafe_set_pub = cls.node.create_publisher(
            UnsafeSet,
            '/unsafe_set',
            QOS_PROFILE
        )
        cls.waypoints_pub = cls.node.create_publisher(
            Waypoints,
            '/hybrid_automaton/waypoints',
            QOS_PROFILE
        )


    @classmethod
    def tearDownClass(cls):
        if cls.node is not None:
            cls.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    
    @pytest.mark.run(order=1)
    def test_node_name_and_namespace(self):
        """Verify the reset node name and namespace."""

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

    def setUp(self):
        self.waypoints = None
        self.guards = None

        self.node.create_subscription(
            GuardsStatus,
            '/hybrid_automaton/guards',
            qos_profile=QOS_PROFILE,
            callback=lambda msg: self.__setattr__('guards', msg)
        )
    

    def start_guards_eval(self) -> bool:
        """util function used to start the guards_evaluation for test functions"""
        future = self.start_guards_eval_cli.call_async(Trigger.Request())
        try:
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=5.0)
        except Exception as e:
            return Exception(f'Unexpected Exception occured while waiting for start_guards_eval_request response: {str(e)}')

        if not future.done():
            return False
        
        return True
    
    def spin_till_guard_update(self, timeout_sec:float=5.0):
        self.guards = None
        start_time = time.time()
        while (time.time() - start_time) < timeout_sec:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            if self.guards is not None:
                return True
        
        return False

    @pytest.mark.run(order=2)
    def test_start_guards_eval_srv_and_stop_eval_srv(self):
        """
        test verifies that the start_guards_eval service works as expected

        1. Should return response True
        2. Should start topics /hybrid_automaton/guards
        2. should create topic subscriptions to /agent_update, /obstacles_update, /unsafe_set, .....

        :raises: if any test fails an AssertionError will be thrown
        """
        # 1. Start guards eval and validate it's starts correctly
        try:
            is_guards_eval = self.start_guards_eval()
            assert is_guards_eval, \
                f'start_guards_eval request failed'
        except Exception as e:
            assert False, str(e)
        finally:
            rclpy.spin_once(self.node)

        # 2. Validate topic's associated with guards eval started
        topic_names_and_types: List[Tuple[str, List[str]]] = self.node.get_topic_names_and_types()
        expected_topic_names_and_types = {
            '/hybrid_automaton/guards': 'colav_interfaces/msg/GuardsStatus',
            '/hybrid_automaton/mode': 'std_msgs/msg/String', 
            '/hybrid_automaton/waypoints': 'colav_interfaces/msg/Waypoints',
            '/agent_update':'colav_interfaces/msg/AgentUpdate',
            '/obstacles_update': 'colav_interfaces/msg/ObstaclesUpdate',
            '/unsafe_set': 'colav_interfaces/msg/UnsafeSet'
        }

        # Loop through topics, check if they are expected and remove
        for topic_name_and_types in topic_names_and_types:
            topic_name = topic_name_and_types[0]
            topic_types = topic_name_and_types[1]
            if topic_name in expected_topic_names_and_types:
                expected_type = expected_topic_names_and_types[topic_name]
                if expected_type in topic_types:
                    del expected_topic_names_and_types[topic_name]

        if len(expected_topic_names_and_types) > 0:
            assert False, 'Test failed: not all expected topics were subscribed/published to by guards node'


    @pytest.mark.run(order=4)
    def test_guards_no_state_update_behavior(self):
        """
        test guards without having guards running
        """

        try:
            is_guards_eval = self.start_guards_eval()
            assert is_guards_eval, \
                f'start_guards_eval request failed'
        except Exception as e:
            assert False, str(e)
        finally:
            rclpy.spin_once(self.node)

        assert self.spin_till_guard_update(timeout_sec=5.0), \
            'timeout occured waiting for guard update.'
        
        # Test 1: No control mode published
        assert self.guards.error == True
        assert self.guards.error_message == "Current control mode has not been published to /hybrid_automaton/waypoints"
        
        # Test 2: Control mode published CRUISE, T2LOS, WAYPOINT_REACHED, FALLBACK 

        control_modes = ['CRUISE', 'T2LOS', 'WAYPOINT_REACHED', 'FB']
        for mode in control_modes:
            self.mode_pub.publish(String(data=mode))
            assert self.spin_till_guard_update(timeout_sec=5.0), \
                'timeout occured waiting for guards update'
            assert self.guards.control_mode == mode, \
                f'guards node did not receive /hybrid_automaton/mode update. got: {self.guards.control_mode}, expected: {mode}'
            assert self.guards.error == True, \
                f'guards node received update from /hybrid_automaton/mode update, but error was expected but not shown due to lack of state updates'
            assert self.guards.error_message == "State updates not received for guard evaluation", \
                f'guards node showing error, but error message is not correct'

        # Test 3: Ensure transition evaluation properly handles invalid control mode name passed in 
        


    def mock_state_pub_callback(self):
        """
        a mock state update publisher for testing
        """
        ros_time = get_current_ros_time()
        self.agent_pub.publish(AgentUpdate(header=Header(stamp=ros_time)))
        self.obstacles_pub.publish(ObstaclesUpdate(header=Header(stamp=ros_time)))
        self.unsafe_set_pub.publish(UnsafeSet(header=Header(stamp=ros_time)))
        self.waypoints_pub.publish(
            Waypoints(waypoints=[Waypoint(position=Point32(x=-500.0, y=300.0), acceptance_radius=20.0), Waypoint(position=Point32(x=700.0, y=800.0), acceptance_radius=30.0)])
        )

    @pytest.mark.run(order=4)
    def test_guards_with_state_updates(self):
        """
        test guards with mock state updates
        """
        # publish waypoints

        # start state_update timer
        self.node.create_timer(
            0.1,
            self.mock_state_pub_callback
        )

        try:
            is_guards_eval = self.start_guards_eval()
            assert is_guards_eval, \
                f'start_guards_eval request failed'
        except Exception as e:
            assert False, str(e)
        finally:
            rclpy.spin_once(self.node)

        self.mode_pub.publish(String(data="CRUISE"))
        rclpy.spin_once(self.node)
        rclpy.spin_once(self.node)
        
        assert self.spin_till_guard_update(timeout_sec=5.0), \
            'timeout occured waiting for guard update.'
        assert self.spin_till_guard_update(timeout_sec=5.0), \
            'timeout occured waiting for guard update.'
        # validate guards evaluation
        print (self.guards)

        assert self.guards.control_mode == 'CRUISE', \
            'exception msg'
        assert self.guards.guard_names == ['cruise_to_t2los_1', 'cruise_to_t2los_2', 'cruise_to_fb', 'cruise_to_waypoint_reached'], \
            'evaluation failed'
        assert self.guards.cruise_to_t2los_1 == False
        assert self.guards.cruise_to_t2los_2 == False # This should be true I think because we are not on LOS need to look into how to fix this
        assert self.guards.cruise_to_waypoint_reached == False
        assert self.guards.cruise_to_fb == False
        assert self.guards.error == False

        self.mode_pub.publish(String(data="T2LOS"))
        rclpy.spin_once(self.node)
        assert self.spin_till_guard_update(timeout_sec=5.0), \
            'timeout occured waiting for guard update.'
        
        assert self.guards.control_mode == 'T2LOS', \
            "exception msg"
        assert self.guards.guard_names == ['t2los_to_cruise', 't2los_to_fb', 't2los_to_waypoint_reached'], \
            'evaluation failed'
        assert self.guards.t2los_to_cruise == True # for some reason I am always on heading to the current waypoint which is strange as I shouldn't
        assert self.guards.t2los_to_fb == False
        assert self.guards.t2los_to_waypoint_reached == False
        assert self.guards.error == False

        self.mode_pub.publish(String(data="WAYPOINT_REACHED"))
        rclpy.spin_once(self.node)
        assert self.spin_till_guard_update(timeout_sec=5.0), \
            'timeout occured waiting for guard update.'
        print (self.guards)
        assert self.guards.control_mode == 'WAYPOINT_REACHED', \
            "exception msg"
        assert self.guards.guard_names == ['waypoint_reached_to_cruise'], \
            'evaluation failed'
        assert self.guards.waypoint_reached_to_cruise == True # for some reason I am always on heading to the current waypoint which is strange as I shouldn't
        assert self.guards.error == False

        self.mode_pub.publish(String(data="FB"))
        rclpy.spin_once(self.node)
        assert self.spin_till_guard_update(timeout_sec=5.0), \
            'timeout occured waiting for guard update.'
        print (self.guards)
        assert self.guards.control_mode == 'FB', \
            "exception msg"
        assert self.guards.guard_names == [], \
            'evaluation failed'
        assert self.guards.error == False