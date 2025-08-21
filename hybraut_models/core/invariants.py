# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines the InvariantBus, InvariantWrapper, and InvariantRegistry classes
for managing invariants in a robotic automaton system.
It includes functionality for evaluating invariants, publishing invariant events,
and managing a registry of invariant components.
"""

import logging
from dataclasses import dataclass
from typing import List, Type


from hybraut_interfaces.msg import InvariantEvaluationMSG, InvariantEvaluationsMSG

from hybraut_aci import InvariantInterface
from hybraut_models.core.component_interfaces import WrapperInterface
from hybraut_models.core.component_interfaces.registry_interface import (
    ComponentRegistry,
)
from hybraut_models.ctx.evaluation_context import EvaluationContext

from hybraut_models.exc import EvaluationException


logger = logging.getLogger(__name__)


@dataclass
class InvariantWrapper(WrapperInterface):
    """
    Wrapper for invariant components that evaluate conditions that must hold within a state.
    """

    component_class: Type[InvariantInterface]

    def __post_init_hook__(self):
        self.initialize()

    """ === access modifiers === """

    def get_invariant_name(self) -> str:
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

    """ === evaluation_functionality === """

    def _evaluate(self, context: EvaluationContext) -> InvariantEvaluationMSG:
        """"""
        if not self.is_initialized:
            raise RuntimeError("Component instance is None, call activate() first")

        msg: InvariantEvaluationMSG = InvariantEvaluationMSG()
        states = context.get_state_values(
            self.component_instance.get_state_input_spec_names()
        )
        component_info = self.component_instance.get_component_info()
        msg.invariant_name = component_info["class_name"]
        msg.invariant_description = component_info["description"]

        try:
            msg.holds = self.component_instance(**states)
        except Exception as e:
            msg.error = True
            msg.message = f"exception occured during invariant evaluation: '{str(e)}'"

        return msg

    """ === string representations === """

    def __str__(self):
        return (
            f"InvariantWrapper(name={self.name}, class={self.component_class.__name__})"
        )

    def __repr__(self):
        return (
            f"<InvariantWrapper name={self.name!r}, "
            f"class={self.component_class.__name__}, "
            f"initialized={self.is_initialized}>"
        )


class InvariantRegistry(ComponentRegistry["InvariantWrapper"]):
    """Registry specialized for managing Invariant components"""

    def __post_init__(self):
        self._component_type_name = "Invariant"
        super().__post_init__()

    """ === access modifiers === """

    def get_invariant_names(self):
        if self._components is None:
            return []
        return list(self._components.keys())

    def get_num_invariants(self):
        return self._components is not None and len(self._components) or 0

    def get_invariant_by_name(self, invariant_name: str) -> InvariantWrapper | None:
        if invariant_name in self._components.keys():
            return self._components[invariant_name]
        return None

    def get_invariants_by_names(
        self, invariant_names: List[str]
    ) -> List[InvariantWrapper]:
        return [
            self.get_invariant_by_name(name)
            for name in invariant_names
            if self.get_invariant_by_name(name) is not None
        ]

    """ === invariant evaluation functions === """

    def evaluate_invariant_by_name(
        self, invariant_name: str, ctx: EvaluationContext
    ) -> InvariantEvaluationMSG:
        """evaluate guard by name"""
        invariant = self.get_invariant_by_name(invariant_name)
        try:
            return invariant._evaluate(ctx)
        except Exception as e:
            logger.info(f"{str(e)}")
            raise EvaluationException(
                f"evaluation exception during 'evaluate_invariant_by_name': {str(e)}"
            )

    def evaluate_invariants_by_name(
        self, invariant_names: List[str], ctx: EvaluationContext
    ) -> List[InvariantEvaluationsMSG]:
        invariant_evaluations_msg: InvariantEvaluationsMSG = InvariantEvaluationsMSG(
            current_mode=ctx.current_mode, stamp=ctx.stamp
        )
        try:
            invariant_evaluation_msgs: List[InvariantEvaluationMSG] = []
            for invariant_name in invariant_names:
                invariant_evaluation_msgs.append(
                    self.evaluate_invariant_by_name(invariant_name, ctx)
                )

            error = False
            error_messages = []
            for invariant_evaluation in invariant_evaluation_msgs:
                if invariant_evaluation.error == True:
                    error = True
                    error_messages.append(invariant_evaluation.message)

            overall_holds = True
            for invariant_evaluation in invariant_evaluation_msgs:
                if not invariant_evaluation.holds:
                    overall_holds = False

            invariant_evaluations_msg.overall_holds = overall_holds
            invariant_evaluations_msg.error = error
            invariant_evaluations_msg.message = " ".join(error_messages)
        except Exception as e:
            invariant_evaluations_msg.error = True
            invariant_evaluations_msg.message = (
                f"Exception occured during invariant evaluation: '{str(e)}'"
            )

        return invariant_evaluations_msg

    """ === class functions === """

    @classmethod
    def _component_class(cls) -> Type[InvariantWrapper]:
        return InvariantWrapper

    """ === string representations === """

    def __str__(self):
        invariant_names = list(self._components.keys()) if self._components else []
        return (
            f"InvariantRegistry(num_invariants={len(invariant_names)}, "
            f"invariants={invariant_names})"
        )

    def __repr__(self):
        invariants_repr = []
        for name, invariant in (self._components or {}).items():
            invariant_type = getattr(
                invariant, "component_class", type(invariant)
            ).__name__
            invariants_repr.append(f"{name}: {invariant_type}")
        invariants_str = ", ".join(invariants_repr) if invariants_repr else "empty"
        return (
            f"<InvariantRegistry num_invariants={len(self._components or {})}, "
            f"invariants={{ {invariants_str} }}>"
        )


""" === local testing code below, not for production === """


def main():
    pass


if __name__ == "__main__":
    main()
