# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
guards class for containing the passive guard components of the automaton.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Type

from hybraut_interfaces.msg import GuardEvaluationMSG
from hybraut_aci_interfaces import GuardInterface
from hybraut_model.automaton_types.component_path import ComponentPath
from hybraut_model.component_interfaces import WrapperInterface
from hybraut_model.component_interfaces.registry_interface import ComponentRegistry
from hybraut_model._evaluation_context import EvaluationContext
from hybraut_model.exceptions import EvaluationException

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

    @classmethod
    def load_guard_from_amdl(
        cls, guard_name: str, guard_dict: Dict[str, Any]
    ) -> "GuardWrapper":
        component_path = ComponentPath.load_component_from_famd(guard_dict)
        component_class = component_path.get_component_class()
        configuration = guard_dict.get("configuration", None)
        return cls(
            _name=guard_name,
            _component_class=component_class,
            _configuration=configuration,
        )


class GuardRegistry(ComponentRegistry["GuardWrapper"]):
    """Registry specialized for managing guard components"""

    def __post_init__(self):
        self._component_type_name = "Guard"
        super().__post_init__()

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

    @classmethod
    def register(cls, guard_dict: Dict[str, Any]) -> Dict[str, GuardWrapper]:
        components = {}
        for name, conf in guard_dict.items():
            try:
                component_cls = cls._component_class()
                component = component_cls.load_guard_from_amdl(
                    guard_name=name, guard_dict=conf
                )
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to import component '{name}': {e}"
                )

        return components

    @classmethod
    def load_guard_registry_from_amdl(
        cls, guard_dict: Dict[str, Any]
    ) -> "GuardRegistry":
        """generates the guard_registry from amdl"""
        logger.info("Loading GuardRegistry from 'amdl' configuration")
        guards = cls.register(guard_dict)
        registry = cls(_components=guards)
        logger.info(f"Created GuardRegistry with {len(guards)} guards")
        return registry


""" main function for testing the GuardRegistry, not for production use"""


def main():
    import rclpy
    from rclpy.node import Node
    import threading
    from rclpy.executors import MultiThreadedExecutor

    rclpy.init()
    node = Node("mock_node")
    executor = MultiThreadedExecutor(num_threads=2)
    thread = threading.Thread(target=executor.spin)
    thread.start()

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
    from hybraut_model._states import StateRegistry

    state_registry = StateRegistry.load_state_registry_from_amdl(
        node=node, states_dict=states
    )
    state_registry.activate_components(node)

    from hybraut_model._evaluation_context import EvaluationContext
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
    rclpy.shutdown()


if __name__ == "__main__":
    main()
