from std_msgs.msg import Bool, String
from colav_hybrid_automaton.automaton.constants import HybridAutomatonStatus
from rclpy.node import Node
from typing import Optional, List, Any


def evaluate_invariants_timer_callback(node: Node):
    """invariant timer callback function"""
    with node._invariant_evaluation_lock:
        try:
            _invariant_key = next(iter(node._mode_invariant))
            _invariant_inputs = _get_invariant_inputs(_invariant_key)
            _invariant_value:bool = node._mode_invariant[_invariant_key](*_invariant_inputs)

            node._invariant = True
            node._invariant_publisher.publish(Bool(data=_invariant_value))
        except Exception as e: 
            node._status = HybridAutomatonStatus.ERROR.name
            node.get_logger().error(f"Exception occured during invariant evaluation callback: {str(e)}")
            node._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
            # TODO: Maybe should stop the timer here.
            return
        
def on_invariant_status_received(node: Node, invariant: Bool):
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
            node._status_publisher.publish(String(data=HybridAutomatonStatus.COMPLETED.name))

def _get_invariant_inputs(node: Node, invariant_key: str) -> List[Any]:
    """Retrieves the state values for the given invariant's state inputs."""

    invariants = node._configuration.get('invariants', {})
    states = node._configuration.get('states', {})

    state_input_names = invariants.get(invariant_key, {}).get('state_inputs', [])

    return [
        states[name]['state']
        for name in state_input_names
        if name in states
    ]