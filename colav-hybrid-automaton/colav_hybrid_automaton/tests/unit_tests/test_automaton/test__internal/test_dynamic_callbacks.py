# import rclpy
# import pytest
# from threading import Lock
# from typing import Dict, Callable, Any
# from rclpy.node import Node
# from builtin_interfaces.msg import Time
# from colav_interfaces.msg import AgentUpdate
# from hybrid_automaton_interfaces.msg import Dynamics
# from colav_hybrid_automaton.automaton.callbacks import evaluate_dynamics_timer_callback
# from colav_hybrid_automaton.automaton.constants import QOS_PROFILE

# @pytest.fixture(scope="function")
# def test_node() -> Node:
#     rclpy.init()
#     node = Node("test_node")
#     yield node
#     node.destroy_node()
#     rclpy.shutdown()

# @pytest.mark.parametrize(
#     "lock, mode, available_modes, mode_dynamics, states",
#     [
#         # 1. bad agent_state
#         (
#             Lock(),
#             "cruise",
#             ["cruise", "t2los", "waypoint_reached", "fallback"],
#             {},
#             {'agent_state': {'state': AgentUpdate(velocity=10.0)}},
#         ),
#     ],
# )
# def test_evaluate_dynamics_timer_callback(
#     test_node: Node,
#     lock: Lock,
#     mode: str,
#     available_modes: str,
#     mode_dynamics: Dict[str, Dict[str, Callable[..., Any]]],
#     states: Dict[str, Any],
# ):
#     # Create a placeholder for the dynamic message
#     dynamic_holder = {'msg': None}

#     def callback(msg):
#         dynamic_holder['msg'] = msg

#     test_node_publisher = test_node.create_publisher(
#         Dynamics,
#         '/hybrid_automaton/dynamics',
#         QOS_PROFILE,
#     )

#     test_node.create_subscription(
#         Dynamics,
#         '/hybrid_automaton/dynamics',
#         callback=callback,
#         qos_profile=QOS_PROFILE,
#     )

#     evaluate_dynamics_timer_callback(
#         lock,
#         mode,
#         available_modes,
#         mode_dynamics,
#         states,
#         test_node.get_clock().now().to_msg(),
#         test_node_publisher,
#         test_node.get_logger()
#     )

#     # Allow some time for the callback to be called
#     rclpy.spin_once(test_node, timeout_sec=1.0)

#     assert dynamic_holder['msg'] is not None