"""
Test class for DynamicsABC abstract class

In this class we utilize DyanmicsABC abstract class to test 
the underlying functionalities for this abstract class to enusre it is working 
as expected through the lifecycle of build and runtime
"""


import pytest
from automaton.core_interfaces.dynamics_abc import DynamicsABC
from typing import NamedTuple
from automaton.core_interfaces.dynamics_abc import DynamicsSpecBuilder
from nodes._internal.types import InputSpec
import pytest

class MockDynamics(DynamicsABC):
    """
    A minimal concrete implementation of the abstract DynamicsABC class,
    used for testing purposes.

    This test dynamic increments the current velocity by 1.0 if it is below
    the target velocity. The yaw rate is passed through unchanged.
    """

    _init_input_spec = [
        InputSpec(name='target_velocity', type=float),
        InputSpec(name='target_yaw_rate', type=float)
    ]
    _state_input_spec = [
        InputSpec(name='current_velocity', type=float),
        InputSpec(name='current_yaw_rate', type=float)
    ]
    _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)
        current_velocity = state_kwargs.get('current_velocity')
        current_yaw_rate = state_kwargs.get('current_yaw_rate')

        if current_velocity < self.__getattribute__('target_velocity'):
            current_velocity = current_velocity + 1.0

        return self.create_output(velocity=current_velocity, yaw_rate=current_yaw_rate)

@pytest.fixture
def dynamics_instance():
    """
    Fixture to instantiate the TestDynamic class.
    """
    return MockDynamics(target_velocity=5.0, target_yaw_rate=0.2)


class TestDynamicsABC:
    def test_dynamic_abstract_class_comprehensive(self, dynamics_instance: DynamicsABC):
        """
        Tests the full initialization and usage of the TestDynamic class.
        
        - Validates correct handling of initial input spec.
        - Validates correct state input/output specification.
        - Confirms behavior of `__call__` method.
        """
        assert dynamics_instance.is_initialized
        assert dynamics_instance.target_velocity == 5.0
        assert dynamics_instance.target_yaw_rate == 0.2

        assert dynamics_instance.init_input_spec_names() == ['target_velocity', 'target_yaw_rate']
        assert dynamics_instance.init_input_spec_types() == [float, float]

        assert dynamics_instance.state_input_spec_names() == ['current_velocity', 'current_yaw_rate']
        assert dynamics_instance.state_input_spec_types() == [float, float]

        assert dynamics_instance.dynamic_output_spec_name() == "AutomatonControlOutputs"
        assert dynamics_instance.dynamic_output_spec_description() == 'outputs for automaton spec'
        assert dynamics_instance.dynamic_output_spec_names() == ['velocity', 'yaw_rate']
        assert dynamics_instance.dynamic_output_spec_types() == [float, float]
        assert dynamics_instance.dynamic_output_spec_units() == ['m/s', 'rad/s']


        # Test valid call
        output = dynamics_instance.__call__(current_velocity=3.0, current_yaw_rate=0.1)
        assert output.velocity == 4.0  # velocity should have increased by 1
        assert output.yaw_rate == 0.1

        # Test call with velocity already above target (should stay the same)
        output = dynamics_instance.__call__(current_velocity=6.0, current_yaw_rate=0.1)
        assert output.velocity == 6.0  # no change

    @pytest.mark.parametrize(
        "init_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'target_yaw_rate': 0.2}, KeyError),
            ({'target_velocity': 2.0}, KeyError),
            ({'target_velocity': 'invalid', 'target_yaw_rate': 0.2}, TypeError),
            ({'target_velocity': 10.0, 'target_yaw_rate': ''}, TypeError)
        ],
        ids=[
            'Test Case 1: no init_kwargs for __init__ of dynamics, expect KeyError.',
            'Test Case 2: missing target_yaw_rate in __init__, expect KeyError.',
            'Test Case 3: missing target_velocity in __init__, expect KeyError.',
            'Test Case 4: invalid target_velocity',
            'Test Case 5: invalid target_yaw_rate type'
        ]
    )
    def test_dynamic_invalid_initializations(self, init_kwargs, expected_exception):
        """
        Parameterized test for invalid initializations of the dynamic class.
        
        Each case checks if the class raises the expected exception type
        when initialized with incomplete or incorrect types in kwargs.
        """
        with pytest.raises(expected_exception):
            # Assuming TestDynamicFixture is a class or callable that takes **kwargs
            MockDynamics(**init_kwargs)

    @pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'current_velocity': 10.0}, KeyError),
            ({'current_yaw_rate': 0.1}, KeyError),
            ({'current_velocity': 'invalid type', 'current_yaw_rate': 0.2}, TypeError),
            ({'current_velocity': 20.0, 'current_yaw_rate': 'invalid type'}, TypeError)
        ],
        ids=[
            "Test Case 1: no state args given, expect KeyError.",
            "Test Case 2: current_yaw_rate state arg missing on __call__, expect KeyError.",
            "Test Case 3: current_velocity state arg missing on __call__, expect KeyError.",
            "Test Case 4: current_velocity state arg type invalid on __call__, expect TypeError.",
            "Test Case 5: current_yaw_rate state arg type invalid on __call__, expect TypeError."
        ]
    )
    def test_dynamic_invalid_state_inputs(self, state_kwargs, expected_exception, dynamics_instance: DynamicsABC):
        """
        Parameterized test for invalid runtime state inputs to the dynamic class.
        
        Each test provides an invalid or incomplete state input dictionary,
        and checks whether the `__call__` method raises the appropriate exception.
        """
        with pytest.raises(expected_exception):
            dynamics_instance.__call__(**state_kwargs)

if __name__ == '__main__':
    pytest.main([__file__])
