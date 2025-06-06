from std_msgs.msg import String
from rclpy.node import Node
from colav_hybrid_automaton.automaton.constants import HybridAutomatonStatus
from threading import Lock
from rclpy.publisher import Publisher
from colav_hybrid_automaton.automaton.factory import generate_mode_profile

from typing import Tuple
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.node import Node

def on_mode_callback(
    lock: Lock,
    node: Node,
    current_mode: str,
    mode: String,
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
            if mode.data == current_mode:
                return
            
            (
                mode, 
                mode_transitions,
                mode_dynamics,
                mode_invariant
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
            node._mode_invariant = mode_invariant
    except Exception as e:
        logger.error(f"Exception occured in 'colav_hybrid_automaton.automaton.callbacks.mode_callbacks.on_mode_callback': {str(e)}")
        # status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name)) # TODO Add this back later
    