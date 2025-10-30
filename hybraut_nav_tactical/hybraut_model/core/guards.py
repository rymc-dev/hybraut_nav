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
from hybraut_nav_tactical.tactical_models.ldr.component_path import ComponentPath
from hybraut_nav_tactical.tactical_models.core.component_interfaces import WrapperInterface
from hybraut_nav_tactical.tactical_models.core.component_interfaces.registry_interface import (
    ComponentRegistry,
)
from hybraut_nav_tactical.tactical_models.ctx.evaluation_context import EvaluationContext
from hybraut_nav_tactical.tactical_models.exc import EvaluationException

logger = logging.getLogger(__name__)


@dataclass
class GuardWrapper(WrapperInterface):
    """
    Wrapper for guard components that evaluate transition conditions.
    """

    component_class: Type[GuardInterface]

    def __post_init_hook__(self):
        self.initialize()

    """ === access modifiers === """

    def get_guard_name(self) -> List[str]:
        return self.name

    def get_initialization_configuration_names_and_types(self):
        names: str = self.component_class.get_init_input_spec_names()
        types: Type = self.component_class.get_init_input_spec_types()

        # need to combine this
        return {name: types[i] for i, name in enumerate(names)}

    def get_state_configuration_names_and_types(self):
        names: str = self.component_class.get_state_input_spec_names()
        types: Type = self.component_class.get_state_input_spec_types()

        # need to combine this
        return {name: types[i] for i, name in enumerate(names)}

    def get_initialization_configuration(self):
        return self.configuration

    """ === TODO: update initialization configuration functions === """

    """ === evaluation === """

    def _evaluate(self, context: EvaluationContext) -> GuardEvaluationMSG:
        """
        Evaluates the guard condition using the component instance.
        """

        if not self.is_initialized:
            raise RuntimeError("Component instance is None. Call activate() first.")

        try:
            msg: GuardEvaluationMSG = GuardEvaluationMSG()
            state_names = self.component_instance.get_state_input_spec_names()
            states = context.get_state_values(state_names)
            msg.guard_name = self.get_guard_name()

            try:
                msg.guard_evaluation = self.component_instance(**states)
            except Exception as e:
                msg.error = True
                msg.message = f"exception occured during guard evaluation: '{str(e)}'"

            return msg
        except Exception as e:
            raise EvaluationException(f"Error evaluating guard '{self.name}': {str(e)}")

    """ === string representations === """

    def __str__(self):
        return f"GuardWrapper(name={self.name}, class={self.component_class.__name__})"

    def __repr__(self):
        return (
            f"<GuardWrapper name={self.name!r}, "
            f"class={self.component_class.__name__}, "
            f"initialized={self.is_initialized}>"
        )


class GuardRegistry(ComponentRegistry["GuardWrapper"]):
    """Registry specialized for managing guard components"""

    def __post_init__(self):
        self._component_type_name = "Guard"
        super().__post_init__()

    """ === access modifiers === """

    def get_num_guards(self):
        return len(self._components) if self._components is not None else 0

    def get_guard_names(self):
        if self._components is None:
            return []
        return list(self._components.keys())

    def get_guard_by_name(self, guard_name: str):
        if guard_name in self._components.keys():
            return self._components[guard_name]

    def get_guards_by_names(self, guard_names: List[str]) -> List[GuardWrapper]:
        guards = []
        for guard_name in guard_names:
            guard = self.get_guard_by_name(guard_name)
            if guard:
                guards.append(guard)
        return guards

    """ === guard evaluation functions === """

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

    """ === string representations === """

    def __str__(self):
        guard_names = self.get_guard_names()
        return (
            f"GuardRegistry(num_guards={self.get_num_guards()}, guards={guard_names})"
        )

    def __repr__(self):
        guards_repr = []
        for name, guard in (self._components or {}).items():
            guard_type = getattr(guard, "component_class", type(guard)).__name__
            guards_repr.append(f"{name}: {guard_type}")
        guards_str = ", ".join(guards_repr) if guards_repr else "empty"
        return f"<GuardRegistry num_guards={self.get_num_guards()}, guards={{ {guards_str} }}>"


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
    from hybraut_nav_tactical.tactical_models.core.states import StateRegistry

    state_registry = StateRegistry.load_state_registry_from_amdl(states_dict=states)

    from hybraut_nav_tactical.tactical_models.ctx.evaluation_context import EvaluationContext
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
