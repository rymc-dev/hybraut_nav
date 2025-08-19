# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
guards class for containing the passive guard components of the automaton.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Type

from hybraut_interfaces.msg import GuardEvaluationMSG
from hybraut_aci import GuardInterface
from hybraut_models.loaders.component_path import ComponentPath
from hybraut_models.component_interfaces import WrapperInterface
from hybraut_models.component_interfaces.registry_interface import ComponentRegistry
from hybraut_models.context.evaluation_context import EvaluationContext
from hybraut_models.exceptions import EvaluationException

logger = logging.getLogger(__name__)


@dataclass
class GuardWrapper(WrapperInterface):
    """
    Wrapper for guard components that evaluate transition conditions.
    """

    _component_class: Type[GuardInterface]

    def __post_init_hook__(self):
        self.initialize()

    def _evaluate(self, context: EvaluationContext) -> GuardEvaluationMSG:
        """
        Evaluates the guard condition using the component instance.
        """

        if not self._is_initialized:
            raise RuntimeError("Component instance is None. Call activate() first.")

        try:
            msg: GuardEvaluationMSG = GuardEvaluationMSG()
            state_names = self._component_instance.get_state_input_spec_names()
            states = context.get_state_values(state_names)
            component_info = self._component_instance.get_component_info()
            msg.guard_name = component_info["class_name"]

            try:
                msg.guard_evaluation = self._component_instance(**states)
            except Exception as e:
                msg.error = True
                msg.message = f"exception occured during guard evaluation: '{str(e)}'"

            return msg
        except Exception as e:
            raise EvaluationException(
                f"Error evaluating guard '{self._name}': {str(e)}"
            )


class GuardRegistry(ComponentRegistry["GuardWrapper"]):
    """Registry specialized for managing guard components"""

    def __post_init__(self):
        self._component_type_name = "Guard"
        super().__post_init__()

    def get_num_guards(self):
        return len(self._components) if self._components is not None else 0

    def get_guard_names(self):
        if self._components is None:
            return []
        return list(self._components.keys())

    def get_guard_by_name(self, guard_name: str):
        if guard_name in self._components.keys():
            return self._components[guard_name]

    def evaluate_guard_by_name(
        self, guard_name: str, ctx: EvaluationContext
    ) -> GuardEvaluationMSG:
        """evaluate guard by name"""
        guard = self.get_guard_by_name(guard_name)
        try:
            return guard._evaluate(ctx)
        except Exception as e:
            logger.info(f"{str(e)}")

    def evaluate_guards_by_name(
        self, guard_names: List[str], ctx: EvaluationContext
    ) -> List[GuardEvaluationMSG]:
        guard_evaluation_msgs = []
        for guard_name in guard_names:
            guard_evaluation_msgs.append(self.evaluate_guard_by_name(guard_name, ctx))

        return guard_evaluation_msgs

    @classmethod
    def _component_class(cls) -> Type[GuardWrapper]:
        return GuardWrapper


""" main function for testing the GuardRegistry, not for production use"""


def main():

    guard_dict = {
        "boolean_flag_guard": {
            "module": "automaton_models.common_behaviours.guards.boolean_flag_guard",
            "class_name": "BooleanFlagGuard",
            "configuration": {"expected_flag": True},
        }
    }

    states = {
        "flag_msg": {
            "topic": "/state/flag_msg",
            "description": "flag_msg.",
            "type": {"pkg": "std_msgs.msg", "msg": "Bool"},
        }
    }
    from hybraut_models.core.states import StateRegistry

    state_registry = StateRegistry.load_state_registry_from_amdl(states_dict=states)

    from hybraut_models.context.evaluation_context import EvaluationContext
    from builtin_interfaces.msg import Time

    evaluation_context = EvaluationContext(
        states=state_registry, current_mode=1, stamp=Time(), metadata={}
    )

    guard_registry: GuardRegistry = GuardRegistry.load_guard_registry_from_amdl(
        guard_dict
    )
    guard_evaluations: List[GuardEvaluationMSG] = (
        guard_registry.evaluate_guards_by_name(
            guard_names=guard_dict.keys(), ctx=evaluation_context
        )
    )

    print(guard_evaluations)


if __name__ == "__main__":
    main()
