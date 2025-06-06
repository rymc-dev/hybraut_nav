from hybrid_automaton_interfaces.msg import Dynamics
from rclpy.node import Node
from typing import List, Any, Dict, Callable
from threading import Lock
from colav_hybrid_automaton.automaton.utils import validate_mode
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher



def evaluate_dynamics_timer_callback(
    lock: Lock,
    mode: str,
    available_modes: List[str],
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
            msg = Dynamics(stamp=stamp)
            try:
                validated_mode = validate_mode(available_modes, mode)
                
                msg.mode = validated_mode

                # Extract the dynamic function key (e.g., 'cruise')
                dynamic_key = validated_mode if validated_mode in mode_dynamics else next(iter(mode_dynamics))
                msg.dynamic_parameters.controller_name = dynamic_key

                dynamic_function = mode_dynamics[dynamic_key]['function']
                state_input_keys = mode_dynamics[dynamic_key]['state_inputs']
                state_inputs = _get_dynamic_inputs(state_input_keys, states)

                msg.dynamic_parameters.dynamic_name = ['velocity', 'yaw_rate']
                msg.dynamic_parameters.dynamic_units = ['m/s', 'r/s']
                msg.dynamic_parameters.dynamic_value = dynamic_function(*state_inputs)
                msg.success = True
            
            except Exception as e:
                logger.error(f'Exception during dynamics creation: {str(e)}')
                msg.success = False
                msg.message = str(e)

            dynamic_publisher.publish(msg)
    except Exception as e:
        logger.error(e)

def _get_dynamic_inputs(state_input_keys: str, states: dict) -> List[Any]:
    """
    Extract inputs for the dynamic function from the states dictionary.
    """

    return [states[k] for k in state_input_keys]