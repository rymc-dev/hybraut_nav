#!/usr/bin/env python3
"""
This class is a wrapper for invariant evaluation of a Hybraut hybrid automaton model.

It is used during Hybraut runtime and is an essential component to make Hybraut an active entity.
"""

import os
import threading
import yaml
from threading import Lock
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default

from hybraut_model import HybridAutomaton
from hybraut_interfaces.msg import InvariantEvaluationsMSG

from hybraut_execution_engine.internal_state import EngineStateTracker


class InvariantEvaluator:
    """Evaluator for invariants in a Hybraut hybrid automaton."""

    def __init__(
        self,
        node: Node,
        automaton: HybridAutomaton,
        state_tracker: EngineStateTracker,
        qos: QoSProfile = qos_profile_system_default,
        cb_group: CallbackGroup = ReentrantCallbackGroup(),
    ) -> None:
        """Initialize the invariant evaluator."""
        self.node = node
        self.automaton = automaton
        self.state_tracker = state_tracker
        self._init_publisher(qos=qos, cb_group=cb_group)
        self.lock = Lock()

    def _init_publisher(
        self,
        qos: QoSProfile,
        cb_group: CallbackGroup,
    ) -> None:
        """Initialize ROS2 publisher for invariant evaluations."""
        self.invariant_evaluation_publisher = self.node.create_publisher(
            InvariantEvaluationsMSG,
            "/automaton/invariant_evaluation",
            qos_profile=qos,
            callback_group=cb_group,
        )

    def _validate_current_mode(self, current_mode: int) -> None:
        """Validate that the current mode exists in the automaton."""
        if current_mode not in self.automaton._modes._modes:
            raise ValueError(f"Invalid mode type: {current_mode}")

    def _evaluate_invariants(self) -> None:
        """
        Runtime wrapper for invariant evaluation.

        Calls the automaton's evaluation function and publishes the evaluation status.
        """
        try:
            current_mode = self.state_tracker.current_mode
            self._validate_current_mode(current_mode)
            eval_msg = self.automaton.evaluate_invariants(current_mode_id=current_mode)
            self.invariant_evaluation_publisher.publish(eval_msg)
        except Exception as e:
            self.node.get_logger().error(f"Invariant evaluation failed: {e}")
            # TODO: Publish recoverable error status for watchdog here

    def __call__(self, *args, **kwargs) -> None:
        """Allow the object to be called like a function to evaluate invariants."""
        with self.lock:
            self._evaluate_invariants()

    def __str__(self) -> str:
        return (
            f"InvariantEvaluator(node={self.node.get_name()}, "
            f"automaton={type(self.automaton).__name__}, "
            f"publisher_topic={self.invariant_evaluation_publisher.topic_name})"
        )

    def __repr__(self) -> str:
        return (
            f"InvariantEvaluator(node={repr(self.node)}, "
            f"automaton={repr(self.automaton)}, "
            f"publisher_topic={self.invariant_evaluation_publisher.topic_name})"
        )


import time

def main() -> None:
    rclpy.init()
    node = Node('mock_node')
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(node)

    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    amdl_path = '/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml'
    with open(amdl_path, "r") as f:
        amdl_dict = yaml.safe_load(f)
        automaton = HybridAutomaton.register_automaton(node=node, amdl_dict=amdl_dict)

    state_tracker: EngineStateTracker = EngineStateTracker(
        node=node,
        initial_mode=0,
        q_goals=[1]
    )

    evaluator = InvariantEvaluator(node=node, automaton=automaton, state_tracker=state_tracker)

    # Shared current_mode as a list so it is mutable in nested scopes
    current_mode = [0]

    # Timer calls evaluator with the current current_mode value
    node.create_timer(
        0.1,
        lambda: evaluator(),
        callback_group=ReentrantCallbackGroup()
    )

    # Thread to increment current_mode after 5 seconds
    def increment_mode_after_delay():
        while True: 
            time.sleep(5)
            current_mode[0] += 1
            node.get_logger().info(f"Current mode incremented to {current_mode[0]}")

    threading.Thread(target=increment_mode_after_delay, daemon=True).start()

    # Keep node alive until shutdown
    try:
        spin_thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()    

""" This is a mock main function to demonstrate the usage of InvariantEvaluator.
In a real application, this would be replaced with the actual ROS2 node setup and execution."""

if __name__ == "__main__":
    main()