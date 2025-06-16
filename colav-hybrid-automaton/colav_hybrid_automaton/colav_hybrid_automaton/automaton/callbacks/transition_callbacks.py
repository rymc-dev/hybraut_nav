from rclpy.node import Node
from std_msgs.msg import String
from hybrid_automaton_interfaces.msg import HybridAutomatonGuardEvaluations as GuardsEvaluation
from colav_hybrid_automaton.automaton.constants import HybridAutomatonStatusEnum
from colav_hybrid_automaton.automaton.utils import validate_mode
from threading import Lock
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher
from typing import List
from rclpy.guard_condition import GuardCondition
from rclpy.node import Node
from colav_hybrid_automaton.automaton.utils import parse_transition
from typing import Any
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus

def transition_evaluation_callback(
    lock: Lock,
    mode: str,
    transition_config: dict,
    states: dict,
    status: HybridAutomatonStatusEnum,
    available_modes: List[str],
    guards_evaluation: GuardsEvaluation,
    mode_publisher: Publisher,
    status_publisher: Publisher,
    waypoints_publisher: Publisher,
    logger: RcutilsLogger
):
    """
    callback performs analysis on transition evalautions. 
    if a transition evaluation returns true in any of it's observations
    this function finds the priority if there are more than one activated guards
    and sets the transition name as an attribute of the node utilizing this function
    then sets status to transitioning and triggers the trigger transition engine guard condition

    """
    try:
        with lock:
            if not mode == guards_evaluation.mode:
                return
            
            if HybridAutomatonStatus.TRANSITIONING == status:
                return

            if not guards_evaluation.success:
                return
            
            pending = [
                name for idx, name in enumerate(guards_evaluation.transition_names)
                if guards_evaluation.transition_values[idx]
            ]
            transition_key = _select_highest_priority_transition(transition_config, pending)
            
            if transition_key is None:
                return
            
            # publish transiting status
            transition = transition_config[transition_key]

            reset = transition['reset']
            if reset is not None: 
                logger.info(f"executing reset: {reset['name']}")
                reset_func = reset['function']
                state_inputs = _get_reset_inputs(states, reset['state_inputs'])
                reset_output = reset_func(*state_inputs)
                waypoints_publisher.publish(reset_output[0])

            mode_publisher.publish(String(data=parse_transition(available_modes, transition_key)))
            # status publish back to active mode.            
            logger.info(f"Triggering transition to '{transition}'")
            # transition_engine.trigger()
    except Exception as e:
        logger.error(f"unexpected exception occured in 'colav_hybrid_automaton.automaton.callbacks.transition_callback': {str(e)}")
    
def _select_highest_priority_transition(transition_config: dict, pending: List[str]):
    """
    Helper function to select the highest-priority transition from a list of pending transitions.
    """
    if len(pending) == 1:
        return pending[0]
    
    highest_priority = float('inf')
    transition = None
    for name in pending:
        prio = transition_config[name]['priority']
        if prio < highest_priority:
            highest_priority = prio
            transition = name

    return transition




def transition_engine_callback(
    mode: str,
    mode_reset_configuration: dict,
    transition: str,
    mode_publisher: Publisher,
    status_publisher: Publisher,
    logger: RcutilsLogger
):
    """
    performs the transition engine callback
    when activated checks if there are any resets 
    associated with the transition if their is 
    we trigger a reset, 
    if not we straight away publish the transition
    when we enter this function we send the transitioning status

    """
    try:
        status_publisher.publish(HybridAutomatonStatus.TRANSITIONING)

        pass        

    except Exception as e: 
        logger.error(f"unexpected exception occured in 'colav_hybrid_automaton.automaton.callbacks.transition_callbacks.transition_engine_callback")

def _get_reset_inputs(states: dict, state_input_keys: list) -> List[Any]:
    """Retrieves the state values for the given invariant's state inputs."""
    return [states[s] for s in state_input_keys]