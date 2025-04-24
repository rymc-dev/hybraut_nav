#!/usr/bin/python3
"""
Integration Test Suite for COLAV Hybrid Automaton Resets Node.

This module contains Integration tests to validate the behavior of the resets node
used in the COLAV Hybrid Automaton. This test class extends upon the unit tests for
the reset conditions, this is mainly used for the purpose of ensuring that the communication
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
from config.qos_config import QOS_PROFILE

# Add package path for local imports
FILE_PATH = os.path.dirname(__file__)
# PKG_PATH = os.path.abspath(
#     os.path.join(FILE_PATH, "..", "install", "colav_hybrid_eval", "lib", "python3.10", "site-packages")
# )
# sys.path.insert(0, PKG_PATH)

EXPECTED_NODE_NAME = 'resets_node'
EXPECTED_NAMESPACE = '/hybrid_automaton'


@pytest.mark.rostest
def generate_test_description():
    """
    Launch reset feature node for this integration testing module
    """
    resets_node = Node(
        executable=sys.executable,
        arguments=[
            os.path.join(FILE_PATH, "..", "colav_hybrid_eval", "execute_resets_node.py")
        ],
        additional_env={'PYTHONBUFFERED': '1'},
    )

    return LaunchDescription([resets_node, ReadyToTest()]), {'resets_node': resets_node}


class TestResetsNode:
    """Tests for the resets node."""

    @classmethod
    def setup_class(cls):
        rclpy.init()

    @classmethod
    def teardown_class(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_resets_node')
        self.waypoints = None
        self.node.create_subscription(
            Waypoints,
            'hybrid_automaton/waypoints',
            lambda msg: setattr(self, 'waypoints', msg),
            qos_profile=QOS_PROFILE,
        )
        self.publisher = self.node.create_publisher(
            Waypoints,
            'hybrid_automaton/waypoints',
            qos_profile=QOS_PROFILE,
        )

    def tearDown(self):
        self.node.destroy_node()

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

    def test_service_metadata(self):
        """Verify the reset service exists with correct type."""
        print (f"test_service_metadata")

        client = self.node.create_client(
            Reset,
            '/hybrid_automaton/resets_node/reset'
        )
        client.wait_for_service(timeout_sec=5.0)

        services = self.node.get_service_names_and_types_by_node(
            node_name=EXPECTED_NODE_NAME,
            node_namespace=EXPECTED_NAMESPACE
        )
        assert any(
            name == '/hybrid_automaton/resets_node/reset' and 'colav_interfaces/srv/Reset' in types
            for name, types in services
        ), f"Service '/hybrid_automaton/resets_node/reset' not found in {services}"

    def test_topic_publications(self):
        """Verify the waypoints topic is published with correct type."""
        print (f"test_topic_publications")
        timeout = 5.0
        deadline = time.time() + timeout

        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
            topics = self.node.get_topic_names_and_types()
            if any(
                name == '/hybrid_automaton/waypoints' and 'colav_interfaces/msg/Waypoints' in types
                for name, types in topics
            ):
                return
        pytest.fail(
            "Topic '/hybrid_automaton/waypoints' with type 'colav_interfaces/msg/Waypoints' not found."
        )

    @parameterized.expand([
        (
            "invalid_transition",
            Waypoints(),
            Reset.Request(transition_name='None'),
            Waypoints(),
            Reset.Response(success=False, message='Reset transition name does not exist: None'),
        ),
        (
            "no_waypoints, waypoint_reached_to_cruise",
            Waypoints(),
            Reset.Request(transition_name='waypoint_reached_to_cruise'),
            Waypoints(),
            Reset.Response(success=False, message='waypoints list size less than 1, something has went wrong is guard condition'),
        ),
        (
            "single_waypoint, waypoint_reached_to_cruise",
            Waypoints(waypoints=[Waypoint()]),
            Reset.Request(transition_name='waypoint_reached_to_cruise'),
            Waypoints(waypoints=[Waypoint()]),
            Reset.Response(success=False, message='waypoints list size less than 1, something has went wrong is guard condition'),
        ),
        (
            "valid_reset, waypoint_reached_to_cruise",
            Waypoints(waypoints=[Waypoint(acceptance_radius=10.0), Waypoint(acceptance_radius=20.0)]),
            Reset.Request(transition_name='waypoint_reached_to_cruise'),
            Waypoints(waypoints=[Waypoint(acceptance_radius=20.0)]),
            Reset.Response(success=True, message='Reset successfully applied'),
        ),
        (
            "no_waypoints, cruise_to_t2los",
            Waypoints(),
            Reset.Request(transition_name='cruise_to_t2los'),
            Waypoints(),
            Reset.Response(success=False, message='waypoints list size less than 1, something has went wrong is guard condition'),
        ),
        (
            "single_waypoint, cruise_to_t2los",
            Waypoints(waypoints=[Waypoint()]),
            Reset.Request(transition_name='cruise_to_t2los'),
            Waypoints(waypoints=[Waypoint()]),
            Reset.Response(success=False, message='waypoints list size less than 1, something has went wrong is guard condition'),
        ),
        # TODO: Add tests for cruise_to_t2los test.
    ])
    def test_reset_service(
        self,
        name,
        input_waypoints,
        request,
        expected_waypoints,
        expected_response,
    ):
        """Test the reset service behavior."""
        print (f"test_reset_service: Test Case: {name}")

        if input_waypoints.waypoints:
            self.publisher.publish(input_waypoints)
            rclpy.spin_once(self.node, timeout_sec=0.2)

        client = self.node.create_client(
            Reset, '/hybrid_automaton/resets_node/reset'
        )
        client.wait_for_service(timeout_sec=5.0)

        future = client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=5.0)

        response = future.result()
        assert response.success == expected_response.success, \
            f"Expected success={expected_response.success}, got={response.success}"
        assert response.message == expected_response.message, \
            f"Expected message='{expected_response.message}', got='{response.message}'"

        # Ensure updated waypoints are received
        rclpy.spin_once(self.node, timeout_sec=1.0)
        assert self.waypoints == expected_waypoints, \
            f"Expected waypoints={expected_waypoints}, got={self.waypoints}"
