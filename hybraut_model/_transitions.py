# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the Transition class and TransitionRegistry for managing state transitions in a system.
It includes methods for evaluating transitions based on guard conditions, executing transitions, and loading transitions from configuration
files.
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Type

from hybraut_model.component_interfaces.registry_interface import ComponentRegistry
from hybraut_model.constants.urgency import UrgencyEnums
from hybraut_model._evaluation_context import EvaluationContext
from hybraut_model._guards import GuardWrapper

from hybraut_interfaces.msg import (
    GuardEvaluationMSG,
    TransitionEvaluationMSG,
    TransitionEvaluationsMSG,
)

from utils import now_to_ros_time_msg

# Set up module-level logger
logger = logging.getLogger(__name__)


@dataclass
class Transition:
    """
    Represents a state transition in the system.
    """

    _name: str = field(init=True)
    _target_mode: int = field(init=True)
    _guard_refs: List[str] = field(init=True)
    _reset_refs: List[str] = field(init=True, default=None)
    _urgency: UrgencyEnums = field(
        init=True, default_factory=lambda: UrgencyEnums.EAGER
    )  # EAGER urgency for transition means the transition occurs automatically.
    _metadata: Dict[str, Any] = field(init=True, default_factory=lambda: {})

    def __post_init__(self):
        pass

    def get_target_mode(self):
        return self._target_mode

    def get_guard_refs(self):
        return self._guard_refs

    def get_reset_refs(self):
        return self._reset_refs

    def get_urgency(self):
        return self._urgency

    def evaluate_transition(self, ctx: EvaluationContext):
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
            guards: List[GuardWrapper] = ctx.guard_registry.get_components_by_names(
                self._guard_refs
            )

            guard_evaluations = []
            for guard in guards:
                try:
                    eval: bool = guard._evaluate(ctx)
                except Exception as e:
                    msg.error = True
                    msg.message.append(f"guard evaluation failed: {str(e)}")
                if not eval:
                    msg._should_transition = False

            msg._expected_resets = self._reset_refs

        except Exception as e:
            msg.error = True
            msg.message = f"exception occured: {str(e)}"

        return msg

    @classmethod
    def load_transition_from_amdl(
        cls, transition_name: str, transition_value: Dict[str, Any]
    ):
        print(f"{transition_name}, {transition_value}")
        name = transition_name
        target_mode = transition_value["target_mode"]
        guard_ref = transition_value["guard"]
        reset_ref = transition_value.get("reset")
        urgency = transition_value.get("urgency")

        if urgency is None:
            return cls(
                _name=name,
                _target_mode=target_mode,
                _guard_refs=guard_ref,
                _reset_refs=reset_ref,
            )

        urgency = UrgencyEnums.EAGER

        return cls(
            _name=name,
            _target_mode=target_mode,
            _guard_refs=guard_ref,
            _reset_refs=reset_ref,
            _urgency=urgency,
        )

    def execute_transition(self, ctx: EvaluationContext):
        """
        This executes the transition, performing the reset and publishing the new mode.
        """
        pass


class TransitionRegistry(ComponentRegistry):
    """
    Registry for managing transitions in the system.
    It provides methods to evaluate transitions based on their guards, execute transitions,
    """

    _components: dict[str, Transition]

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

    @classmethod
    def register(
        cls: Type["ComponentRegistry"], config_dict: Dict[str, Any]
    ) -> Dict[str, Transition]:
        components = {}

        for name, conf in config_dict.items():
            try:
                component_cls = cls._component_class()
                component = component_cls.load_transition_from_amdl(
                    transition_name=name, transition_value=conf
                )
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to load component '{name}': {e}"
                )
                raise
        return components

    @classmethod
    def load_transition_registry_from_amdl(cls, transition_dict: dict):
        logging.info("Loading TransitionRegistry")
        transitions = cls.register(transition_dict)
        registry = cls(_components=transitions)
        logger.info(f"Created TransitionRegistry with {len(transitions)} transitions")

        return registry


""" === Main function for testing or running the module, not for production use === """


def main():
    pass


if __name__ == "__main__":
    main()
