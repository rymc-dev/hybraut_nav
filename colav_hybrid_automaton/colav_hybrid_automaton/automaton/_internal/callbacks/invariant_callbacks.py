""" 
file containing the implementation of the invariant callback for the hybrid automaton
"""

import threading
from rclpy.publisher import Publisher
from builtin_interfaces.msg import Time
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton

from hybrid_automaton_interfaces.msg import (
    HybridAutomatonInvariantsEvaluation, 
    HybridAutomatonInvariantStatus, 
    HybridAutomatonMode,  
    HybridAutomatonStatus
)

def invariants_evaluation_callback(
        lock: threading.Lock,
        automaton_model: HybridAutomaton,
        stamp: Time,
        invariants_evaluation_publisher: Publisher,
        status_publisher: Publisher
):
    """
    Periodically evaluates the invariants for the current mode of the hybrid automaton.

    For each invariant associated with the current mode:
    - Retrieves required state inputs
    - Evaluates the invariant
    - Publishes the evaluation result to the '/hybrid_automaton/invariants' topic

    If any invariant fails (i.e., evaluates to False), the overall invariant evaluation will be marked as failed.

    If an error occurs during evaluation (e.g., invariant misconfiguration), it is considered a fatal exception,
    and a fatal status is published to the status topic.
    """
    try:
        with lock:
            current_mode = automaton_model.current_mode
            msg = HybridAutomatonInvariantsEvaluation(
                current_mode=HybridAutomatonMode(type=current_mode, stamp=stamp),
                stamp=stamp
            )

            invariant_statuses = []
            for invariant in automaton_model.modes[current_mode].invariants:
                invariant_info = invariant.instance.get_invariant_info()
                invariant_name = invariant_info['class_name']
                invariant_description = invariant_info['description']

                state_input_keys = invariant.instance.state_input_spec_names()
                state_kwargs = {
                    key: automaton_model.states[key].current_state
                    for key in state_input_keys
                }

                holds = invariant.instance(**state_kwargs)

                invariant_statuses.append(HybridAutomatonInvariantStatus(
                    invariant_name=invariant_name,
                    invariant_description=invariant_description,
                    holds=holds
                ))

            msg.invariant_statuses = invariant_statuses
            msg.overall_holds = all(status.holds for status in invariant_statuses)

            invariants_evaluation_publisher.publish(msg)

    except Exception as e:
        status_publisher.publish(HybridAutomatonStatus(
            type=HybridAutomatonStatus.STATUS_FATAL,
            message=f"Fatal exception occurred in invariant evaluation: {str(e)}",
            stamp=stamp
        ))