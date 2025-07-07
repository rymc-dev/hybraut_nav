# from colav_hybrid_automaton.automaton._internal.callbacks import on_mode_callback
# from threading import Lock
# import rclpy
# from rclpy.node import Node
# import pytest
# from rclpy.executors import MultiThreadedExecutor
# import threading
# from hybrid_automaton_interfaces.msg import HybridAutomatonMode, HybridAutomatonStatus

# @pytest.fixture
# def test_node():
#     rclpy.init()
#     test_node = Node()
#     executor = MultiThreadedExecutor()
#     executor.add_node(test_node)

#     thread = threading.Thread(target=executor.spin).start()

#     yield test_node

#     rclpy.shutdown()

# def test_mode_callback_comprehesive(test_node):

#     available_modes = ['cruise', 't2los', 'waypoint_reached', 'fallback']
#     on_mode_callback(
#         lock=Lock(),
#         node=test_node,
#         available_modes=available_modes,
#         current_mode=HybridAutomatonMode(type=HybridAutomatonMode.MODE_CRUISE),
#         mode_configuration={},
#         transition_configuration={},
#         dynamics_configuration={},
#         invariants_configuration={},
#         reset_configuration={},
#         guard_configuration={},
#         status_publisher=test_node.create_publisher(
#             msg_type=HybridAutomatonStatus,
#             topic='/hybrid_automaton/status',
#             qos_profile=10
#         )
#     )