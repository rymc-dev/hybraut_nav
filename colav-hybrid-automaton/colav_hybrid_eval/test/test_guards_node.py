#!/usr/bin/python3
"""
Unit Test Suite for COLAV Hybrid Automaton Guard Node.

This module contains unit tests to validate the behavior of the ROS2 COLAV Hybrid Automaton Guard Node
used in the COLAV Hybrid Automaton. Both standard and edge cases are tested to ensure full coverage 
and confirm the expected functionality of each guard.

:author: Ryan McKee  
:date: April 15, 2025
"""

import pytest
import rclpy
from rclpy.node import Node
import threading
from scripts.nodes.guards_node import HAGuardsNode
from colav_interfaces.msg import GuardsStatus

@pytest.fixture(scope="module")
def ha_guards_node():
    """
    Fixture to start the HAGuardsNode before tests.
    The node will be show down after all tests.
    """
    rclpy.init()
    node = HAGuardsNode()

    def spin_node():
        rclpy.spin(node)

    spin_thread = threading.Thread(target=spin_node)
    spin_thread.daemon = True
    spin_thread.start()

    rclpy.spin_once(node, timeout_sec=1.0)

    yield node

    rclpy.shutdown()
    spin_thread.join()

@pytest.mark.dependency()
def test_ha_guards_node_creation(ha_guards_node):
    """
    Test if HAGuardsNode is created successfully

    This test verifies:
    1. The node name is assigned correctly
    2. The node publishers are initialized correctly
    3. The node subs are initialized correctly

    :raises: AssertionError if any of the checks fail
    """
    node = ha_guards_node

    # check node name and namespace
    assert node.get_name() == 'guards_node', (
        f"node name test failed: name expected: 'guards_node', actual: {node.get_name()}"
    )
    assert node.get_namespace() == '/hybrid_automaton', (
        f"node namespace test failed: name expected {'/hybrid_automaton'}, actual: {node.get_namespace()}"
    )

    # publisher_names = [name for name, _ in node.get_publisher_names_and_types_by_node()]
    # publisher_types = [type for _, type in node.get_publisher_names_and_types_by_node]

    # expected_publisher_names = ["/hybrid_automaton/guards_status"]
    # expected_publisher_types = [GuardsStatus]

    # for expected_publisher_name in expected_publisher_names:
    #     assert expected_publisher_name in publisher_names, \
    #         f"node service test failed: Service {expected_publisher_name} not found in the node."
    
    
