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
from hybrid_automaton_interfaces.msg import HybridAutomatonMode, HybridAutomatonStatus

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

    threading.Thread(target=executor.spin).start()

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
        "current_mode, new_mode, expected_status, expected_status_message",
        [
            (
                HybridAutomatonMode.MODE_CRUISE, 
                HybridAutomatonMode.MODE_T2LOS, 
                HybridAutomatonStatus.STATUS_ACTIVE_MODE, 
                'Mode transition: 0.cruise -> 1.t2los'
            ),
            (
                HybridAutomatonMode.MODE_T2LOS,
                HybridAutomatonMode.MODE_WAYPOINT_REACHED,
                HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                'Mode transition: 1.t2los -> 3.waypoint_reached'
            ),
            (
                HybridAutomatonMode.MODE_WAYPOINT_REACHED,
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                'Mode transition: 3.waypoint_reached -> 0.cruise'
            ),
            (
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonMode.MODE_FALLBACK,
                HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                'Mode transition: 0.cruise -> 2.fallback'
            ),
            (
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonMode.MODE_CRUISE,
                HybridAutomatonStatus.STATUS_INFO,
                'Mode 0.cruise already active'
            )
        ],
        ids=[
            "a valid new mode received from transition engine, allowing us to move from cruise to t2los",
            "a valid new mode receive from transition engine, changing current mode for hybrid automaton state to waypoint_reached ",
            "a valid new mode received from the transtiion engine, changing current mode from waypoint_reached to cruise",
            "a valid new mode received from transition engine, allowing us to move from cruise to fallback mode.",
            "a new mode is received but it is the same mode that is already active, therefore we just ignore and send a status message informing the user."
        ]
    )
    def test_mode_callback_comprehesive_valid_inputs(
        self, 
        current_mode: int, 
        new_mode: int, 
        expected_status: int, 
        expected_status_message: str,
        mock_automaton_node_fixture,
        request
    ):
        """
        Test
        """
        mock_automaton_node, status_publisher, status_list =  mock_automaton_node_fixture
        mock_automaton_node.__getattribute__('automaton_model').current_mode = current_mode
        on_mode_callback(
            lock=Lock(),
            rcv_mode_msg=HybridAutomatonMode(type=new_mode),
            node=mock_automaton_node,
            automaton_model= mock_automaton_node.__getattribute__('automaton_model'),
            status_publisher=status_publisher
        )

        time.sleep(0.2)

        assert mock_automaton_node.__getattribute__('automaton_model').current_mode == new_mode, 'new mode not the same as current mode'
        print (f"most recent status: {status_list[-1]}")
        assert status_list[0].type == expected_status, 'status value not the same'
        assert status_list[0].message == expected_status_message, 'status message not the same.'

    def test_mode_callback_invalid_mode_values(mock_automaton_node_fixture):

        

    def test_mode_callback_invalid_arg_inputs(
            
    ):
        pass

# import time

# if __name__ == '__main__':
#     rclpy.init()
    
#     mock_automaton_node = Node('mock_automaton_node')

#     automaton_model = HybridAutomatonFactory.hybrid_automaton_registry(
#         automaton_famd_path='/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
#         generate_mmd_diagrams=False
#     )

#     mock_automaton_node.__setattr__('automaton_model', automaton_model)
    
#     status_publisher = mock_automaton_node.create_publisher(
#         topic='hybrid_automaton/status',
#         msg_type=HybridAutomatonStatus,
#         qos_profile=10
#     )
    
#     status_list = []

#     # FIX 1: Convert message to string for logging
#     def status_callback(msg):
#         mock_automaton_node.get_logger().info(f"Status received - Type: {msg.type}, Message: {msg.message}")
#         status_list.append(msg)  # Also append to list for testing

#     mock_automaton_node.create_subscription(
#         topic='hybrid_automaton/status',
#         msg_type=HybridAutomatonStatus,
#         callback=status_callback,
#         qos_profile=10
#     )

#     executor = MultiThreadedExecutor(num_threads=2)
#     executor.add_node(mock_automaton_node)

#     threading.Thread(target=executor.spin).start()

#     on_mode_callback(
#         lock=Lock(),
#         rcv_mode_msg=HybridAutomatonMode(type=HybridAutomatonMode.MODE_T2LOS),
#         node=mock_automaton_node,
#         automaton_model= mock_automaton_node.__getattribute__('automaton_model'),
#         status_publisher=status_publisher
#     )

#     assert mock_automaton_node.__getattribute__('automaton_model').current_mode == HybridAutomatonMode.MODE_T2LOS

#     time.sleep(0.2)

#     print (status_list)
#     assert len(status_list) == 1
#     assert status_list[0].type == HybridAutomatonStatus.STATUS_ACTIVE_MODE
#     assert status_list[0].message == 'Mode transition: 0.cruise -> 1.t2los'


#     on_mode_callback(
#         lock=Lock(),
#         rcv_mode_msg=HybridAutomatonMode(type=HybridAutomatonMode.MODE_CRUISE),
#         node=mock_automaton_node,
#         automaton_model=mock_automaton_node.__getattribute__('automaton_model'),
#         status_publisher=status_publisher
#     )
#     time.sleep(0.2)
#     assert len(status_list) == 2
#     assert status_list[1].type == HybridAutomatonStatus.STATUS_ACTIVE_MODE
#     assert status_list[1].message == 'Mode transition: 1.t2los -> 0.cruise'

#     on_mode_callback(
#         lock=Lock(),
#         rcv_mode_msg=HybridAutomatonMode(type=HybridAutomatonMode.MODE_WAYPOINT_REACHED),
#         node=mock_automaton_node,
#         automaton_model=mock_automaton_node.__getattribute__('automaton_model'),
#         status_publisher=status_publisher
#     )
#     time.sleep(0.2)
#     assert len(status_list) == 3
#     assert status_list[2].type == HybridAutomatonStatus.STATUS_ACTIVE_MODE
#     assert status_list[2].message == 'Mode transition: 0.cruise -> 3.waypoint_reached'



#     rclpy.shutdown()