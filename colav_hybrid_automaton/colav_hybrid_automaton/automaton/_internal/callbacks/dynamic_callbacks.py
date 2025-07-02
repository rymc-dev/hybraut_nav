from hybrid_automaton_interfaces.msg import HybridAutomatonDynamics
from rclpy.node import Node
from typing import List, Any, Dict, Callable
from threading import Lock
from colav_hybrid_automaton.automaton._internal.utils import validate_mode
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher
from hybrid_automaton_interfaces.msg import HybridAutomatonMode 



def evaluate_dynamics_timer_callback(
    lock: Lock,
    mode: HybridAutomatonMode,
    available_modes: Dict[int, str],
    mode_dynamics: Dict[str, Callable[..., Any]],
    states: Dict[str, dict],
    stamp: Time,
    dynamic_publisher: Publisher,
    logger: RcutilsLogger
):
    """
    Evaluate and publish dynamics based on the current mode and system state.
    """
    try:
        with lock:
            msg = HybridAutomatonDynamics(stamp=stamp)
            try:
                validate_mode(available_modes, mode)
                
                # msg.mode = validated_mode

                # Extract the dynamic function key (e.g., 'cruise')
                msg.dynamic_parameters.controller_name = mode_dynamics['name']
                dynamics_instance = mode_dynamics['instance']
                state_input_keys = mode_dynamics['state_inputs']
                state_inputs = _get_dynamic_inputs(state_input_keys, states)

                msg.dynamic_parameters.dynamic_name = mode_dynamics['dynamic_outputs']['dynamic_parameter_names']
                msg.dynamic_parameters.dynamic_units = mode_dynamics['dynamic_outputs']['dynamic_parameter_metrics']
                msg.dynamic_parameters.dynamic_value = dynamics_instance.__call__(**state_inputs)
                msg.success = True
            
            except Exception as e:
                msg.success = False
                msg.message = f"exception occured during '{mode}' dynamic evaluation: '{str(e)}'"

            dynamic_publisher.publish(msg)
    except Exception as e:
        logger.error(f"unexpected exception occured during 'colav_hybrid_automaton.automaton.callbacks.dynamic_callbacks.evaluate_dynamics_timer_callback': '{str(e)}'")

def _get_dynamic_inputs(state_input_keys: str, states: dict) -> List[Any]:
    """
    Extract inputs for the dynamic function from the states dictionary.
    """

    return {k: states[k] for k in state_input_keys}
