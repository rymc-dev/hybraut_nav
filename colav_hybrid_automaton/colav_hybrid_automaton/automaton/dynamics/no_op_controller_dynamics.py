from .dynamics import DynamicsABC
from typing import NamedTuple
from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsSpec, DynamicsField


class NoOpControllerDynamics(DynamicsABC):

    _dynamic_output_spec: DynamicsSpec = (
        DynamicsSpec("AutomatonCMD", description="Automaton outputs for hydrofoil")
        .add_field("velocity", float, unit="m/s", description="Velocity in meters per second")
        .add_field("yaw_rate", float, unit="rad/s", description="Yaw rate in radians per second")
    ).create_dataclass()

    def __call__(self, **state_kwargs):
        super.__call__(**state_kwargs)
        output = self._dynamic_output_spec(velocity=0.0, yaw_rate=0.0)
        return output
