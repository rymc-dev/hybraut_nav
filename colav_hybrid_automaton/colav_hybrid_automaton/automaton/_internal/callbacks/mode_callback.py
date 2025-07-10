from threading import Lock
from rclpy.publisher import Publisher
from hybrid_automaton_interfaces.msg import HybridAutomatonMode
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus

def on_mode_callback(
    lock: Lock,
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
                message=f"Mode {rcv_mode_msg.type}.{automaton_model.modes[rcv_mode_msg.type].name} already active")
                status_publisher.publish(status_msg)

    except ValueError as e:
        status_msg = HybridAutomatonStatus(
        type=HybridAutomatonStatus.STATUS_ERROR,
        message=f"Mode validation error in on_mode_callback: {e}"
        )
        status_publisher.publish(status_msg)
    except Exception as e:
        status_msg = HybridAutomatonStatus(
        type=HybridAutomatonStatus.STATUS_FATAL ,
        message=f"Unexpected error in on_mode_callback: {e}"
        )
        status_publisher.publish(status_msg)