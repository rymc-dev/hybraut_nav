from .dynamics import Dynamics
from typing import NamedTuple

def NoOpControllerDynamics(Dynamics):
        
    class PIDDynamicsOutput(NamedTuple):
        velocity: float
        yaw_rate: float

    def __init__(self, **init_kwargs):
        super().__init__(PIDDynamicsOutput, **init_kwargs)

    def __call__(**state_kwargs):
        super.__call__(**state_kwargs)
        return PIDDynamicsOutput(velocity=0.0, yaw_rate=0.0)
