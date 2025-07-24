from automaton_models.hybrid.aci_interfaces import DynamicsInterface
from automaton_models.hybrid.aci_interfaces.dynamics_interface import DynamicsSpecBuilder


class NoOpControllerDynamics(DynamicsInterface):

    _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

    def __call__(self, **state_kwargs):
        super.__call__(**state_kwargs)
        return self.create_output(
            velocity=0.0,
            yaw_rate=0.0
        )

if __name__ == '__main__':
    dynamics: DynamicsInterface = NoOpControllerDynamics()
    dynamic_output = dynamics.__call__()

    print (dynamic_output)