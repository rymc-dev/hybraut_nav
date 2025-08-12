#! /usr/bin/env python3
"""

"""

from rclpy.node import Node
from hybraut_model import HybridAutomaton
from threading import Lock

from hybraut_interfaces.msg import InvariantEvaluationsMSG

from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup


class HybrautInvariantEvaluator:
    """ 
    Evaluator for invariants
    """

    def __init__(
        self, node: Node, automaton: HybridAutomaton, 
        qos: QoSProfile = qos_profile_system_default, 
        cb_group: CallbackGroup = ReentrantCallbackGroup()
    ): 
        """Initialize the invariant evaluator."""
        self.node = node
        self.automaton = automaton

        self.__post_init__(
            qos=qos,
            cb_group=cb_group
        )

    def __post_init__(
        self,
        qos: QoSProfile = qos_profile_system_default,
        cb_group: CallbackGroup = ReentrantCallbackGroup()
    ):
        """Post-initialization for invariant evaluator."""
        self.lock = Lock()
        self.invariant_evaluation_publisher = self.node.create_publisher(
            InvariantEvaluationsMSG,
            "/automaton/invariant_evaluation",
            qos_profile=qos,
            callback_group=cb_group
        )

    """ === evaluation functions === """

    def _validate_current_mode(self, current_mode: int) -> None:
        """Validate that the current mode exists in the automaton"""
        if current_mode not in list(self.automaton._modes._modes.keys()):
            raise ValueError(f"Invalid mode type: {current_mode}")
        
    def _evaluate_invariants(self, current_mode: int)-> None:
        """
        runtime wrapper for the invariant evaluation of the hybrid automaton model. 
        function on runtime will call the invariant evaluation function for the model 
        and publish the invariant evaluation status.
        """
        try:
            self._validate_current_mode(current_mode=current_mode)
            eval = self.automaton.evaluate_invariants(current_mode_id=current_mode)
            self.invariant_evaluation_publisher.publish(eval)
        except Exception as e: 
            # TODO: Need to add some code here to publish a recoverable error status for the watchdog.
            pass

    def __call__(self, *args, **kwds):
        self._evaluate_invariants(**kwds) 
    
    def __str__(self):
        pass

    def __repr__(self):
        pass



import yaml
import rclpy

from rclpy.node import Node
import threading
from rclpy.executors import MultiThreadedExecutor

import os

def main():
    rclpy.init()
    mock_node = Node('mock_node')
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(mock_node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    path = '/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml'
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        hybraut_model:HybridAutomaton = HybridAutomaton.register_automaton(node=mock_node, amdl_dict=data)

    hybraut_invariant_evaluator: HybrautInvariantEvaluator = HybrautInvariantEvaluator(node=mock_node, automaton=hybraut_model)
    hybraut_invariant_evaluator(
        current_mode = 0
    )


if __name__ == '__main__':
    main()