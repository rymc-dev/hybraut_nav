"""
Test class for NoOpControllerDynamics an implementation of the Abstract Dynamics ABC for COLAV hybrid automaton control modes fallback.

In this class we utilize NoOpControllerDynamics to test 
the underlying functionalities for this abstract class to enusre it is working 
as expected through the lifecycle of build and runtime
"""

import pytest
from nodes.dynamics import NoOpControllerDynamics, DynamicsABC

@pytest.fixture
def no_op_controller_dynamics_instance():
    return NoOpControllerDynamics()

class TestNoOpControllerDynamics():
    """test suite for NoOpController Dynamics class"""
    
    def test_initialization_and_specs(self, no_op_controller_dynamics_instance: DynamicsABC):
        """test the dynamic class instance initializes correctly with proper specs"""
        assert no_op_controller_dynamics_instance.init_input_spec_names() == []
        assert no_op_controller_dynamics_instance.init_input_spec_types() == []

        assert no_op_controller_dynamics_instance.state_input_spec_names() == []
        assert no_op_controller_dynamics_instance.state_input_spec_types() == []

        assert no_op_controller_dynamics_instance.dynamic_output_spec_name() == "AutomatonControlOutputs"
        assert no_op_controller_dynamics_instance.dynamic_output_spec_description() == "outputs for automaton spec"
        assert no_op_controller_dynamics_instance.dynamic_output_spec_names() == ['velocity', 'yaw_rate']
        assert no_op_controller_dynamics_instance.dynamic_output_spec_types()== [float, float]
        assert no_op_controller_dynamics_instance.dynamic_output_spec_units() == ['m/s', 'rad/s']

    def test_string_representations(self, no_op_controller_dynamics_instance: DynamicsABC):
        """Test string representation methods"""
        assert repr(no_op_controller_dynamics_instance) == 'NoOpControllerDynamics(output_type=AutomatonControlOutputs, initialized=True)'
        assert str(no_op_controller_dynamics_instance) == 'Dynamics Function: NoOpControllerDynamics (Output: AutomatonControlOutputs)'

    def test_dynamic_evaluation(self, no_op_controller_dynamics_instance: DynamicsABC):
        """Test the dynamics evaluations of this controller"""
        dynamics_outputs = no_op_controller_dynamics_instance()
        assert dynamics_outputs.velocity== 0.0
        assert dynamics_outputs.yaw_rate == 0.0

    # NOTE: No __init__ kwargs or __call__ kwargs expected therefore no tests for validation required.

if __name__ == '__main__':
    pytest.main([__file__])