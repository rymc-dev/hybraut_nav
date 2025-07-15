import pytest
import rclpy
from rclpy.node import Node
import os
from automaton._internal.callbacks.invariant_callback import invariants_evaluation_callback
from automaton._internal.factory import HybridAutomatonFactory
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus, HybridAutomatonModeState, HybridAutomatonInvariantStatus, HybridAutomatonInvariantsEvaluation
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
import threading
import time

TEST_FAMD_PATH = os.path.join(os.path.dirname(__file__), 'test_data/test_hybrid_automaton.famd.yaml')

@pytest.fixture
def mock_automaton_node_fixture():
    """fixture for the testing of on_mode_callback"""
    rclpy.init()
    
    mock_automaton_node = Node('mock_automaton_node')

    automaton_model = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path=TEST_FAMD_PATH, 
        generate_mmd_diagrams=False
    )

    mock_automaton_node.__setattr__('automaton_model', automaton_model)
    
    status_publisher = mock_automaton_node.create_publisher(
        topic='hybrid_automaton/status',
        msg_type=HybridAutomatonStatus,
        qos_profile=10
    )
    
    status_list = []

    # FIX 1: Convert message to string for logging
    def status_callback(msg):
        mock_automaton_node.get_logger().info(f"Status received - Type: {msg.type}, Message: {msg.message}")
        status_list.append(msg)  # Also append to list for testing

    mock_automaton_node.create_subscription(
        topic='hybrid_automaton/status',
        msg_type=HybridAutomatonStatus,
        callback=status_callback,
        qos_profile=10
    )

    invariant_list = []
    def invariant_callback(msg):
        mock_automaton_node.get_logger().info(f"invariant received")
        invariant_list.append(msg)  # Also append to list for testing

    mock_automaton_node.create_subscription(
        topic='hybrid_automaton/invariant_evaluation',
        msg_type=HybridAutomatonInvariantsEvaluation,
        callback=invariant_callback,
        callback_group=MutuallyExclusiveCallbackGroup(),
        qos_profile=10
    )
    invariant_evaluation_publisher = mock_automaton_node.create_publisher(
        topic='hybrid_automaton/invariant_evaluation',
        msg_type=HybridAutomatonInvariantsEvaluation,
        callback_group=MutuallyExclusiveCallbackGroup(),
        qos_profile=10
    )

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(mock_automaton_node)

    executor_thread = threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    yield mock_automaton_node, status_publisher, status_list, invariant_evaluation_publisher, invariant_list

    executor.shutdown()
    mock_automaton_node.destroy_node()
    rclpy.shutdown()


class TestInvariantCallback:
    """test suite for the invariants evaluation callback"""

    @pytest.mark.parametrize(
            "current_mode_id, expected_invariant_output",
            [
                (0, True),
                (1, False)
            ],
            ids=[
                "test valid for test_mode invariant with output",
                "test valid output for goal_mode invariant"
            ]
    )
    def test_invariant_evaluation_callback_comprehensive(self, current_mode_id, expected_invariant_output: bool, mock_automaton_node_fixture, request):
        mock_automaton_node, status_publisher, status_list, invariant_evaluation_publisher, invariant_list = mock_automaton_node_fixture
        mock_automaton_node.__getattribute__('automaton_model').current_mode = current_mode_id

        invariants_evaluation_callback(
            lock=threading.Lock(),
            automaton_model=mock_automaton_node.__getattribute__('automaton_model'),
            stamp=mock_automaton_node.get_clock().now().to_msg(),
            invariants_evaluation_publisher=invariant_evaluation_publisher,
            status_publisher=status_publisher
        )

        time.sleep(0.2)
        
        assert expected_invariant_output == invariant_list[-1].overall_holds


if __name__ == '__main__':
    pytest.main([__file__])

# # if __name__ == '__main__':
# #     rclpy.init()
    
# #     mock_automaton_node = Node('mock_automaton_node')

# #     automaton_model = HybridAutomatonFactory.hybrid_automaton_registry(
# #         automaton_famd_path=TEST_FAMD_PATH, 
# #         generate_mmd_diagrams=False
# #     )

# #     mock_automaton_node.__setattr__('automaton_model', automaton_model)
    
# #     status_publisher = mock_automaton_node.create_publisher(
# #         topic='hybrid_automaton/status',
# #         msg_type=HybridAutomatonStatus,
# #         qos_profile=10
# #     )
    
# #     status_list = []

# #     # FIX 1: Convert message to string for logging
# #     def status_callback(msg):
# #         mock_automaton_node.get_logger().info(f"Status received - Type: {msg.type}, Message: {msg.message}")
# #         status_list.append(msg)  # Also append to list for testing

# #     mock_automaton_node.create_subscription(
# #         topic='hybrid_automaton/status',
# #         msg_type=HybridAutomatonStatus,
# #         callback=status_callback,
# #         qos_profile=10
# #     )

# #     invariant_list = []
# #     def invariant_callback(msg):
# #         mock_automaton_node.get_logger().info(f"invariant received")
# #         invariant_list.append(msg)  # Also append to list for testing

# #     mock_automaton_node.create_subscription(
# #         topic='hybrid_automaton/invariant_evaluation',
# #         msg_type=HybridAutomatonInvariantsEvaluation,
# #         callback=invariant_callback,
# #         callback_group=MutuallyExclusiveCallbackGroup(),
# #         qos_profile=10
# #     )
# #     invariant_evaluation_publisher = mock_automaton_node.create_publisher(
# #         topic='hybrid_automaton/invariant_evaluation',
# #         msg_type=HybridAutomatonInvariantsEvaluation,
# #         callback_group=MutuallyExclusiveCallbackGroup(),
# #         qos_profile=10
# #     )

# #     executor = MultiThreadedExecutor(num_threads=2)
# #     executor.add_node(mock_automaton_node)

# #     executor_thread = threading.Thread(target=executor.spin, daemon=True)
# #     executor_thread.start()

    

# #     fixture = (mock_automaton_node, status_publisher, status_list, invariant_evaluation_publisher, invariant_list)

# #     TestInvariantCallback().test_invariant_evaluation_callback_comprehensive(
# #         current_mode_id=0,
# #         expected_invariant_output=True,
# #         mock_automaton_node_fixture=fixture,
# #         request="Hello world"
# #     )

# #     executor.shutdown()
# #     mock_automaton_node.destroy_node()
# #     rclpy.shutdown()