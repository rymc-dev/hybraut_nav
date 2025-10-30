# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the Transition class and TransitionRegistry for managing state transitions in a system.
It includes methods for evaluating transitions based on guard conditions, executing transitions, and loading transitions from configuration
files.
"""

from typing import Any, Dict, List, Type, Optional

from hybraut_nav_tactical.tactical_models.core.component_interfaces.registry_interface import (
    ComponentRegistry,
)
from hybraut_nav_tactical.tactical_models.const.urgency import UrgencyEnums
from hybraut_nav_tactical.tactical_models.ctx.evaluation_context import EvaluationContext
from hybraut_nav_tactical.tactical_models.core.guards import GuardWrapper

from hybraut_interfaces.msg import (
    GuardEvaluationMSG,
    TransitionEvaluationMSG,
    TransitionEvaluationsMSG,
)

from hybraut_utils import now_to_ros_time_msg


class Transition:
    """
    Represents a transition in the system, managing a specific transition
    managing it's guards reference, reset references urgency type and metadata
    """

    def __init__(
        self,
        name: str,
        target_mode: int,
        guard_refs: List[str],
        reset_refs: List[str],
        priority: int,
        urgency: Optional[UrgencyEnums] = UrgencyEnums.EAGER,
        metadata: Optional[Dict[str, Any]] = {},
    ):
        self._name = name
        self._target_mode = target_mode
        self._guard_refs = guard_refs
        self._reset_refs = reset_refs
        self._priority = priority
        self._urgency = urgency
        self._metadata = metadata

    """ === access modifiers === """

    def get_name(self):
        return self._name

    def get_target_mode(self):
        return self._target_mode

    def get_guard_refs(self):
        return self._guard_refs

    def get_reset_refs(self):
        return self._reset_refs

    def get_urgency(self):
        return self._urgency

    def get_metadata(self):
        return self._metadata

    def get_priority(self):
        return self._priority

    """ === utility functions === """

    def evaluate_transition(self, ctx: EvaluationContext) -> TransitionEvaluationMSG:
        """
        evaluates the guard condition for transition, if any
        return as true we get the reset refs and return for the priority
        transition
        """
        msg: TransitionEvaluationMSG = TransitionEvaluationMSG()
        msg.name = self._name
        msg.target_mode = self._target_mode
        msg._priority = self._priority
        msg._should_transition = True

        try:
            guards: List[GuardWrapper] = ctx.guard_registry.get_guards_by_names(
                self._guard_refs
            )

            guard_evaluations = []
            for guard in guards:
                try:
                    eval: GuardEvaluationMSG = guard._evaluate(ctx)
                    msg.guards.append(eval)
                except Exception as e:
                    msg.error = True
                    msg.message.append(f"guard evaluation failed: {str(e)}")
                if not eval.guard_evaluation:
                    msg._should_transition = False
                if eval.error:
                    msg.error = True
                    msg.message = f"guard evaluation failed: {str(e)}"

            msg._expected_resets = self._reset_refs

        except Exception as e:
            msg.error = True
            msg.message = f"exception occured: {str(e)}"

        return msg

    """ === string representations === """

    def __repr__(self):
        return (
            f"Transition(name={self._name!r}, target_mode={self._target_mode}, "
            f"guards={self._guard_refs}, resets={self._reset_refs}, urgency={self._urgency})"
        )

    def __str__(self):
        return f"Transition '{self._name}' -> Mode {self._target_mode} | Guards: {self._guard_refs} | Resets: {self._reset_refs} | Urgency: {self._urgency}"


class TransitionRegistry(ComponentRegistry):
    """
    Registry for managing transitions in the system.
    It provides methods to evaluate transitions based on their guards, execute transitions,
    """

    _components: dict[str, Transition]

    def get_transition_by_name(self, transition_name: str):
        return self._components.get(transition_name)

    def evaluate_transitions(
        self, transitions: Dict[int, str], ctx: EvaluationContext
    ) -> TransitionEvaluationsMSG:
        """
        Evaluate the given transitions based on their associated guards,
        and return a TransitionEvaluationsMSG summarizing the results.

        Args:
            transitions (Dict[int, str]): Mapping from priority to transition name.
            ctx (EvaluationContext): Context containing current mode and registries.

        Returns:
            TransitionEvaluationsMSG: Evaluation results for each transition.
        """
        transition_evaluations_msg = TransitionEvaluationsMSG(
            current_mode=ctx.current_mode, stamp=now_to_ros_time_msg()
        )
        if not isinstance(transitions, dict) or len(transitions) < 1:
            transition_evaluations_msg.message = "no transitions for this mode."
            return transition_evaluations_msg

        # Extract names and priorities, preserving order
        sorted_items = sorted(transitions.items())
        transition_names = [name for _, name in sorted_items]
        transition_priorities = [priority for priority, _ in sorted_items]

        # Get transition components
        transition_components: Dict[str, Transition] = self.get_components_by_names(
            transition_names
        )

        # Evaluate each transition
        for transition_name, priority in zip(transition_names, transition_priorities):
            transition = transition_components[transition_name]
            transition_msg = TransitionEvaluationMSG(
                name=transition_name,
                target_mode=transition._target_mode,
                priority=priority,
            )

            # Handle guard references (could be a list or single string)
            guard_refs = transition._guard_refs
            if not isinstance(guard_refs, list):
                guard_refs = [guard_refs]

            # Evaluate guards
            has_transition = False
            has_exception = False
            exception_messages = []

            guards: Dict[str, GuardWrapper] = (
                ctx.guard_registry.get_components_by_names(guard_refs)
            )
            for guard in guards.values():
                guard_eval: GuardEvaluationMSG = guard._evaluate(context=ctx)
                transition_msg.guards.append(guard_eval)

                if guard_eval.guard_evaluation:
                    has_transition = True
                if guard_eval.error:
                    has_exception = True
                    exception_messages.append(guard_eval.message)

            # Set overall transition result
            transition_msg.should_transition = has_transition
            transition_msg.expected_resets = (
                []
            )  # TODO: Fill in expected resets if needed
            transition_msg.error = has_exception
            transition_msg.message = "\n".join(exception_messages)

            transition_evaluations_msg.transition_evaluations.append(transition_msg)

        return transition_evaluations_msg

    @classmethod
    def _component_class(cls) -> Type[Transition]:
        return Transition

    """ === String Representations === """

    def __repr__(self):
        return f"TransitionRegistry({list(self._components.keys())})"

    def __str__(self):
        transitions_str = "\n".join(str(t) for t in self._components.values())
        return f"TransitionRegistry with {len(self._components)} transitions:\n{transitions_str}"


""" === Main function for testing or running the module, not for production use === """


def main():
    # Example usage of Transition and TransitionrRegistry

    transition_data = {
        "transition_1": {
            "target_mode": 2,
            "guard": ["guard_1", "guard_2"],
            "reset": ["reset_1"],
            "urgency": 1,  # EAGER urgency,
        },
        "transition_2": {
            "target_mode": 3,
            "guard": ["guard_3"],
            "reset": ["reset_2", "reset_3"],
            "urgency": 2,  # LAZY urgency
        },
    }

    transition_registry = TransitionRegistry.load_transition_registry_from_amdl(
        transition_data
    )

    print(f"string transition_registry representation: {transition_registry}\n")
    print(f"__repr__ transition_registry representation: {repr(transition_registry)}")


if __name__ == "__main__":
    main()
