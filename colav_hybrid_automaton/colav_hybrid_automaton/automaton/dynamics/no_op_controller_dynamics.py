from .dynamics import DynamicsABC
from typing import NamedTuple

class PIDDynamicsOutput(NamedTuple):
    velocity: float
    yaw_rate: float

class NoOpControllerDynamics(DynamicsABC):

    def __init__(self, **init_kwargs):
        super().__init__(PIDDynamicsOutput, **init_kwargs)

    def __call__(**state_kwargs):
        super.__call__(**state_kwargs)
        return PIDDynamicsOutput(velocity=0.0, yaw_rate=0.0)
