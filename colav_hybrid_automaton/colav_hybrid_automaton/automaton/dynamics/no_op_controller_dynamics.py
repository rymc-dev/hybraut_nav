from .dynamics import DynamicsABC
from typing import NamedTuple
from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsSpec, DynamicsField
from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsSpecBuilder


class NoOpControllerDynamics(DynamicsABC):

    _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

    def __call__(self, **state_kwargs):
        super.__call__(**state_kwargs)
        return self.create_output(
            velocity=0.0,
            yaw_rate=0.0
        )
