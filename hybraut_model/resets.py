# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides the ResetWrapper and ResetRegistry classes for managing resets in a robotic automaton system.
It includes functionality for loading resets from configuration, evaluating resets, and managing state updates.
It is designed to be used within the Hybraut ROS2 framework.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type


from hybraut_interfaces.msg import AutomatonReset, AutomatonResets

from hybraut_model.automaton_types.component_path import ComponentPath
from hybraut_aci import ResetInterface
from hybraut_model.component_interfaces.registry_interface import ComponentRegistry
from hybraut_model.component_interfaces.wrapper_interface import WrapperInterface

from hybraut_model.evaluation_context import EvaluationContext
from utils import now_to_ros_time_msg

# Set up module-level logger
logger = logging.getLogger(__name__)


@dataclass
class ResetWrapper(WrapperInterface):
    """
    ResetWrapper is a wrapper for reset components that encapsulates the logic for evaluating resets
    and managing state updates. It is designed to be used within the Hybraut ROS2
    framework and provides a standardized interface for reset components.
    """

    def _evaluate(self, ctx: EvaluationContext):
        if not self._is_initialized:
            raise RuntimeError("can not evaluate uninitialized reset")

        states = ctx.get_state_values(
            self._component_instance.get_state_input_spec_names()
        )
        outputs = self._component_instance(**states)  # dict of key: output_value
        target_states = ctx.get_states(list(outputs.keys()))

        for target_state_key, target_state_value in target_states.items():
            target_state_value.state_bus.publish_state(outputs[target_state_key])

        # return only key -> output_value mapping
        return {key: outputs[key] for key in outputs}

        # need to publish the state updates for the correlating topics from the state registry

    def __post_init_hook__(self):
        self.initialize()


class ResetRegistry(ComponentRegistry["ResetWrapper"]):
    """
    ResetRegistry manages a collection of ResetWrapper components.
    It provides methods to load resets from configuration, evaluate resets by name,
    and retrieve reset names and components.
    It is designed to be used within the Hybraut ROS2 framework.
    """

    def __post_init__(self):
        self._component_type_name = "Reset"
        super().__post_init__()

    def get_reset_names(self):
        if self._components is None:
            return []
        return list(self._components.keys())

    def get_reset_by_name(self, reset_name: str):
        if reset_name in self._components.keys():
            return self._components[reset_name]

    def evaluate_reset_by_name(self, reset_name: str, ctx: EvaluationContext):
        """evalute reset by name"""
        reset = self.get_reset_by_name(reset_name)
        try:
            reset._evaluate(ctx)
        except Exception as e:
            logger.info(f"{str(e)}")

    def evaluate_resets_by_names(self, reset_names: List[str], ctx: EvaluationContext):
        """evaluate resets by name"""
        for reset_name in reset_names:
            self.evaluate_reset_by_name(reset_name, ctx)

    @classmethod
    def _component_class(cls) -> Type[ResetWrapper]:
        return ResetWrapper


"""main function to test the ResetRegistry and ResetWrapper functionality, not for production use"""


def main():
    reset_dict = {
        "battery_level_reset": {
            "module": "automaton_models.common_behaviours.resets.battery_level_reset",
            "class_name": "BatteryLevelReset",
            "configuration": {
                "low_battery_threshold": 30.0,
                "critical_battery_threshold": 5.0,
                "power_save_factor": 20.0,
            },
        }
    }
    import threading

    registry: ResetRegistry = ResetRegistry.load_reset_registry_from_amdl(
        reset_dict=reset_dict
    )
    # registry.activate_components(node)

    states = {
        "power_save_mode": {
            "topic": "/state/power_save_mode",
            "description": "Pose of the agent including position and orientation.",
            "type": {"pkg": "std_msgs.msg", "msg": "Bool"},
        },
        "max_performance_factor": {
            "topic": "/state/max_performance_factor",
            "description": "Pose of the agent including position and orientation.",
            "type": {"pkg": "std_msgs.msg", "msg": "Float64"},
        },
        "battery_status": {
            "topic": "/state/battery_status",
            "description": "Pose of the agent including position and orientation.",
            "type": {"pkg": "std_msgs.msg", "msg": "Int32"},
        },
        "return_to_base_required": {
            "topic": "/state/return_to_base_required",
            "description": "Pose of the agent including position and orientation.",
            "type": {"pkg": "std_msgs.msg", "msg": "Bool"},
        },
        "battery_level": {
            "topic": "/state/battery_level",
            "description": "Pose of the agent including position and orientation.",
            "type": {"pkg": "std_msgs.msg", "msg": "Float64"},
            "params": {"update_hz": 10.0, "timeout_sec": 0.5},
        },
        "current_power_mode": {
            "topic": "/state/current_power_mode",
            "description": "current power mode.",
            "type": {"pkg": "std_msgs.msg", "msg": "Int32"},
            "params": {"update_hz": 10.0, "timeout_sec": 0.5},
        },
    }
    from hybraut_model.states import StateRegistry

    state_registry = StateRegistry.load_state_registry_from_amdl(states_dict=states)
    # state_registry._components['battery_level'].current_state = Float64(_data=80.5)
    # state_registry._components['current_power_mode'].current_state = Int32(_data=2)
    from builtin_interfaces.msg import Time

    evaluation_context = EvaluationContext(
        states=state_registry, current_mode=0, stamp=Time(), metadata={}
    )

    reset_names = registry.get_reset_names()
    resets = registry.evaluate_resets_by_names(reset_names, evaluation_context)
    print(registry.get_reset_names())


if __name__ == "__main__":
    main()
