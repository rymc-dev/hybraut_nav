from rclpy.node import Node
from std_msgs.msg import String
from hybrid_automaton_interfaces.msg import Transition as AutomatonTransition
from colav_hybrid_automaton.automaton.constants import HybridAutomatonStatus
from colav_hybrid_automaton.automaton.utils import validate_mode

def evaluate_transitions_timer_callback(node: Node):
    """
    callback evaluates transitions available for the current Hybrid automaton mode.
    """
    with node._transition_eval_lock: 
        try:
            stamp = node.get_clock().now().to_msg()
            eval: AutomatonTransition = AutomatonTransition(stamp=stamp, mode=validate_mode(node._mode))
            
            if node._status is HybridAutomatonStatus.TRANSITIONING:            
                return
            else:
                eval.success = True
                eval.transition_names = []
                eval.transition_values = []
                eval.transition_priority = []

                error_messages = []
                for transition_key in node._mode_transitions:
                    try:
                        transition_config = node._mode_transitions[transition_key]
                        state_inputs = [node._configuration['states'][s]['state'] for s in transition_config['guard']['state_inputs']]
                        guard_eval = bool(transition_config['guard']['function'](*state_inputs))
                        
                        eval.transition_names.append(transition_key)
                        eval.transition_values.append(guard_eval)
                        eval.transition_priority.append(transition_config['priority'])
                    except Exception as e:
                        error_messages.append(f"{transition_config['name']}: {str(e)}")
                        eval.success = False

                if error_messages:
                    raise ValueError("Errors during evaluation: " + "; ".join(error_messages))

                if any(eval.transition_values):
                    node._status = HybridAutomatonStatus.TRANSITIONING
                    node._status_publisher.publish(String(data=str(HybridAutomatonStatus.TRANSITIONING.name)))
                else:
                    node._status = HybridAutomatonStatus.EXECUTING_MODE
                    node._status_publisher.publish(String(data=str(HybridAutomatonStatus.EXECUTING_MODE.name)))
                node._current_transition_evaluation = eval
                node._transition_evaluation_publisher.publish(eval)
        except Exception as e:
            node._status_publisher.publish(String(data=str(HybridAutomatonStatus.ERROR.name)))
            eval.success = False
            eval.message = str(e)
