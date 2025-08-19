# !/usr/bin/python3

"""
Hybrid Automaton Implementation

This module implements a Hybrid Automaton that can be used to model systems with discrete and continuous dynamics
and transitions between different modes. It provides methods for evaluating transitions, invariants, and dynamics,
as well as performing resets. The automaton is defined by its states, guards, resets, dynamics, invariants, transitions, and modes.
It also includes a method for registering the automaton from an AMDL (Automaton Modeling Description Language) dictionary.
This code is part of the Hybraut project, which aims to provide a framework for hybrid automata modeling in robotics and other domains.
The automaton can be used to evaluate the current state of the system, check for valid transitions, and apply resets as needed.
It is designed to be flexible and extensible, allowing for the addition of new states, guards, resets, dynamics, invarints, transitions, and modes.
The automaton can be integrated with ROS 2 for real-time applications, enabling the evaluation of hybrid systems in a robotic context.
This module is intended to be used as part of a larger Hybraut framework, which includes various components for hybrid automata modeling and
evaluation.
"""

from dataclasses import dataclass, field
from typing import List

from utils import now_to_ros_time_msg

from hybraut_models.core.guards import GuardRegistry
from hybraut_models.core.invariants import InvariantRegistry
from hybraut_models.core.modes import ModeRegistry, Mode
from hybraut_models.core.resets import ResetRegistry
from hybraut_models.core.dynamics import DynamicsRegistry
from hybraut_models.core.states import StateRegistry
from hybraut_models.core.transitions import TransitionRegistry

from hybraut_models.context.evaluation_context import EvaluationContext

from hybraut_interfaces.msg import TransitionEvaluationsMSG
from hybraut_interfaces.msg import InvariantEvaluationsMSG
from hybraut_interfaces.msg import AutomatonDynamicsEvaluation
from typing import Tuple, Any


from hybraut_models.exceptions import EvaluationException


