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
from typing import Dict


def on_mode_callback(
    lock: Lock,
    node: Node,
    available_modes: Dict[int, float],
    current_mode: HybridAutomatonMode,
    mode: HybridAutomatonMode,
    mode_configuration: dict,
    transition_configuration: dict,
    dynamics_configuration: dict,
    invariants_configuration: dict,
    reset_configuration: dict,
    guard_configuration: dict,
    status_publisher: Publisher,
    logger: RcutilsLogger
):
    try:
        with lock:
            if mode.type == current_mode.type:
                return
            
            validate_mode(available_modes, mode)
            
            (
                mode, 
                mode_transitions,
                mode_dynamics,
                mode_invariants
            ) = generate_mode_profile(
                mode,
                mode_configuration,
                transition_configuration,
                dynamics_configuration,
                invariants_configuration,
                reset_configuration,
                guard_configuration
            )

            node._mode = mode
            node._mode_transitions = mode_transitions
            node._mode_dynamics = mode_dynamics
            node._mode_invariants = mode_invariants
            logger.debug(f"Automaton mode successfully changed to '{mode}'.")
    except Exception as e:
        logger.debug(f"Automaton mode change to '{mode}' was rejected due to an error: {e}")
        logger.error(
            f"Exception occurred in 'colav_hybrid_automaton.automaton.callbacks.mode_callbacks.on_mode_callback': {type(e).__name__}: {e}"
        )
        # status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name)) # TODO Add this back later
    