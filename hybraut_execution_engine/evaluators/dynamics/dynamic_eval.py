#! /usr/bin/env python3
""" """

# TODO: dynamics evaluation is going to output to it's own output topic like with resets.
#       not only simplifying the code for the executor and improving udp communication
#       but also enhancing the modularity and reusability of the codebase.

from rclpy.node import Node
from typing import List, Any, Dict, Callable
from threading import Lock
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher
from hybraut_models import HybridAutomaton
import threading
from hybraut_interfaces.msg import (
    AutomatonDynamicsEvaluation,
    AutomatonMode,
    AutomatonStatus,
)

from colav_interfaces.msg import AgentState, WaypointsState
from typing import Tuple, Any

from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup

from hybraut_execution_engine.evaluators.dynamics.dynamic_bus import DynamicsHub

from hybraut_execution_engine.internal_state import EngineStateTracker
from hybraut_interfaces.msg import AutomatonEvents


class DynamicEvaluator:
    """
    Evaluator for dynamics
    """

    def __init__(
        self,
        node: Node,
        state_tracker: EngineStateTracker,
        automaton: HybridAutomaton,
        event_publisher: Publisher,
    ):
        """
        Initialize the dynamics evaluator.
        """
        self.node = node
        self.automaton = automaton
        self.state_tracker = state_tracker
        self.event_publisher = event_publisher
        self.dynamics_hub = DynamicsHub(
            node=node, dynamics_registry=automaton._dynamic_registry
        )

        self.__post_init__()

    def __post_init__(
        self,
        qos: QoSProfile = qos_profile_system_default,
        cb_group: CallbackGroup = ReentrantCallbackGroup(),
    ):
        """
        Post-initialization for the dynamics evaluator.
        """
        self.lock = Lock()
        self.dynamics_evaluation_publisher = self.node.create_publisher(
            AutomatonDynamicsEvaluation,
            "/automaton/dynamics_evaluation",
            qos_profile=qos,
            callback_group=cb_group,
        )

    """ === evaluation functions ==="""

    def _validate_current_mode(
        self, current_mode: int, hybraut_model: HybridAutomaton
    ) -> Tuple:
        """Validate that the current mode exists in the automaton"""
        if not hybraut_model._modes.is_mode(current_mode):
            raise ValueError(f"Invalid mode type: {current_mode}")

    def _evaluate_dynamics(
        self, current_mode: int, hybraut_model: HybridAutomaton, stamp: Time
    ) -> Tuple[Any, AutomatonDynamicsEvaluation]:
        """evaluates the dynamics for the current automaton mode"""

        try:
            cmd, msg = hybraut_model.evaluate_dynamics(current_mode)
        except RuntimeError as e:
            raise RuntimeError(f"exception occured during _evaluate_dynamics: {str(e)}")
        except Exception as e:
            raise Exception(
                f"unexpected exception occured during _evaluate_dynamics: '{str(e)}'"
            )

        return cmd, msg

    def dynamics_evaluation_callback(self):
        """
        Callback for evaluating dynamics in the hybrid automaton on a timer.

        At regular time intervals, this function evaluates the dynamics associated with the
        current mode of the hybrid automaton.

        We publish dynamics based on agent_state and other states assigend to the dynamic controllers
        in the hybrid automaton dynamics module, we publish the dynamics updates to '/hybrid_automaton/dynamics
        and at the same time if anything goes wrong we publish status updates to '/hybrid_automaton/status
        """
        try:
            current_mode = self.state_tracker.get_current_mode()
            # self._validate_current_mode(current_mode, self.automaton)

            cmd, dynamic_evaluation = self._evaluate_dynamics(
                current_mode=current_mode,
                hybraut_model=self.automaton,
                stamp=self.node.get_clock().now().to_msg(),
            )
            self.dynamics_evaluation_publisher.publish(dynamic_evaluation)
            if cmd is not None:
                self.dynamics_hub.publish(name=dynamic_evaluation.dynamic_name, msg=cmd)
        except Exception as e:
            self.event_publisher.publish(
                AutomatonEvents(
                    type=AutomatonEvents.HANDLE_RECOVERABLE_ERROR,
                    message=f"exception occured during dynamics evaluation: {str(e)}",
                    stamp=self.node.get_clock().now().to_msg(),
                )
            )

    """ === class functions === """

    def __call__(self, *args, **kwargs):
        with self.lock:
            self.dynamics_evaluation_callback()

    def __str__(self):
        """String representation of the dynamics evaluator."""
        pass

    def __repr__(self):
        """Official string representation of the dynamics evaluator."""
        pass


import rclpy
from hybraut_models import HybridAutomaton
from rclpy.executors import MultiThreadedExecutor
import threading


def main():
    rclpy.init()

    executor = MultiThreadedExecutor(num_threads=2)
    mock_node = Node("mock_node")
    from hybraut_interfaces.msg import AutomatonStatus

    status_publisher = mock_node.create_publisher(
        msg_type=AutomatonStatus,
        topic="/automaton/status",
        qos_profile=qos_profile_system_default,
        callback_group=ReentrantCallbackGroup(),
    )

    executor.add_node(mock_node)

    thread = threading.Thread(target=executor.spin)
    thread.start()
    path = "/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml"
    import yaml

    with open(path, "r") as file:
        amdl_dict = yaml.safe_load(file)

    hybraut_model = HybridAutomaton.register_automaton(
        node=mock_node, amdl_dict=amdl_dict
    )

    state_tracker: EngineStateTracker = EngineStateTracker(
        node=mock_node, initial_mode=0, q_goals=[1]
    )

    hybraut_dynamic_evaluator = DynamicEvaluator(
        node=mock_node,
        automaton=hybraut_model,
        state_tracker=state_tracker,
        status_publisher=status_publisher,
    )

    def evaluate_dynamics():
        import time

        while True:
            hybraut_dynamic_evaluator()
            time.sleep(5.0)

    thread2 = threading.Thread(target=evaluate_dynamics)
    thread2.start()

    def increment_current_mode():
        import time

        while True:
            time.sleep(5.0)
            state_tracker.current_mode += 1
            print("incremented current mode")

    thread3 = threading.Thread(target=increment_current_mode)
    thread3.start()

    thread.join()

    executor.shutdown()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
