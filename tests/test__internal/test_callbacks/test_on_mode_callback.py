from hybraut_lifecycle._internal.callbacks import on_mode_callback
from threading import Lock
import rclpy
from rclpy.node import Node
import time
import pytest
from rclpy.executors import MultiThreadedExecutor
import threading
from automaton_interfaces.msg import HybridAutomatonMode, HybridAutomatonStatus, HybridAutomatonModeState
from hybraut_lifecycle._internal.factory import HybridAutomatonFactory
import os


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

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(mock_automaton_node)

    executor_thread = threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    yield mock_automaton_node, status_publisher, status_list

    executor.shutdown()
    mock_automaton_node.destroy_node()
    rclpy.shutdown()

class TestOnModeCallback:
    """
    test suite for the on_mode_callback function a key component of the hybrid automaton
    framework.
    """

    @pytest.mark.parametrize(
        "current_mode_id, update_mode_id, expected_mode_id, expected_status_id, expected_status_message",
        [
            (
                0, # test_mode 
                1,  # goal_mode
                1, # goal_mode
                HybridAutomatonStatus.STATUS_ACTIVE_MODE, 
                'Mode transition: 0.test_mode -> 1.goal_mode'
            ),
            (
                0,
                0,
                0,
                HybridAutomatonStatus.STATUS_INFO,
                'Mode 0.test_mode already active'
            ),
            (
                0,
                50,
                0,
                HybridAutomatonStatus.STATUS_ERROR,
                "Mode validation error in on_mode_callback: Invalid mode type: 50"
            )
        ],
        ids=[
            "a valid new mode received from transition engine, allowing us to move from test_mode to goal_mode",
            "a new mode is received but it is the same mode that is already active, therefore we just ignore and send a status message informing the user.",
            "invalid new mode received, should get a valid status exception."
        ]
    )
    def test_mode_callback_comprehensive(
        self, 
        current_mode_id: int, 
        update_mode_id: int, 
        expected_mode_id: int,
        expected_status_id: HybridAutomatonStatus, 
        expected_status_message: str,
        mock_automaton_node_fixture,
        request
    ):
        """
        Test the on_mode_callback function for the different expected status outputs and to ensure that 
        the automaton_model instance has it's mode updated correctly.
        """
        mock_automaton_node, status_publisher, status_list = mock_automaton_node_fixture
        status_list.clear()
        mock_automaton_node.__getattribute__('automaton_model').current_mode = current_mode_id
        
        on_mode_callback(
            lock=Lock(),
            rcv_mode_state_msg=HybridAutomatonModeState(current_mode_id=update_mode_id),
            automaton_model=mock_automaton_node.__getattribute__('automaton_model'),
            status_publisher=status_publisher
        )

        time.sleep(0.2)

        # test_id = request.node.callspec.id if hasattr(request.node, 'callspec') else "unknown"
        test_id = 1
        assert mock_automaton_node.__getattribute__('automaton_model').current_mode == expected_mode_id, f'new mode not the same as current mode - Test ID: {test_id}'
        assert status_list[-1].type == expected_status_id, f'status value not the same - Test ID: {test_id}'
        assert status_list[-1].message == expected_status_message, f'status message not the same - Test ID: {test_id}'
    
    # TODO: Need to add custom exception messages for each of these
    @pytest.mark.parametrize(
            "lock_arg, current_mode_id, is_automaton_model_arg, is_status_publisher_arg, expected_status_type, expected_status_message",
            [
                (None, 0, True, True, HybridAutomatonStatus.STATUS_FATAL, "Unexpected error in on_mode_callback: 'NoneType' object does not support the context manager protocol"),
                (Lock(), None, True, True, HybridAutomatonStatus.STATUS_ERROR, "Mode validation error in on_mode_callback: Invalid mode type: None"),
                (Lock(), 1, False, True, HybridAutomatonStatus.STATUS_FATAL, "Unexpected error in on_mode_callback: 'NoneType' object does not support the context manager protocol"),
                # (Lock(), HybridAutomatonMode(type=HybridAutomatonMode.MODE_T2LOS), True, False, HybridAutomatonStatus.STATUS_FATAL, ""), #TODO: Need to get this test working
            ],
            ids=[
                "invalid lock arg given to automaton",
                "invalid rcv_mode_msg",
                "invalid automaton model passed",
                # "invalid status_publisher passed"
            ]
    )
    def test_mode_callback_exception_handling(
        self,
        lock_arg,
        current_mode_id,
        is_automaton_model_arg,
        is_status_publisher_arg,
        expected_status_type,
        expected_status_message,
        mock_automaton_node_fixture,
        request
    ):
        """
        Test exception handling for invalid parameter types passed to on_mode_callback.
        Note: Since the function has comprehensive try-catch blocks, most invalid inputs
        will result in error status messages rather than raised exceptions.
        """
        mock_automaton_node, status_publisher, status_list = mock_automaton_node_fixture

        on_mode_callback(
            lock=lock_arg,
            rcv_mode_state_msg=HybridAutomatonModeState(current_mode_id=current_mode_id),
            automaton_model=mock_automaton_node.__getattribute__('automaton_model') if is_automaton_model_arg else None,
            status_publisher=status_publisher if is_status_publisher_arg else None
        )

        time.sleep(0.1)

        test_id = request.node.callspec.id if hasattr(request.node, 'callspec') else "unknown"
        actual_status_type = status_list[-1].type
        assert actual_status_type == expected_status_type, f"{test_id}: test failed got status_type: {actual_status_type}, expected: {expected_status_type}"
        # actual_status_message = status_list[-1].message
        # assert actual_status_message == expected_status_message

if __name__ == '__main__':
    pytest.main([__file__])