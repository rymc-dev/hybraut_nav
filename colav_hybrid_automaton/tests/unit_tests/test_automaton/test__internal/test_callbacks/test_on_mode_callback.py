from colav_hybrid_automaton.automaton._internal.callbacks import on_mode_callback
from threading import Lock
import rclpy
from rclpy.node import Node
import time
import pytest
from rclpy.executors import MultiThreadedExecutor
import threading
from hybrid_automaton_interfaces.msg import HybridAutomatonMode, HybridAutomatonStatus
from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory

@pytest.fixture
def mock_automaton_node_fixture():
    """fixture for the testing of on_mode_callback"""
    rclpy.init()
    
    mock_automaton_node = Node('mock_automaton_node')

    automaton_model = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path='/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
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
        "current_mode, mode_msg, expected_mode, expected_status, expected_status_message",
        [
            (
                HybridAutomatonMode.MODE_CRUISE, 
                HybridAutomatonMode.MODE_T2LOS, 
                HybridAutomatonMode.MODE_T2LOS,
                HybridAutomatonStatus.STATUS_ACTIVE_MODE, 
                'Mode transition: 0.cruise -> 1.t2los'
            ),
            (
                HybridAutomatonMode.MODE_T2LOS,
                HybridAutomatonMode.MODE_WAYPOINT_REACHED,
                HybridAutomatonMode.MODE_WAYPOINT_REACHED,
                HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                'Mode transition: 1.t2los -> 3.waypoint_reached'
            ),
            (
                HybridAutomatonMode.MODE_WAYPOINT_REACHED,
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                'Mode transition: 3.waypoint_reached -> 0.cruise'
            ),
            (
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonMode.MODE_FALLBACK,
                HybridAutomatonMode.MODE_FALLBACK,
                HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                'Mode transition: 0.cruise -> 2.fallback'
            ),
            (
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonStatus.STATUS_INFO,
                'Mode 0.cruise already active'
            ),
            (
                HybridAutomatonMode.MODE_CRUISE,
                50,
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonStatus.STATUS_ERROR,
                "Mode validation error in on_mode_callback: Invalid mode type: 50"
            )
        ],
        ids=[
            "a valid new mode received from transition engine, allowing us to move from cruise to t2los",
            "a valid new mode receive from transition engine, changing current mode for hybrid automaton state to waypoint_reached ",
            "a valid new mode received from the transtiion engine, changing current mode from waypoint_reached to cruise",
            "a valid new mode received from transition engine, allowing us to move from cruise to fallback mode.",
            "a new mode is received but it is the same mode that is already active, therefore we just ignore and send a status message informing the user.",
            "invalid new mode received, should get a valid status exception."
        ]
    )
    def test_mode_callback_comprehensive(
        self, 
        current_mode: int, 
        mode_msg: int, 
        expected_mode: int,
        expected_status: int, 
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
        mock_automaton_node.__getattribute__('automaton_model').current_mode = current_mode
        
        on_mode_callback(
            lock=Lock(),
            rcv_mode_msg=HybridAutomatonMode(type=mode_msg),
            automaton_model=mock_automaton_node.__getattribute__('automaton_model'),
            status_publisher=status_publisher
        )

        time.sleep(0.05)

        test_id = request.node.callspec.id if hasattr(request.node, 'callspec') else "unknown"
        assert mock_automaton_node.__getattribute__('automaton_model').current_mode == expected_mode, f'new mode not the same as current mode - Test ID: {test_id}'
        assert status_list[-1].type == expected_status, f'status value not the same - Test ID: {test_id}'
        assert status_list[-1].message == expected_status_message, f'status message not the same - Test ID: {test_id}'
    
    # TODO: Need to add custom exception messages for each of these
    @pytest.mark.parametrize(
            "lock_arg, rcv_mode_msg_arg, is_automaton_model_arg, is_status_publisher_arg, expected_status_type, expected_status_message",
            [
                (None, HybridAutomatonMode(type=HybridAutomatonMode.MODE_T2LOS), True, True, HybridAutomatonStatus.STATUS_FATAL, ""),
                (Lock(), None, True, True, HybridAutomatonStatus.STATUS_FATAL, ""),
                (Lock(), HybridAutomatonMode(type=HybridAutomatonMode.MODE_T2LOS), False, True, HybridAutomatonStatus.STATUS_FATAL, ""),
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
        rcv_mode_msg_arg,
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
            rcv_mode_msg=rcv_mode_msg_arg,
            automaton_model=mock_automaton_node.__getattribute__('automaton_model') if is_automaton_model_arg else None,
            status_publisher=status_publisher if is_status_publisher_arg else None
        )

        time.sleep(0.1)

        test_id = request.node.callspec.id if hasattr(request.node, 'callspec') else "unknown"
        actual_status_type = status_list[-1].type
        assert actual_status_type == expected_status_type, f"{test_id}: test failed got status_type: {actual_status_type}, expected: {expected_status_type}"
        # assert status_list[-1].message == expected_status_message
        print ('error message:')
        print (status_list[-1].message)

if __name__ == '__main__':
    pytest.main([__file__])