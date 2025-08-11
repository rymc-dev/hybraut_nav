#! /usr/bin/env python3
"""

"""

from rclpy.node import Node
from hybraut_model import HybridAutomaton
from threading import Lock

from hybraut_interfaces.msg import InvariantEvaluationMSG

from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup


class HybrautInvariantEvaluator:
    """ 
    Evaluator for invariants
    """

    def __init__(self, node: Node, automaton: HybridAutomaton): 
        """Initialize the invariant evaluator."""
        self.node = node
        self.automaton = automaton

        self.__post_init__()

    def __post_init__(
        self,
        qos: QoSProfile = qos_profile_system_default,
        cb_group: CallbackGroup = ReentrantCallbackGroup()
    ):
        """Post-initialization for invariant evaluator."""
        self.lock = Lock()
        self.invariant_evaluation_publisher = self.node.create_publisher(
            InvariantEvaluationMSG,
            "/automaton/invariant_evaluation",
            qos_profile=qos,
            callback_group=cb_group
        )

    """ === evaluation functions === """

    def _validate_current_mode(current_mode: int, hybraut_model: HybridAutomaton) -> None:
        """Validate that the current mode exists in the automaton"""
        if current_mode not in list(hybraut_model._modes._modes.keys()):
            raise ValueError(f"Invalid mode type: {current_mode}")
        
    def _evaluate_invariants(current_mode: int, hybraut_model: HybridAutomaton) -> InvariantEvaluationMSG:
        pass

    def __call__(self, *args, **kwds):
        pass 
    
    def __str__(self):
        pass

    def __repr__(self):
        pass


def main():
    ...

if __name__ == '__main__':
    main()