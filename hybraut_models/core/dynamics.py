# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dynamics class for containing the passive guard components of the automaton.
"""


import logging
from dataclasses import dataclass
from typing import Type, Dict, Any

from hybraut_interfaces.msg import AutomatonDynamicsEvaluation
from hybraut_aci import DynamicsInterface
from hybraut_aci.core.dynamics_interface import DynamicsInterface

from hybraut_models.ctx.evaluation_context import EvaluationContext
from hybraut_models.core.component_interfaces.wrapper_interface import WrapperInterface
from hybraut_models.core.component_interfaces.registry_interface import (
    ComponentRegistry,
)
from hybraut_models.ldr.component_path import ComponentPath
from hybraut_models.ldr.msg_type import MsgType
import json
from typing import List

from typing import Tuple
from rosidl_runtime_py import message_to_ordereddict

from dataclasses import field

logger = logging.getLogger(__name__)


@dataclass
class DynamicsWrapper(WrapperInterface):
    """
    wrapper for a instance of dynamics implementation
    """

    output_topic: str = field(init=True, default=None)
    output_msg_type: Type = field(init=True, default=None)
    component_class: Type[DynamicsInterface]

    def __post_init_hook__(self):
        self.initialize()

    """ === access modifiers === """

    def get_dynamic_name(self) -> str:
        return self.name

    def get_output_topic(self):
        return self.output_topic

    def get_output_msg_type(self):
        return self.output_msg_type

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

    """ === evaluation function === """

    def _evaluate(
        self, ctx: EvaluationContext
    ) -> Tuple[Any, AutomatonDynamicsEvaluation]:
        """
        Evaluate the current dynamics for the automaton.

        This method:
        1. Collects the required state inputs from the given `ctx`.
        2. Executes the dynamics component to produce a control command (`cmd`).
        3. Creates an `AutomatonDynamicsEvaluation` message containing
            descriptive and debugging information about the evaluation,
            including a JSON-encoded representation of the command.

        Returns:
            Tuple[Any, AutomatonDynamicsEvaluation]:
                - The control command object (type depends on the dynamics output type).
                - An `AutomatonDynamicsEvaluation` message for logging/diagnostics.

        Raises:
            RuntimeError: If the dynamics component is not initialized.
        """
        if not self.is_initialized:
            raise RuntimeError("Component instance is None. Call activate first.")

        # Prepare the debug/introspection message
        msg = AutomatonDynamicsEvaluation()
        msg.current_mode = ctx.current_mode
        msg.dynamic_name = self.component_instance.get_component_name()
        msg.dynamic_description = self.component_instance.get_component_description()
        msg.dynamic_output_topic = self.get_output_topic()

        cmd = None
        try:
            # Gather required state inputs for this dynamics
            state_names = self.component_instance.get_state_input_spec_names()
            states = ctx.get_state_values(state_names)

            # Execute the dynamics to produce the command
            cmd = self.component_instance(**states)

            # Serialize the command to JSON for debugging
            msg.dynamic_output_str = json.dumps(message_to_ordereddict(cmd))
        except Exception as e:
            msg.error = True
            msg.message = f"Exception occurred during dynamics evaluation: {e!r}"

        return cmd, msg

    def __str__(self):
        return (
            f"DynamicsWrapper(name={self.name}, "
            f"class={self.component_class.__name__}, "
            f"output_topic={self._output_topic}, "
            f"initialized={self.is_initialized})"
        )

    def __repr__(self):
        return (
            f"<DynamicsWrapper name={self.name!r}, "
            f"class={self.component_class.__name__}, "
            f"output_topic={self._output_topic!r}, "
            f"output_msg_type={getattr(self._output_msg_type, '__name__', self._output_msg_type)}, "
            f"initialized={self.is_initialized}>"
        )


class DynamicsRegistry(ComponentRegistry["DynamicsInterface"]):
    """Registry specialized for managing dynamics"""

    def __post_init__(self):
        self._component_type_name = "Dynamics"
        super().__post_init__()

    def get_num_dynamics(self):
        return len(self._components)

    def get_dynamics_names(self):
        if self._components is None:
            return []

        return list(self._components.keys())

    def get_dynamics_by_name(self, dynamics_name: str):
        if dynamics_name in self._components.keys():
            return self._components[dynamics_name]

    def get_dynamics_by_names(self, dynamic_names: List[str]):
        dynamics = {}
        for dynamic_name in dynamic_names:
            dynamics[dynamic_name] = self.get_dynamics_by_name(dynamic_name)
        return dynamics

    def evaluate_dynamics_by_name(
        self, dynamics_name: str, ctx: EvaluationContext
    ) -> Tuple[Any, AutomatonDynamicsEvaluation]:
        dynamics = self.get_dynamics_by_name(dynamics_name)
        try:
            cmd, dynamics_evaluation = dynamics._evaluate(ctx)
            dynamics_evaluation.dynamic_name = dynamics_name
            return cmd, dynamics_evaluation
        except Exception as e:
            logger.info(f"{str(e)}")

    @classmethod
    def _component_class(cls) -> Type[DynamicsWrapper]:
        return DynamicsWrapper


"""main is a test function, which is not for use within production"""


def main():

    import threading
    from hybraut_models.ctx.evaluation_context import EvaluationContext
    from builtin_interfaces.msg import Time
    from hybraut_models.core.states import StateRegistry

    dynamics_name = "pid_controller"

    dynamics_dict = {
        "pid_controller": {
            "module": "hybraut_common_behaviours.dynamics",
            "class_name": "PIDControllerDynamics",
            "configuration": {
                "control_frequency": 100,
                "max_velocity": 30.0,
                "derivative_filter_alpha": 0.1,
                "integral_max": 0.2,
                "target_velocity": 25.0,  # updated cruise speed
                "yaw_kp": 0.3,  # gentle heading proportional gain
                "yaw_ki": 0.01,  # small integral for smooth correction
                "yaw_kd": 0.05,  # small derivative gain to damp oscillations
                "vel_kp": 0.5,  # moderate velocity proportional gain
                "vel_ki": 0.05,  # small integral to avoid windup
                "vel_kd": 0.05,  # small derivative for smooth velocity changes
                "error_tolerance": 0.01,  # precision in heading error
                "max_yaw_rate": 0.1,  # limit yaw rate to gentle turns
            },
            "output": {
                "topic": "/cmd_vel",
                "type": {"pkg": "geometry_msgs.msg", "msg": "Twist"},
            },
        }
    }

    states = {
        "agent_state": {
            "topic": "/state/agent",
            "description": "State of the agent including position, velocity and heading.",
            "type": {"pkg": "colav_interfaces.msg", "msg": "AgentState"},
        },
        "waypoints_state": {
            "topic": "/state/waypoints",
            "description": "State of the waypoints including current waypoint and virtual waypoints.",
            "type": {"pkg": "colav_interfaces.msg", "msg": "WaypointsState"},
        },
    }

    state_registry = StateRegistry.load_state_registry_from_amdl(states_dict=states)

    evaluation_context = EvaluationContext(
        states=state_registry,
        current_mode=1,
        stamp=Time(),
        metadata={},
        guard_registry=None,
        reset_registry=None,
        invariant_registry=None,
    )

    dynamics: DynamicsRegistry = DynamicsRegistry.load_dynamics_registry_from_amdl(
        dynamics_dict=dynamics_dict
    )
    cmd, dynamic_evaluation = dynamics.evaluate_dynamics_by_name(
        "pid_controller", evaluation_context
    )

    print(cmd)
    print(dynamic_evaluation)


if __name__ == "__main__":
    main()
