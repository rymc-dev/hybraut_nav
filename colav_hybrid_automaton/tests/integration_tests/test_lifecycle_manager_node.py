# import os
# import sys
# import time
# import unittest
# from typing import List, Tuple

# import pytest
# import rclpy
# from launch import LaunchDescription
# import launch_ros
# import launch_ros.actions
# import launch_testing.actions
# from parameterized import parameterized

# from hybrid_automaton.config.qos_config import QOS_PROFILE
# from hybrid_automaton.utils import get_current_ros_time
# from std_srvs.srv import Trigger
# from geometry_msgs.msg import Point32

# from std_msgs.msg import Header
# from builtin_interfaces.msg import Time
# from colav_interfaces.msg import GuardsStatus, UnsafeSet, AgentUpdate, ObstaclesUpdate, Waypoints, Waypoint
# from std_msgs.msg import String

# EXPECTED_NODE_NAME = 'lifecycle_manager'
# EXPECTED_NAMESPACE = '/hybrid_automaton'


# @pytest.mark.rostest
# def generate_test_description():
#     """
#     Launch reset feature node for testing
#     """
#     file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'hybrid_automaton', 'execute_lifecycle_manager_node.py') 

#     lifecycle_manager = launch_ros.actions.Node(
#         executable=sys.executable, # sys.executable python interpreted
#         arguments=[file_path],
#         additional_env={'PYTHONBUFFERED':'1'}, # std::out std::error streams being sent straight to terminal in real time
#     )
#     return (LaunchDescription([lifecycle_manager, launch_testing.actions.ReadyToTest()]), {'lifecycle_manager': lifecycle_manager})

# class TestLifecycleManager(unittest.TestCase):
#     """test for lifecycle manager"""
#     @classmethod
#     def setUpClass(cls):
#         rclpy.init()
#         cls.node = rclpy.create_node('test_lifecycle_manager')

#     @classmethod
#     def tearDownClass(cls):
#         if cls.node is not None:
#             cls.node.destroy_node()
#         if rclpy.ok():
#             rclpy.shutdown()

#     @pytest.mark.run(order=1)
#     def test_node_name_and_namespace(self):

#         timeout = 5.0
#         deadline = time.time() + timeout

#         while time.time() < deadline:
#             rclpy.spin_once(self.node, timeout_sec=0.2)
#             nodes = self.node.get_node_names_and_namespaces()
#             if (EXPECTED_NODE_NAME, EXPECTED_NAMESPACE) in nodes:
#                 return
#         pytest.fail(
#             f"Node '{EXPECTED_NODE_NAME}' in namespace '{EXPECTED_NAMESPACE}' not found. "
#             f"Available nodes: {nodes}"
#         )