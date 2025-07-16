from automaton.core_interfaces import DynamicsABC
from automaton.core_interfaces.dynamics_abc import DynamicsSpecBuilder


class NoOpControllerDynamics(DynamicsABC):

    _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

    def __call__(self, **state_kwargs):
        super.__call__(**state_kwargs)
        return self.create_output(
            velocity=0.0,
            yaw_rate=0.0
        )

if __name__ == '__main__':
    dynamics: DynamicsABC = NoOpControllerDynamics()
    dynamic_output = dynamics.__call__()

    print (dynamic_output)