# !/usr/bin/python3
#
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

from typing import List

from hybraut_utils import now_to_ros_time_msg

from .core.guards import GuardRegistry
from .core.invariants import InvariantRegistry
from .core.modes import ModeRegistry, Mode
from .core.resets import ResetRegistry
from .core.dynamics import DynamicsRegistry
from .core.states import StateRegistry
from .core.transitions import TransitionRegistry

from .ctx.evaluation_context import EvaluationContext

from hybraut_interfaces.msg import TransitionEvaluationsMSG
from hybraut_interfaces.msg import InvariantEvaluationsMSG
from hybraut_interfaces.msg import AutomatonDynamicsEvaluation
from hybraut_interfaces.msg import AutomatonResets
from hybraut_nav_tactical.tactical_models.const import ModeConnectivity

from typing import Tuple, Any


from .exc import EvaluationException


class HybridAutomaton:
    """
    HybridAutomaton class is a passive entity model representation
    of a hybrid automaton, it contains functions for evaluation of the hybrid automaton
    and contains non active details regarding the automaton.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        initial_mode: int,
        goal_modes: List[int],
        mode_registry: ModeRegistry,
        state_registry: StateRegistry,
        transition_registry: TransitionRegistry,
        guard_registry: GuardRegistry,
        reset_registry: ResetRegistry,
        dynamic_registry: DynamicsRegistry,
        invariant_registry: InvariantRegistry,
        mode_connectivity: ModeConnectivity = ModeConnectivity.WEAK,  # TODO: Implement functionality in the future for different connectivity types, atm we just use WEAK connectivity
    ):
        self._name = name
        self._description = description
        self._version = version
        self._initial_mode = initial_mode
        self._goal_modes = goal_modes
        self._mode_registry = mode_registry
        self._state_registry = state_registry
        self._transition_registry = transition_registry
        self._guard_registry = guard_registry
        self._reset_registry = reset_registry
        self._dynamic_registry = dynamic_registry
        self._invariant_registry = invariant_registry
        self._mode_connectivity = mode_connectivity

    """ === access modifiers === """

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._description

    def get_version(self) -> str:
        return self._version

    def get_initial_mode(self) -> int:
        return self._initial_mode

    def get_goal_modes(self) -> List[int]:
        return self._goal_modes

    def get_mode_connectivity(self) -> ModeConnectivity:
        return self._mode_connectivity

    """ === utility functions === """

    def _generate_evaluation_context(self, current_mode_id: int) -> EvaluationContext:
        """
        utility function for hybrid_automata for generating
        """
        return EvaluationContext(
            current_mode=current_mode_id,
            states_registry=self._state_registry,
            stamp=now_to_ros_time_msg(),
            mode_registry=self._mode_registry,
            transition_registry=self._transition_registry,
            guard_registry=self._guard_registry,
            reset_registry=self._reset_registry,
            invariant_registry=self._invariant_registry,
            metadata={},
        )

    """ === automaton evaluation functions === """

    def evaluate_transitions(self, mode_id: int) -> TransitionEvaluationsMSG:
        """performs transition evaluations for the current mode"""

        if not self._mode_registry.is_mode(mode_id):
            raise RuntimeError(
                f"invalid mode received: {mode_id}, not valid mode for evaluation."
            )

        try:
            current_mode: Mode = self._mode_registry.get_mode(mode_id)
            possible_transitions = current_mode.get_transition_refs()
            ctx = self._generate_evaluation_context(mode_id)
            transition_evaluations: TransitionEvaluationsMSG = (
                self._transition_registry.evaluate_transitions(
                    transitions=possible_transitions, ctx=ctx
                )
            )

            return transition_evaluations

        except EvaluationException as e:
            raise EvaluationException(
                f"Error evaluating transitions for mode {mode_id}: {str(e)}"
            ) from e
        except Exception as e:
            raise EvaluationException(
                f"Unexpected error evaluating transitions for mode {mode_id}: {str(e)}"
            ) from e

    def evaluate_invariants(self, mode_id: int) -> InvariantEvaluationsMSG:
        """performs invariant evaluations for the current mode"""

        if not self._mode_registry.is_mode(mode_id):
            raise RuntimeError(
                f"invalid mode received: {mode_id}, not valid mode for evaluation."
            )

        try:
            current_mode: Mode = self._mode_registry.get_mode(mode_id)
            invariant_names = current_mode.get_invariant_refs()
            ctx = self._generate_evaluation_context(mode_id)
            invariant_evaluations: InvariantEvaluationsMSG = (
                self._invariant_registry.evaluate_invariants_by_name(
                    invariant_names, ctx
                )
            )

            return invariant_evaluations
        except EvaluationException as e:
            raise EvaluationException(
                f"Error evaluating invariants for mode {mode_id}: {str(e)}"
            ) from e
        except Exception as e:
            raise EvaluationException(
                f"Unexpected error evaluating invariants for mode {mode_id}: {str(e)}"
            ) from e

    def evaluate_dynamics(
        self, mode_id: int
    ) -> Tuple[Any, AutomatonDynamicsEvaluation]:
        """performs dynamics evaluations for the current mode"""

        if not self._mode_registry.is_mode(mode_id):
            raise RuntimeError(
                f"invalid mode received: {mode_id}, not valid mode for evaluation."
            )

        try:
            current_mode: Mode = self._mode_registry.get_mode(mode_id)
            dynamics_names = current_mode.get_dynamics_ref()
            ctx = self._generate_evaluation_context(mode_id)
            cmd, dynamics_evaluation = self._dynamic_registry.evaluate_dynamics_by_name(
                dynamics_names, ctx
            )

            return cmd, dynamics_evaluation

        except EvaluationException as e:
            raise EvaluationException(
                f"Error evaluating dynamics for mode {mode_id}: {str(e)}"
            ) from e
        except Exception as e:
            raise EvaluationException(
                f"Unexpected error evaluating dynamics for mode {mode_id}: {str(e)}"
            ) from e

    """ === Application function - state-changing write functions === """

    def apply_resets(self, mode_id: int, reset_names: List[str]) -> AutomatonResets:
        """execute resets to states"""
        # TODO: Need to finish this.
        if not self._mode_registry.is_mode(mode_id):
            raise RuntimeError(
                f"invalid mode received: {mode_id}, not valid mode for evaluation."
            )

        current_mode: Mode = self._mode_registry.get_mode(mode_id)
        # validate the reset names are valid for the current mode
        ctx = self._generate_evaluation_context(mode_id)
        resets = self._reset_registry.get_components_by_names(reset_names)
        return

    """ === string representations === """

    def __repr__(self) -> str:
        return (
            f"HybridAutomaton("
            f"name={self._name!r}, "
            f"version={self._version!r}, "
            f"initial_mode={self._initial_mode!r}, "
            f"goal_modes={self._goal_modes!r}, "
            f"mode_registry={self._mode_registry!r}, "
            f"state_registry={self._state_registry!r}, "
            f"transition_registry={self._transition_registry!r}, "
            f"guard_registry={self._guard_registry!r}, "
            f"reset_registry={self._reset_registry!r}, "
            f"dynamic_registry={self._dynamic_registry!r}, "
            f"invariant_registry={self._invariant_registry!r})"
        )

    def __str__(self) -> str:
        lines = [
            f"HybridAutomaton: {self._name} (v{self._version})",
            f"Description: {self._description}",
            f"Initial mode: {self._initial_mode}",
            f"Goal modes: {self._goal_modes if self._goal_modes else 'None'}",
            "",
            f"Modes: {repr(self._mode_registry._modes)}",
            f"States: {repr(self._state_registry)}",
            f"Transitions: {repr(self._transition_registry)}",
            f"Guards: {repr(self._guard_registry)}",
            f"Resets: {repr(self._reset_registry)}",
            f"Dynamics: {repr(self._dynamic_registry)}",
            f"Invariants: {repr(self._invariant_registry)}",
        ]
        return "\n".join(lines)


""" === the code below is purely for testing and not to be used in production ==="""


def main():
    # --- mock registry classes for testing ---
    class MockRegistry:
        def __init__(self, name, items=None):
            self._name = name
            self._items = items if items is not None else []

        def __len__(self):
            return len(self._items)

        def __repr__(self):
            return f"<MockRegistry {self._name} with {len(self)} items>"

    # Specialized mock for modes (since __str__ expects `_modes`)
    class MockModeRegistry(MockRegistry):
        def __init__(self, items=None):
            super().__init__("ModeRegistry", items)
            self._modes = items if items is not None else []

    # --- create a sample HybridAutomaton instance ---
    mode_registry = MockModeRegistry(items=["mode1", "mode2"])
    state_registry = MockRegistry("StateRegistry", items=["s1", "s2", "s3"])
    transition_registry = MockRegistry("TransitionRegistry", items=["t1"])
    guard_registry = MockRegistry("GuardRegistry", items=["g1", "g2"])
    reset_registry = MockRegistry("ResetRegistry", items=["r1"])
    dynamic_registry = MockRegistry("DynamicRegistry", items=["d1", "d2"])
    invariant_registry = MockRegistry("InvariantRegistry", items=["inv1"])

    automaton = HybridAutomaton(
        name="TestAutomaton",
        description="A simple test automaton for debugging.",
        version="0.1",
        initial_mode=0,
        goal_modes=[1],
        mode_registry=mode_registry,
        state_registry=state_registry,
        transition_registry=transition_registry,
        guard_registry=guard_registry,
        reset_registry=reset_registry,
        dynamic_registry=dynamic_registry,
        invariant_registry=invariant_registry,
    )

    # --- test __repr__ and __str__ ---
    print(">>> REPR:")
    print(repr(automaton))
    print("\n>>> STR:")
    print(str(automaton))


if __name__ == "__main__":
    main()