@dataclass
class HybridAutomaton:
    """
    Hybrid Automaton class that encapsulates the structure and behavior of a passive Hybrid Automaton
    """

    _name: str = field(init=True)
    _description: str = field(init=True)
    _version: str = field(init=True)

    _initial_mode: int = field(init=True)
    _goal_modes: List[int] = field(init=True)

    _modes: ModeRegistry = field(init=True)
    _states: StateRegistry = field(init=True)
    _guards: GuardRegistry = field(init=True)
    _resets: ResetRegistry = field(init=True)
    _dynamics: DynamicsRegistry = field(init=True)
    _invariants: InvariantRegistry = field(init=True)
    _transitions: TransitionRegistry = field(init=True)

    def _generate_evaluation_context(self, current_mode_id: int) -> EvaluationContext:
        """
        utility function for hybrid_automata for generating
        """
        return EvaluationContext(
            current_mode=current_mode_id,
            states=self._states,
            stamp=now_to_ros_time_msg(),
            guard_registry=self._guards,
            reset_registry=self._resets,
            invariant_registry=self._invariants,
            metadata={},
        )

    def evaluate_transitions(self, current_mode_id: int) -> TransitionEvaluationsMSG:
        """performs transition evaluations for the current mode"""

        if not self._modes.is_mode(current_mode_id):
            raise RuntimeError(
                f"invalid mode received: {current_mode_id}, not valid mode for evaluation."
            )

        try:
            current_mode: Mode = self._modes.get_mode(current_mode_id)
            possible_transitions = current_mode.get_transition_refs()
            ctx = self._generate_evaluation_context(current_mode_id)
            transition_evaluations: TransitionEvaluationsMSG = (
                self._transitions.evaluate_transitions(
                    transitions=possible_transitions, ctx=ctx
                )
            )

            return transition_evaluations

        except EvaluationException as e:
            raise EvaluationException(
                f"Error evaluating transitions for mode {current_mode_id}: {str(e)}"
            ) from e
        except Exception as e:
            raise EvaluationException(
                f"Unexpected error evaluating transitions for mode {current_mode_id}: {str(e)}"
            ) from e

    def evaluate_invariants(self, current_mode_id: int) -> InvariantEvaluationsMSG:
        """performs invariant evaluations for the current mode"""

        if not self._modes.is_mode(current_mode_id):
            raise RuntimeError(
                f"invalid mode received: {current_mode_id}, not valid mode for evaluation."
            )

        try:
            current_mode: Mode = self._modes.get_mode(current_mode_id)
            invariant_names = current_mode.get_invariant_refs()
            ctx = self._generate_evaluation_context(current_mode_id)
            invariant_evaluations: InvariantEvaluationsMSG = (
                self._invariants.evaluate_invariants_by_name(invariant_names, ctx)
            )

            return invariant_evaluations
        except EvaluationException as e:
            raise EvaluationException(
                f"Error evaluating invariants for mode {current_mode_id}: {str(e)}"
            ) from e
        except Exception as e:
            raise EvaluationException(
                f"Unexpected error evaluating invariants for mode {current_mode_id}: {str(e)}"
            ) from e

    def evaluate_dynamics(
        self, current_mode_id: int
    ) -> Tuple[Any, AutomatonDynamicsEvaluation]:
        """performs dynamics evaluations for the current mode"""

        if not self._modes.is_mode(current_mode_id):
            raise RuntimeError(
                f"invalid mode received: {current_mode_id}, not valid mode for evaluation."
            )

        try:
            current_mode: Mode = self._modes.get_mode(current_mode_id)
            dynamics_names = current_mode.get_dynamics_ref()
            ctx = self._generate_evaluation_context(current_mode_id)
            cmd, dynamics_evaluation = self._dynamics.evaluate_dynamics_by_name(
                dynamics_names, ctx
            )

            return cmd, dynamics_evaluation

        except EvaluationException as e:
            raise EvaluationException(
                f"Error evaluating dynamics for mode {current_mode_id}: {str(e)}"
            ) from e
        except Exception as e:
            raise EvaluationException(
                f"Unexpected error evaluating dynamics for mode {current_mode_id}: {str(e)}"
            ) from e

    def perform_resets(self, current_mode_id: int, reset_names: List[str]):
        """execute resets to states"""
        # TODO: Need to finish this.
        if not self._modes.is_mode(current_mode_id):
            raise RuntimeError(
                f"invalid mode received: {current_mode_id}, not valid mode for evaluation."
            )

        current_mode: Mode = self._modes.get_mode(current_mode_id)
        # validate the reset names are valid for the current mode
        ctx = self._generate_evaluation_context(current_mode_id)
        resets = self._resets.get_components_by_names(reset_names)
        return


"""
the code below is purely for testing and not to be used in production
"""

if __name__ == "__main__":

    import rclpy
    from rclpy.executors import MultiThreadedExecutor
    from rclpy.node import Node
    import threading
    import yaml

    rclpy.init()
    executors = MultiThreadedExecutor(num_threads=2)

    node = Node("mock_node")
    executors.add_node(node)

    thread = threading.Thread(target=executors.spin)

    path = "/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml"
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    automaton: HybridAutomaton = HybridAutomaton.register_automaton(
        node=node, amdl_dict=data
    )

    try:
        transitions_evalutation = automaton.evaluate_transitions(current_mode_id=0)
        print(transitions_evalutation)
    except RuntimeError as e:
        print(str(e))
    except Exception as e:
        print(f"unexpected exception occured: {str(e)}")

    try:
        invariants_evaluation = automaton.evaluate_invariants(current_mode_id=0)
        print(invariants_evaluation)
    except RuntimeError as e:
        print(str(e))
    except Exception as e:
        print(f"unexpected excpetion occured: {str(e)}")

    try:
        cmd, dynamics_output = automaton.evaluate_dynamics(current_mode_id=0)
        print(f"cmd: {cmd}")
        print(dynamics_output)
    except RuntimeError as e:
        print(str(e))
        # print exception status unrecoverable
    except Exception as e:
        print(f"unexpected exception occured: {str(e)}")

    rclpy.shutdown()
