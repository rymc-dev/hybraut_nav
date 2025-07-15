from threading import Lock
from rclpy.publisher import Publisher
from hybrid_automaton_interfaces.msg import HybridAutomatonModeState
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus

def on_mode_callback(
    lock: Lock,
    rcv_mode_state_msg: HybridAutomatonModeState,
    automaton_model: HybridAutomaton,
    status_publisher: Publisher
):
    """
    Callback for hybrid automaton mode subscription.
    When a new mode is received from the transition evaluators' transition engine
    on /hybrid_automaton/mode topic, this function updates the internal hybrid
    automaton model state and validates the mode transition.
    Args:
    lock: Thread lock for safe concurrent access
    node: ROS node instance
    rcv_mode_msg: Received mode message
    automaton_model: Hybrid automaton model to update
    status_publisher: Publisher for status messages
    """

    try:
        with lock:
            # Validate the new mode exists before attempting transition
            if rcv_mode_state_msg.current_mode_id not in automaton_model.modes:
                raise ValueError(f"Invalid mode type: {rcv_mode_state_msg.current_mode_id}")
            
            previous_mode = automaton_model.get_mode()
            
            # Only update if the mode is actually changing
            if previous_mode != rcv_mode_state_msg.current_mode_id:
                automaton_model.set_mode(rcv_mode_state_msg)
                # Get mode names safely with fallback
                prev_mode_name = automaton_model.modes[previous_mode].name
                new_mode_name = automaton_model.modes[rcv_mode_state_msg.current_mode_id].name
                status_msg = HybridAutomatonStatus(
                type=HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                message=f"Mode transition: {previous_mode}.{prev_mode_name} -> {rcv_mode_state_msg.current_mode_id}.{new_mode_name}"
                )
                status_publisher.publish(status_msg)
            else:
                # Log that mode is already active (optional)
                status_msg = HybridAutomatonStatus(
                type=HybridAutomatonStatus.STATUS_INFO,
                message=f"Mode {rcv_mode_state_msg.current_mode_id}.{automaton_model.modes[rcv_mode_state_msg.current_mode_id].name} already active")
                status_publisher.publish(status_msg)

    except ValueError as e:
        status_msg = HybridAutomatonStatus(
        type=HybridAutomatonStatus.STATUS_ERROR,
        message=f"Mode validation error in on_mode_callback: {e}"
        )
        status_publisher.publish(status_msg)
    except Exception as e:
        status_msg = HybridAutomatonStatus(
        type=HybridAutomatonStatus.STATUS_FATAL,
        message=f"Unexpected error in on_mode_callback: {e}"
        )
        status_publisher.publish(status_msg)


import rclpy
from rclpy.node import Node
import threading
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import QoSProfile
import os
import time
from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory

# automaton_model_file_path = os.path.join(os.path.dirname(__file__), 'test_data/test_hybrid_automaton.famd.yaml')
automaton_model_file_path = "/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/tests/unit_tests/test_automaton/test__internal/test_callbacks/test_data/test_hybrid_automaton.famd.yaml"

if __name__ == '__main__':
    rclpy.init()
    mock_node = Node('mock_node')
    qos_profile = QoSProfile(depth=10)
    
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(mock_node)

    automaton_model = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path=automaton_model_file_path, generate_mmd_diagrams=False)

    lock = threading.Lock()
    status_publisher = mock_node.create_publisher(
        topic='/hybrid_automaton/automaton_status',
        msg_type=HybridAutomatonStatus,
        callback_group=MutuallyExclusiveCallbackGroup(),
        qos_profile=qos_profile
    )
    status_list = []
    def status_callback(msg):
        status_list.append(msg)
    status_subscription = mock_node.create_subscription(
        topic='/hybrid_automaton/automaton_status',
        msg_type=HybridAutomatonStatus,
        callback=lambda msg: status_callback,
        callback_group=MutuallyExclusiveCallbackGroup(),
        qos_profile=qos_profile
    )
    mode_publisher = mock_node.create_publisher(
        HybridAutomatonModeState,
        '/hybrid_automaton/automaton_mode_state',
        qos_profile=qos_profile,
        callback_group=MutuallyExclusiveCallbackGroup()
    )

    mode_subscription = mock_node.create_subscription(
        HybridAutomatonModeState,
        '/hybrid_automaton/automaton_mode_state',
        lambda msg: on_mode_callback(
            lock=lock,
            rcv_mode_state_msg=msg,
            automaton_model=automaton_model,
            status_publisher=status_publisher
        ),
        qos_profile=qos_profile,
        callback_group=MutuallyExclusiveCallbackGroup()
    )



    executor_thread = threading.Thread(target=executor.spin)
    executor_thread.start()

    # send the mode update

    mode_state_msg = HybridAutomatonModeState(
        current_mode= 1, 
        stamp=mock_node.get_clock().now().to_msg()
    )

    mode_publisher.publish(mode_state_msg)

    time.sleep(0.2)







