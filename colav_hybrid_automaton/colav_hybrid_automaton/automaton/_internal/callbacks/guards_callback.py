from threading import Lock
from colav_hybrid_automaton.automaton._internal.constants import HybridAutomatonStatusEnum
from typing import List, Dict
from rclpy.publisher import Publisher
from builtin_interfaces.msg import Time
from hybrid_automaton_interfaces.msg import HybridAutomatonGuardEvaluations
from rclpy.logging import RcutilsLogger
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus
from colav_hybrid_automaton.automaton._internal.utils import validate_mode
from hybrid_automaton_interfaces.msg import HybridAutomatonMode


def evaluate_guards_timer_callback(
    lock: Lock,
    mode: HybridAutomatonMode, 
    available_modes: List[str],
    status: HybridAutomatonStatusEnum,
    states: dict,
    stamp: Time,
    mode_transitions: Dict[int, str],
    status_publisher: Publisher,
    guards_evaluation_publisher: Publisher,
    logger: RcutilsLogger
):
    """
    callback evaluates transitions available for the current Hybrid automaton mode.
    """
    try:
        with lock:
            eval: HybridAutomatonGuardEvaluations = HybridAutomatonGuardEvaluations(stamp=stamp) 
            try:
                if status is HybridAutomatonStatus.TRANSITIONING:            
                    return
                else:
                    eval.mode = validate_mode(available_modes, mode)

                    eval.success = True
                    eval.transition_names = []
                    eval.guard_evaluations = []
                    eval.guard_priority = []

                    error_messages = []
                    for transition_key in mode_transitions:
                        try:
                            transition_config = mode_transitions[transition_key]
                            state_inputs = [states[s] for s in transition_config['guard']['state_inputs']]
                            guard_eval = bool(transition_config['guard']['function'](*state_inputs))
                            
                            eval.transition_names.append(transition_key)
                            eval.guard_evaluations.append(guard_eval)
                            eval.guard_priority.append(transition_config['priority'])
                        except Exception as e:
                            error_messages.append(f"{transition_key}: {str(e)}")
                            eval.success = False

                    if error_messages:
                        raise ValueError(f"guards exceptions: \n" + "- ".join(error_messages))

                    if any(eval.guard_evaluations):
                        status = HybridAutomatonStatus.TRANSITIONING
                        # status_publisher.publish(String(data=str(HybridAutomatonStatus.TRANSITIONING.name))) # TODO: Return these when status callback has been tested.
                    else:
                        status = HybridAutomatonStatus.ACTIVE_MODE
                        # status_publisher.publish(String(data=str(HybridAutomatonStatus.EXECUTING_MODE.name)))

                    
            except Exception as e:
                # status_publisher.publish(String(data=str(HybridAutomatonStatus.ERROR.name)))
                eval.success = False
                eval.message = f"exception occured during '{mode}' transition evaluation: '{str(e)}'" 

            guards_evaluation_publisher.publish(eval)

    except Exception as e: 
        logger.error(f"unexpected exception occured in 'colav_hybrid_automaton.automaton.callbacks.transition_callbacks.evaluate_transitions_timer_callback': '{str(e)}'")
        