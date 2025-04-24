import os
import sys
import time
import unittest
import uuid
import pytest

import launch
import launch_ros
import launch_ros.actions
import launch_testing.actions
from colav_interfaces.srv import Reset
from colav_interfaces.msg import Waypoint, Waypoints

pkg_path = os.path.join(os.path.dirname(__file__), '..', 'install', 'colav_hybrid_eval', 'lib', 'python3.10', 'site-packages')
sys.path.insert(0, os.path.abspath(pkg_path))

from config.qos_config import QOS_PROFILE
from parameterized import parameterized
from rclpy.task import Future

import rclpy
from typing import List, Tuple

file_path = os.path.dirname(__file__)

EXPECTED_NODE_NAME = 'resets_node'
EXPECTED_NAMESPACE = '/hybrid_automaton'

@pytest.mark.rostest
def generate_test_description():
    """
    Launches feature nodes required for unit tests in this file
    """
    # listener node
    resets_node = launch_ros.actions.Node(
        executable=sys.executable, # sys.executable python interpreted
        arguments=[os.path.join(file_path, "..", "colav_hybrid_eval", "execute_resets_node.py")],
        additional_env={'PYTHONBUFFERED':'1'}, # std::out std::error streams being sent straight to terminal in real time
    )

    return (
        launch.LaunchDescription([
            resets_node,
            launch_testing.actions.ReadyToTest()
        ]),
        {
            'resets': resets_node
        }
    )

class TestResetsNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.test_node = rclpy.create_node('test_resets_node')
        self.waypoints = None
        self.test_node.create_subscription(
            msg_type=Waypoints,
            topic='hybrid_automaton/waypoints',
            callback=lambda msg: self.__setattr__('waypoints', msg),
            qos_profile=QOS_PROFILE
        )
        self._waypoints_pub = self.test_node.create_publisher(
            msg_type=Waypoints,
            topic='hybrid_automaton/waypoints',
            qos_profile=QOS_PROFILE            
        )

    def tearDown(self):
        self.test_node.destroy_node()

    def test_node_name_and_namespace(self):
        """
        Tests if resets node has correct default initiailzation

        """
        start_time = time.time()
        timeout_period = 5

        
        while (time.time() - start_time) < timeout_period: 
            node_names_and_namespaces:List[Tuple[str, str]] = self.test_node.get_node_names_and_namespaces()
            is_correct_node_name_and_namespace = False
            for node_name_and_namespace in node_names_and_namespaces:
                if node_name_and_namespace[0] == EXPECTED_NODE_NAME and \
                        node_name_and_namespace[1] == EXPECTED_NAMESPACE:
                    is_correct_node_name_and_namespace = True
            rclpy.spin_once(self.test_node, timeout_sec=0.2)
                
        assert is_correct_node_name_and_namespace, f"reset node initialized incorrectly, default namespace should be /hybrid_automaton and name should be resets: {node_names_and_namespaces}"

    def test_node_srvs_metadata(self):
        """
        Tests if the reset node services exist
        """
        start_time = time.time()
        timeout_period = 5.0

        EXPECTED_SRVS_AND_TYPES = {'/hybrid_automaton/resets_node/reset': 'colav_interfaces/srv/Reset'}
        is_srvs_and_types_value = False

        while (time.time() - start_time) < timeout_period:
            try:
                node_srvs_and_types: List[Tuple[str, List[str]]] = self.test_node.get_service_names_and_types_by_node(
                    node_name=EXPECTED_NODE_NAME,
                    node_namespace=EXPECTED_NAMESPACE
                )

                found = set()
                for srv_name, srv_type_list in node_srvs_and_types:
                    expected_type = EXPECTED_SRVS_AND_TYPES.get(srv_name)
                    if expected_type and expected_type in srv_type_list:
                        found.add(srv_name)

                if found == set(EXPECTED_SRVS_AND_TYPES.keys()):
                    is_srvs_and_types_value = True
                    break
            except Exception: 
                pass

            time.sleep(0.2)  # wait a bit before retrying

        assert is_srvs_and_types_value, f"❌ Expected services not found within timeout expected: {EXPECTED_SRVS_AND_TYPES} actual: {node_srvs_and_types}"

    def test_node_topics_init(self):
        """
        Test if the topics for the reset node are there
        """
        start_time = time.time()
        timeout_period = 5.0

        # Define expected topics and their types
        EXPECTED_TOPICS = {"/hybrid_automaton/waypoints": "colav_interfaces/msg/Waypoints"}  # Topic names and their expected types
        is_topics_and_types_value = False

        # Retry loop with timeout
        while (time.time() - start_time) < timeout_period:
            try:
                # Get the node's topics and types
                node_topics_and_types: List[Tuple[str, List[str]]] = self.test_node.get_topic_names_and_types()

                found = set()
                for topic_name, topic_types in node_topics_and_types:
                    # Compare each topic's name and its types
                    expected_type = EXPECTED_TOPICS.get(topic_name)  # Get expected type for the topic
                    if expected_type and expected_type in topic_types:
                        found.add(topic_name)  # Add to found topics if types match

                # Check if all expected topics were found
                if found == set(EXPECTED_TOPICS.keys()):
                    is_topics_and_types_value = True
                    break
            except Exception:
                pass  # Handle exceptions gracefully

            time.sleep(0.2)  # Wait a bit before retrying

        # Assert that the expected topics were found within the timeout
        assert is_topics_and_types_value, f"❌ Expected topics not found within timeout. Expected: {EXPECTED_TOPICS}, Actual: {node_topics_and_types}"


    @parameterized.expand([
        # Test Case 1: invalid transition name
        (
            "test invalid transition name", 
            Waypoints(),
            Reset.Request(transition_name='None'),
            Waypoints(),
            Reset.Response(success=False, message=f'Reset transition name does not exist: None')
        ),
        # Test Case 2: waypoint_reached_to_cruise transition with no waypoints in list
        (
            "Test invalid waypoint_reached_to_cruise request no waypoints in state", 
            Waypoints(),
            Reset.Request(transition_name='waypoint_reached_to_cruise'),
            Waypoints(),
            Reset.Response(success=False, message=f'waypoints list size less than 1, something has went wrong is guard condition')
        ),
        # Test Case 2: waypoint_reached_to_cruise transition with no waypoints in list
        (
            "Test invalid waypoint_reached_to_cruise request only one waypoint in states", 
            Waypoints(waypoints=[Waypoint()]),
            Reset.Request(transition_name='waypoint_reached_to_cruise'),
            Waypoints(waypoints=[Waypoint()]),
            Reset.Response(success=False, message=f'waypoints list size less than 1, something has went wrong is guard condition')
        ),
        (
            "Test Valid Reset waypoint_reached_to_cruise, 2 waypoints in list", 
            Waypoints(waypoints=[Waypoint(acceptance_radius=float(10)), Waypoint(acceptance_radius=float(20))]),
            Reset.Request(transition_name='waypoint_reached_to_cruise'),
            Waypoints(waypoints=[Waypoint(acceptance_radius=float(20))]),
            Reset.Response(success=True, message=f'Reset successfully applied')
        ),
    ])
    def test_reset_srv(
        self,
        description: str,
        before_waypoints: Waypoints,
        request: Reset.Request,
        expected_waypoints: Waypoints,
        expected_response: Reset.Response
    ):
        """
        Tests is reset service works as expected 
        """
        self.test_node.get_logger().info(f'Starting test: {description}')
        
        if before_waypoints is not None:
            self._waypoints_pub.publish(before_waypoints)
        
        rclpy.spin_once(self.test_node, timeout_sec=0.2)
        timeout_period = 5.0
        try:
            reset_cli = self.test_node.create_client(
                Reset,
                '/hybrid_automaton/resets_node/reset'
            )
            reset_cli.wait_for_service(timeout_sec=timeout_period)
        except Exception as e:
            assert False, f"Exception occured during test: {str(e)}"

        future: Future = reset_cli.call_async(request)
        rclpy.spin_until_future_complete(self.test_node, future, timeout_sec=5.0)

        if not future.done():
            assert False, f"Future failed to return response"

        actual_response: Reset.Response = future.result()

        assert actual_response.success == expected_response.success, \
            f"Expected success={expected_response.success}, got {actual_response.success}"
        assert actual_response.message == expected_response.message, \
            f"Expected message={expected_response.message}, got {actual_response.message}"
        rclpy.spin_once(self.test_node, timeout_sec=1.0) # spin so that subscriber sees the waypoints update
        assert self.waypoints == expected_waypoints, \
            f"Expected waypoints={expected_waypoints}, got {self.waypoints}"