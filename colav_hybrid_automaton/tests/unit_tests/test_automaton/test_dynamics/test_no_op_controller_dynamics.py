import pytest
from colav_hybrid_automaton.automaton.dynamics import NoOpControllerDynamics, DynamicsABC

def test_no_op_controller_dynamics_comprehsensive():
    dynamics: DynamicsABC = NoOpControllerDynamics()

    assert dynamics.init_input_spec_names()== []
    assert dynamics.init_input_spec_types() == []
    
    assert dynamics.state_input_spec_names() == []
    assert dynamics.state_input_spec_types() == []

    assert dynamics.dynamic_output_spec_name() == 'AutomatonControlOutputs'
    assert type(dynamics.dynamic_output_spec_description()) == str
    assert dynamics.dynamic_output_spec_names() == ['velocity', 'yaw_rate']
    assert dynamics.dynamic_output_spec_types() == [float, float]
    assert dynamics.dynamic_output_spec_units() == ['m/s', 'rad/s']

    dynamics_outputs = dynamics.__call__()

    assert dynamics_outputs.velocity == 0.0
    assert dynamics_outputs.yaw_rate == 0.0 

if __name__ == '__main__':
    test_no_op_controller_dynamics_comprehsensive()