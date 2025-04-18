# #!/usr/bin/python3
# """
# Unit Test Suite for COLAV Hybrid Automaton Guard Node.

# This module contains unit tests to validate the behavior of the ROS2 COLAV Hybrid Automaton Guard Node
# used in the COLAV Hybrid Automaton. Both standard and edge cases are tested to ensure full coverage
# and confirm the expected functionality of each guard.

# :author: Ryan McKee
# :date: April 15, 2025
# """

# import pytest
# import rclpy
# from rclpy.node import Node
# import threading
# from scripts.nodes.guards_node import HAGuardsNode
# from colav_interfaces.msg import GuardsStatus
# from rclpy.executors import SingleThreadedExecutor
# from rclpy.node import Node
# from std_srvs.srv import Trigger


# @pytest.fixture(scope="module")
# def ha_guards_node():
#     rclpy.init()
#     node = HAGuardsNode()
#     executor = SingleThreadedExecutor()
#     executor.add_node(node)

#     def spin_node():
#         try:
#             executor.spin()
#         except Exception as e:
#             print(f"[Executor Error] {e}")

#     spin_thread = threading.Thread(target=spin_node)
#     spin_thread.daemon = True
#     spin_thread.start()

#     # Give the node some time to spin and set up correctly
#     rclpy.spin_once(node, timeout_sec=1.0)

#     yield node

#     # Cleanup: shutdown executor and destroy node
#     executor.shutdown()
#     node.destroy_node()
#     rclpy.shutdown()
#     spin_thread.join()

# @pytest.mark.dependency()
# def test_ha_guards_node_creation(ha_guards_node):
#     """
#     Test if HAGuardsNode is created successfully

#     This test verifies:
#     1. The node name is assigned correctly
#     2. The node publishers are initialized correctly
#     3. The node subs are initialized correctly
#     """

#     node = ha_guards_node

#     # Check node name and namespace
#     assert node.get_name() == 'guards_node', (
#         f"Node name test failed: expected 'guards_node', got: {node.get_name()}"
#     )
#     assert node.get_namespace() == '/hybrid_automaton', (
#         f"Namespace test failed: expected '/hybrid_automaton', got: {node.get_namespace()}"
#     )
#     services_and_types = node.get_service_names_and_types()
#     print (services_and_types)
#     expected_services = {
#         '/hybrid_automaton/start_guard_evaluation': ['std_srvs/srv/Trigger']
#     }

#     for expected_service, expected_srv_types in expected_services.items():
#         match = next(
#             ((service, srv_types) for service, srv_types in services_and_types if service == expected_service),
#             None
#         )
#         assert match is not None, f"Missing expected service: {expected_service}"
#         actual_srv_types = match[1]
#         assert actual_srv_types == expected_srv_types, (
#             f"Service {expected_service} has incorrect service type(s): expected {expected_srv_types}, got {actual_srv_types}"
#         )

# # @pytest.mark.dependency(test_ha_guards_node_creation)
# # def test_ha_guard_evaluation_start(ha_guards_node):
# #     node = ha_guards_node
# #     test_node = Node('test_node')
# #     cli = test_node.create_client(
# #         srv_type=Trigger,
# #         srv_name='/hybrid_automaton/start_guard_evaluation'
# #     )
# #     future = cli.call_async(Trigger.Request())
# #     if future.result().success:
# #         # assertion 1
# #         pass
# #     else:
# #         # assertion failed
# #         AssertionError("Failed to get /hybrid_automaton/start_guard_evaluation requests response")

# #     topics_and_types = node.get_topic_names_and_types()

# #     # Define the required topics and expected message types
# #     expected_topics = {
# #         '/agent_update': ['colav_interfaces/msg/AgentUpdate'],
# #         '/hybrid_automaton/current_mode': ['std_msgs/msg/String'],
# #         '/hybrid_automaton/guards_status': ['colav_interfaces/msg/GuardsStatus'],
# #         '/hybrid_automaton/waypoints': ['colav_interfaces/msg/Waypoints'],
# #         '/obstacles_update': ['colav_interfaces/msg/ObstaclesUpdate'],
# #     }

# #     # Check that each expected topic is present
# #     for expected_topic, expected_msg_types in expected_topics.items():
# #         match = next(
# #             ((topic, msg_types) for topic, msg_types in topics_and_types if topic == expected_topic),
# #             None
# #         )
# #         assert match is not None, f"Missing expected topic: {expected_topic}"
# #         actual_msg_types = match[1]
# #         assert actual_msg_types == expected_msg_types, (
# #             f"Topic {expected_topic} has incorrect msg type(s): expected {expected_msg_types}, got {actual_msg_types}"
# #         )

# # def generate_test_description():
# #     return {}

# # @pytest.mark.dependency(depends=[test_ha_guards_node_creation, test_ha_guard_evaluation_start])
# # def test_ha_guards_evaluation_cruise(ha_guards_node):
# #     pass

# # @pytest.mark.dependency(depends=[test_ha_guards_node_creation, test_ha_guard_evaluation_start])
# # def test_ha_guards_evaluation_t2los(ha_guards_node):
# #     pass

# # @pytest.mark.dependency(depends=[test_ha_guards_node_creation, test_ha_guard_evaluation_start])
# # def test_ha_guards_evaluation_fallback(ha_guards_node):
# #     pass

# # @pytest.mark.dependency(depends=[test_ha_guards_node_creation, test_ha_guard_evaluation_start])
# # def test_ha_guards_evaluation_waypoint_reached(ha_guards_node):
# #     pass
