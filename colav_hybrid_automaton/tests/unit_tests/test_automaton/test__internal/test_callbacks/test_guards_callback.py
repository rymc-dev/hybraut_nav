# import rclpy
# from rclpy.node import Node
# from colav_hybrid_automaton.automaton._internal.callbacks.guards_callback import evaluate_guards_timer_callback
# import pytest
# from hybrid_automaton_interfaces.msg import (
#     HybridAutomatonGuardEvaluations,
#     HybridAutomatonStatus,
#     HybridAutomatonMode
# )
# from threading import Lock

# import threading
# from rclpy.executors import MultiThreadedExecutor


# @pytest.fixture
# def setup():
#     rclpy.init()

#     test_node = Node('test_node')
#     stamp = test_node.get_clock().now().to_msg()
#     available_modes = {0: "MODE_CRUISE", 1:"MODE_T2LOS", 2:"MODE_FALLBACK", 3:"MODE_WAYPOINT_REACHED", 255: "MODE_INACTIVE"}
#     lock = Lock,
#     mode_transitions = {}
#     status_publisher = test_node.create_publisher(
#         msg_type=HybridAutomatonStatus,
#         topic='/hybrid_automaton/status',
#         qos_profile=10
#     )
#     guard_evaluation_publisher = test_node.create_publisher(
#         msg_type=HybridAutomatonGuardEvaluations,
#         topic="/hybrid_automaton/guards",
#         qos_profile=10
#     )
#     executor = MultiThreadedExecutor(num_threads=2)
#     executor.add_node(test_node)

#     status_values = []
#     status_sub = test_node.create_subscription(
#         msg_type=HybridAutomatonStatus,
#         topic='/hybrid_automaton/status',
#         callback=lambda msg: status_value.append(msg)
#         qos_profile=10
#     )

#     guard_evaluation_values = []
#     guard_sub = test_node.create_subscription(
#         msg_type=HybridAutomatonGuardEvaluations,
#         topic="/hybrid_automaton/guards",
#         callback=lambda msg: guard_evaluation_values.append(msg),
#         qos_profile=10
#     )

#     threading.Thread(target=executor.spin).start()

#     yield test_node, stamp, mode_transitions, status_publisher, guard_evaluation_publisher, lock, available_modes, status_values, guard_evaluation_values

#     rclpy.shutdown()

# @pytest.mark.parametrize(
#     "mode, status, states_kwargs",
#     [
#         # Test 1: test something 
#         (),
#         # Test 2: test something else
#     ]
# )
# def test_evaluate_guards_timer_callback_comprehensive(
#     setup,
#     mode: HybridAutomatonMode,
#     states: dict,
#     status: HybridAutomatonStatus,

# ):
#     [test_node, stamp, mode_transitions, status_publisher, guard_evaluation_publisher, lock, available_modes, status_values, guard_evaluation_values] = setup


#     evaluate_guards_timer_callback(
#         lock = lock,
#         mode = mode,
#         available_modes=available_modes,
#         status = status,
#         states = states,
#         stamp = test_node.get_clock().now().to_msg(),
#         mode_transitions=mode_transitions,
#         status_publisher=status_publisher,
#         guards_evaluation_publisher=guard_evaluation_publisher,
#         logger=test_node.get_logger()
#     )

#     assert True
    
#     # here we do assertions on the status_values and guard_evaluation_values
    