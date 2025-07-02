from std_msgs.msg import Bool, String
from colav_hybrid_automaton.automaton._internal.constants import HybridAutomatonStatusEnum
from rclpy.node import Node
from typing import Optional, List, Any
from threading import Lock
from rclpy.publisher import Publisher
from hybrid_automaton_interfaces.msg import HybridAutomatonInvariant
from rclpy.impl.rcutils_logger import RcutilsLogger
from builtin_interfaces.msg import Time
from colav_hybrid_automaton.automaton._internal.utils import validate_mode

def evaluate_invariants_timer_callback(
    lock: Lock,
    mode: str,
    stamp: Time,
    available_modes: dict,
    invariant_config: dict,
    states: dict, 
    invariant_publisher: Publisher,
    logger: RcutilsLogger
):
    """invariant timer callback function"""
    try:
        with lock:
            invariant: HybridAutomatonInvariant = HybridAutomatonInvariant(stamp=stamp)
            try:
                invariant.mode = validate_mode(available_modes, mode)
                invariant.invariant_name = next(iter(invariant_config))
                invariant_inputs = _get_invariant_inputs(states=states, state_input_keys=invariant_config[invariant.invariant_name]['state_inputs'])
                invariant.holds = bool(invariant_config[invariant.invariant_name]['function'](*invariant_inputs))
            except Exception as e: 
                error_message = f"exception occured during '{mode}' invariant evaluation: {str(e)}"
                logger.debug(error_message)
                # node._status = HybridAutomatonStatus.ERROR.name # TODO Add this when status callback functions are working.
                # node._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                # TODO: Maybe should stop the timer here.
                invariant.error = True
                invariant.message = error_message
            
            invariant_publisher.publish(invariant)
    except Exception as e:
        logger.debug(f"unexpected exception occured in 'colav_hybrid_automaton.automaton.callbacks.innvariant_callbacks.evaluate_invariants_timer_callback': '{str(e)}'")
        
def on_invariant_received_callback(node: Node, invariant: Bool):
    """Callback for receiving an invariant update."""
    if invariant.data is False:  # invariant is true
        if node._invariant_timeout_guard_lock.acquire(blocking=False):
            try:
                node._trigger_invariant_timeout_guard.trigger()
            finally:
                node._invariant_timeout_guard_lock.release()

def handle_invariant_timeout_guard(node: Node, system_clock=None):
    """
    Triggered by a guard condition when an invariant holds.
    Waits for 1 second to allow a mode transition.
    If no transition occurs, checks if the mode is final.
    """
    with node._invariant_timeout_guard_lock:
        node.get_logger().info('Invariant timeout guard triggered')
        previous_mode = node._mode
        rate = node.create_rate(1.0, system_clock)
        rate.sleep()
        if node._mode == previous_mode:
            node.get_logger().info(
                f"Invariant held in mode {node._mode} with no transition within time tolerance."
            )
            node._status_publisher.publish(String(data=HybridAutomatonStatusEnum.COMPLETED.value))

def _get_invariant_inputs(states: dict, state_input_keys: list) -> List[Any]:
    """Retrieves the state values for the given invariant's state inputs."""
    return [states[s] for s in state_input_keys]