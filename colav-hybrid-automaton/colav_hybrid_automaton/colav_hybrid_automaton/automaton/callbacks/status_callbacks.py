import rclpy
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition as LifecycleTransition
from hybrid_automaton_interfaces.msg import HybridAutomatonGuardEvaluations
from rclpy.node import Node
from colav_hybrid_automaton.automaton.constants import HybridAutomatonStatusEnum
from colav_hybrid_automaton.automaton.utils import select_highest_priority_transition
from std_msgs.msg import String
from time import time

def on_status_received_callback(node: Node, status: String):

    if status.data == HybridAutomatonStatusEnum.COMPLETED.name: 
        with node.completed_lock:
            _handle_completed_status(node)

    if status.data == HybridAutomatonStatusEnum.ACTIVE_MODE.name: # all this does is change the hybrid automaton state for executing mode
        with node.executing_mode_lock: 
            _handle_active_mode_status(node)
   
    if status.data == HybridAutomatonStatusEnum.ERROR.name:
        with node.error_lock: # On exception print set the status and move hybrid automaton to deactivate state
            _handle_error_status(node)
            
    if status.data == HybridAutomatonStatusEnum.TRANSITIONING.name:
        with node.transition_lock:
            _handle_transition_status(node)


def _handle_completed_status(node: Node):
        node._status = HybridAutomatonStatusEnum.COMPLETED
        node.get_logger().info('Waypoint reached hybrid automaton has completed.')
        future = node._trigger_transition_cli.call_async(ChangeState.Request(transition=LifecycleTransition(id=LifecycleTransition.TRANSITION_DEACTIVATE)))

def _handle_error_status(node: Node):
    node.destroy_subscription(node._status_subscription)
    node._status = HybridAutomatonStatusEnum.ERROR
    future = node._trigger_transition_cli.call_async(ChangeState.Request(transition=LifecycleTransition(id=LifecycleTransition.TRANSITION_DEACTIVATE)))
    
    rclpy.spin_until_future_complete(node,future, timeout_sec=5.0)
    if future.done():
        if not future.result().success:
            node.get_logger().error('transition request to configure for hybrid automaton lifecycle failed')

def _handle_active_mode_status(node: Node):
    node._status = HybridAutomatonStatusEnum.ACTIVE_MODE

def _handle_transition_status(node: Node):
    try:
        node._status = HybridAutomatonStatusEnum.TRANSITIONING.name
        # TODO: Move invariant check to evaluation loop if needed

        if isinstance(node._current_transition_evaluation, HybridAutomatonGuardEvaluations):
            current_transition_eval: HybridAutomatonGuardEvaluations = node._current_transition_evaluation

            if not current_transition_eval.success:
                node.get_logger().error(f"Transition evaluation failed: {current_transition_eval.message}")
                node._status_publisher.publish(String(data=HybridAutomatonStatusEnum.ERROR.name))
                return

            pending = [
                name for idx, name in enumerate(current_transition_eval.transition_names)
                if current_transition_eval.transition_values[idx]
            ]
        else:
            node._status_publisher.publish(String(data=HybridAutomatonStatusEnum.ERROR.name))
            return

        transition = select_highest_priority_transition(pending)
        node.get_logger().info(f"Executing {transition} transition.")

        if transition is None:
            raise RuntimeError('transition is none')

        if node._mode_transitions[transition]['reset'] is not None:
            node.get_logger().info(f"Executing reset: '{node._mode_transitions[transition]['reset']['name']}'")
            state_inputs = [node._configuration['states'][s]['state'] for s in node._mode_transitions[transition]['reset']['state_inputs']]
            reset_outputs = node._mode_transitions[transition]['reset']['function'](*state_inputs)
            node._waypoints_publisher.publish(*reset_outputs) # at the moment only reset type I am doing is waypoints TODO: Need to change this function

        transition_to = node._parse_transition(transition)
        node._mode_publisher.publish(String(data=transition_to))

        # poll transition
        timeout = 1
        start_time = time.time()
        rate = node.create_rate(100)
        while not node._mode == transition_to:
            if time.time() - start_time > timeout:
                node.get_logger().warn("Mode transition timed out.")
                break
            rate.sleep()  # avoid busy waiting

        node._status_publisher.publish(String(data=HybridAutomatonStatusEnum.EXECUTING_MODE.name))
    except Exception as e:
        node.get_logger().error(f"exception occured attempting transition: {str(e)}, transitioning to error state")
        node._status_publisher.publish(String(data=HybridAutomatonStatusEnum.ERROR.name)) 
        