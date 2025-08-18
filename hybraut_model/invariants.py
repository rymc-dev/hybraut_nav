# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines the InvariantBus, InvariantWrapper, and InvariantRegistry classes
for managing invariants in a robotic automaton system.
It includes functionality for evaluating invariants, publishing invariant events,
and managing a registry of invariant components.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type


from hybraut_interfaces.msg import InvariantEvaluationMSG, InvariantEvaluationsMSG

from hybraut_aci_interfaces import InvariantInterface
from hybraut_model.automaton_types.component_path import ComponentPath
from hybraut_model.component_interfaces import WrapperInterface
from hybraut_model.component_interfaces.registry_interface import ComponentRegistry
from hybraut_model.evaluation_context import EvaluationContext

from hybraut_model.exceptions import EvaluationException


logger = logging.getLogger(__name__)


@dataclass
class InvariantWrapper(WrapperInterface):
    """
    Wrapper for invariant components that evaluate conditions that must hold within a state.
    """

    _component_class: Type[InvariantInterface]

    def __post_init_hook__(self):
        self.initialize()

    def _evaluate(self, context: EvaluationContext) -> InvariantEvaluationMSG:
        """"""
        if not self._is_initialized:
            raise RuntimeError("Component instance is None, call activate() first")

        msg: InvariantEvaluationMSG = InvariantEvaluationMSG()
        states = context.get_state_values(
            self._component_instance.get_state_input_spec_names()
        )
        component_info = self._component_instance.get_component_info()
        msg.invariant_name = component_info["class_name"]
        msg.invariant_description = component_info["description"]
        try:
            msg.holds = self._component_instance(**states)
        except Exception as e:
            msg.error = True
            msg.message = f"exception occured during invariant evaluation: '{str(e)}'"

        return msg


class InvariantRegistry(ComponentRegistry["InvariantWrapper"]):
    """Registry specialized for managing Invariant components"""

    def __post_init__(self):
        self._component_type_name = "Invariant"
        super().__post_init__()

    def get_invariant_names(self):
        if self._components is None:
            return []
        return list(self._components.keys())

    def get_invariant_by_name(self, invariant_name: str):
        if invariant_name in self._components.keys():
            return self._components[invariant_name]

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

    @classmethod
    def _component_class(cls) -> Type[InvariantWrapper]:
        return InvariantWrapper


if __name__ == "__main__":

    invariant_name = "timeout_invariant"
    invariants_dict = {
        "timeout_invariant": {
            "module": "hybraut_common_behaviours.invariants",
            "class_name": "TimeoutInvariant",
            "configuration": {"timeout_sec": 10.0, "entry_time": 1.0},
        }
    }

    states = {
        "current_time": {
            "topic": "/state/current_time",
            "description": "the current time for the system",
            "type": {"pkg": "std_msgs.msg", "msg": "Float64"},
        }
    }
    from hybraut_model.states import StateRegistry
    from std_msgs.msg import Float64

    state_registry = StateRegistry.load_state_registry_from_amdl(states_dict=states)
    state_registry.get_components_by_names(["current_time"])[
        "current_time"
    ].update_state(Float64(data=0.0))
    from builtin_interfaces.msg import Time

    evaluation_context = EvaluationContext(
        states=state_registry,
        reset_registry=None,
        invariant_registry=None,
        guard_registry=None,
        current_mode=1,
        stamp=Time(),
        metadata={},
    )

    invariant_registry: InvariantRegistry = (
        InvariantRegistry.load_invariant_registry_from_amdl(
            invariants_dict=invariants_dict
        )
    )
    invariant_evaluations: List[InvariantEvaluationMSG] = (
        invariant_registry.evaluate_invariants_by_name(
            invariant_names=invariants_dict.keys(),
            ctx=evaluation_context,
        )
    )

    print(invariant_evaluations)
