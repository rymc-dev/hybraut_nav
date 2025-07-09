from std_msgs.msg import String
from rclpy.node import Node
from colav_hybrid_automaton.automaton._internal.constants import  HybridAutomatonStatusEnum
from threading import Lock
from rclpy.publisher import Publisher
# from colav_hybrid_automaton.automaton._internal.factory import generate_mode_profile

from typing import Tuple
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.node import Node
from colav_hybrid_automaton.automaton._internal.utils import validate_mode
from typing import List
from hybrid_automaton_interfaces.msg import HybridAutomatonMode
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus
from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory


def on_mode_callback(
    lock: Lock,
    node: Node,
    rcv_mode_msg: HybridAutomatonMode,
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
            if rcv_mode_msg.type not in automaton_model.modes:
                raise ValueError(f"Invalid mode type: {rcv_mode_msg.type}")
            
            previous_mode = automaton_model.get_mode()
            
            # Only update if the mode is actually changing
            if previous_mode != rcv_mode_msg.type:
                automaton_model.set_mode(rcv_mode_msg)
                
                # Get mode names safely with fallback
                prev_mode_name = automaton_model.modes[previous_mode].name
                new_mode_name = automaton_model.modes[rcv_mode_msg.type].name
                
                status_msg = HybridAutomatonStatus(
                    type=HybridAutomatonStatus.STATUS_ACTIVE_MODE,
                    message=f"Mode transition: {previous_mode}.{prev_mode_name} -> {rcv_mode_msg.type}.{new_mode_name}"
                )
                status_publisher.publish(status_msg)
            else:
                # Log that mode is already active (optional)
                status_msg = HybridAutomatonStatus(
                    type=HybridAutomatonStatus.STATUS_INFO,
                    message=f"Mode {rcv_mode_msg.type}.{automaton_model.modes[rcv_mode_msg.type].name} already active"
                )
                status_publisher.publish(status_msg)
                
    except ValueError as e:
        status_msg = HybridAutomatonStatus(
            type=HybridAutomatonStatus.STATUS_ERROR,
            message=f"Mode validation error in on_mode_callback: {e}"
        )
        status_publisher.publish(status_msg)
        
    except Exception as e:
        status_msg = HybridAutomatonStatus(
            type=HybridAutomatonStatus.STATUS_ERROR,
            message=f"Unexpected error in on_mode_callback: {e}"
        )
        status_publisher.publish(status_msg)

import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from threading import Lock
from hybrid_automaton_interfaces.msg import HybridAutomatonMode, HybridAutomatonStatus
from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory

if __name__ == '__main__':
    """a simple example of how this callback could be utilized within the hybrid automaton model"""
    rclpy.init()
    test_node = Node('test_node')
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(test_node)    

    status_publisher = test_node.create_publisher(
        topic='hybrid_automaton/status',
        msg_type=HybridAutomatonStatus,
        qos_profile=10
    )
    status_list = []

    # FIX 1: Convert message to string for logging
    def status_callback(msg):
        test_node.get_logger().info(f"Status received - Type: {msg.type}, Message: {msg.message}")
        status_list.append(msg)  # Also append to list for testing

    status_subscription = test_node.create_subscription(
        topic='hybrid_automaton/status',
        msg_type=HybridAutomatonStatus,
        callback=status_callback,
        qos_profile=10
    )

    # Start spinning in background thread
    threading.Thread(target=executor.spin, daemon=True).start()
    
    # Give executor time to start
    import time
    time.sleep(0.1)
    
    automaton = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path='/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
        generate_mmd_diagrams=False
    )
    test_node.__setattr__('automaton_model', automaton)
    
    mode_msg = HybridAutomatonMode(type=HybridAutomatonMode.MODE_CRUISE)
    
    # Call the callback function
    on_mode_callback(
        lock=Lock(),
        node=test_node,
        rcv_mode_msg=mode_msg,
        automaton_model=test_node.__getattribute__('automaton_model'),
        status_publisher=status_publisher
    )

    # Wait for message to be processed
    time.sleep(1.0)
    
    print(f"Status list length: {len(status_list)}")
    for i, status in enumerate(status_list):
        print(f"Status {i}: Type={status.type}, Message='{status.message}'")

    rclpy.shutdown()