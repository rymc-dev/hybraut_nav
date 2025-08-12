# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transition Evaluator for Hybraut Hybrid Automaton
This module provides a class to evaluate transitions in a hybrid automaton
and publish the results via ROS2 topics.
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default
from hybraut_model import HybridAutomaton
from threading import Lock

from hybraut_interfaces.msg import TransitionEvaluationsMSG


class TransitionEvaluator:
    """
    Evaluator for transitions in a Hybraut hybrid automaton
    """

    def __init__(
        self,
        node: Node,
        automaton: HybridAutomaton,
        qos: QoSProfile = qos_profile_system_default,
        cb_group: CallbackGroup = ReentrantCallbackGroup(),
    ):
        """Initialize the transition evaluator."""
        self.node = node
        self.automaton = automaton
        self._init_publisher(qos=qos, cb_group=cb_group)
        self.lock = Lock()

    def _init_publisher(self, qos: QoSProfile, cb_group: CallbackGroup):
        """Initialize ROS2 publisher for transition evaluations."""
        self.transition_evaluations_publisher = self.node.create_publisher(
            TransitionEvaluationsMSG,
            "/automaton/transition_evaluations",
            qos_profile=qos,
            callback_group=cb_group,
        )

    def _validate_current_mode(self, current_mode: int) -> None:
        """Validate that the current mode exists in the automaton."""
        if current_mode not in self.automaton._modes._modes:
            raise ValueError(f"Invalid mode type: {current_mode}")

    def _evaluate_transitions(self, current_mode: int) -> None:
        """

        Runtime wrapper for transition evaluation.

        Calls the automaton's evaluation function and publishes the evaluation status.
        """
        try:
            self._validate_current_mode(current_mode)
            evaluations = self.automaton.evaluate_transitions(current_mode)
            self.transition_evaluations_publisher.publish(evaluations)
        except Exception as e:
            self.node.get_logger().error(f"Error evaluating transitions: {e}")

    def __call__(self, *, current_mode: int) -> None:
        """
        Call method to evaluate transitions for the given current mode.

        This method is intended to be called by the ROS2 executor.
        """
        with self.lock:
            self._evaluate_transitions(current_mode=current_mode)

    """ === string representation methods === """

    def __str__(self) -> str:
        return (
            f"TransitionsEvaluator(node={self.node.get_name()}, "
            f"automaton={type(self.automaton).__name__}, "
            f"publisher_topic={self.transition_evaluations_publisher.topic_name})"
        )

    def __repr__(self) -> str:
        return (
            f"TransitionsEvaluator(node={self.node.get_name()}, "
            f"automaton={type(self.automaton).__name__}, "
            f"publisher_topic={self.transition_evaluations_publisher.topic_name})"
        )


import time
import threading
from rclpy.executors import MultiThreadedExecutor
import os
import yaml


def main() -> None:
    rclpy.init()
    node = Node("mock_node")
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(node)

    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    amdl_path = "/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml"
    with open(amdl_path, "r") as f:
        amdl_dict = yaml.safe_load(f)
        automaton = HybridAutomaton.register_automaton(node=node, amdl_dict=amdl_dict)

    evaluator = TransitionEvaluator(node=node, automaton=automaton)

    # Shared current_mode as a list so it is mutable in nested scopes
    current_mode = [0]

    # Timer calls evaluator with the current current_mode value
    node.create_timer(
        0.1,
        lambda: evaluator._evaluate_transitions(current_mode=current_mode[0]),
        callback_group=ReentrantCallbackGroup(),
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
