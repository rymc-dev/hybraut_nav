"""
Test class for InvariantABC abstract class

Tests the underlying functionalities for the InvariantABC abstract class to ensure it works
as expected through the lifecycle of build and runtime.
"""

import pytest
from automaton_models.hybrid.aci_interfaces.invariant_interface import InvariantInterface
from automaton.spec.io_spec import IOSpec
from _pytest.fixtures import FixtureRequest

class MockInvariant(InvariantInterface):
    """Mock implementation of InvariantInterface for testing purposes."""

    _init_input_spec = [
        IOSpec.create_io_spec(name='target', type=float)
    ]

    _state_input_spec = [
        IOSpec.create_io_spec(name='measurement', type=float)
    ]

    def _evaluate(self, **state_kwargs) -> bool:
        """
        Mock invariant that checks if the measurement is within 10% of the target.

        Returns True if:
            abs(measurement - target) <= 0.1 * target
        """
        target: float = self.target
        measurement: float = state_kwargs.get("measurement")

        if measurement is None:
            raise ValueError("Missing required state 'measurement'")

        tolerance = 0.1 * abs(target)
        return abs(measurement - target) <= tolerance

@pytest.fixture
def invariant_instance():
    return MockInvariant(target=20.0)

class TestInvariantABC:
    """Test suite for InvariantABC abstract class functionality."""

    def test_initialization_and_specs(self, invariant_instance: InvariantInterface):
        """Test that invariant instacne initializes correctly and with proper specs.""" 
        # Test valid creation
        assert invariant_instance.is_initialized
        assert invariant_instance.target == 20.0

        assert invariant_instance._get_component_type() == "Invariant"
        assert invariant_instance.get_init_input_spec_names() == ['target']
        assert invariant_instance.get_init_input_spec_types() == [float]
        assert invariant_instance.get_state_input_spec_names() == ['measurement']
        assert invariant_instance.get_state_input_spec_types() == [float]
    
    def test_string_representations(self, invariant_instance):
        """Test string representation methods."""
        assert repr(invariant_instance) == "MockInvariant(initialized=True)"
        assert str(invariant_instance) == "Hybrid Automaton Invariant: MockInvariant"

    def test_component_information(self, invariant_instance: InvariantInterface):
        invariant_info = invariant_instance.get_component_info()
        assert invariant_info['class_name'] == 'MockInvariant'
        assert invariant_info['component_type'] == 'Invariant'
        assert invariant_info['description'] == 'Mock implementation of InvariantInterface for testing purposes.'
        assert invariant_info['is_initialized'] == True
        assert invariant_info['init_input_spec_names'] == ['target']
        assert invariant_info['init_input_spec_types'] == ['float']
        assert invariant_info['state_input_spec_names'] == ['measurement']
        assert invariant_info['state_input_spec_types'] == ['float']


    @pytest.mark.parametrize(
            "measurement, expected_evaluation",
            [
                (10.0, False),
                (20.0, True),
                (21.0, True), 
                (30.0, False)
            ],
            ids=[
                "test 1",
                "test 2",
                "test 3", 
                "test 4"
            ]
    )
    def test_valid_invariant_evaluation(self, measurement: float, expected_evaluation: bool, invariant_instance: InvariantInterface, request: FixtureRequest):
        """Test invariant evaluation works correctly."""
        assert invariant_instance(measurement=measurement) == expected_evaluation, \
                f"{request.node.callspec.id}"

    # @pytest.mark.parametrize(
    #     "init_kwargs, expected_exception",
    #     [
    #         ({}, KeyError),
    #         ({'i': 1.0}, TypeError),
    #     ],
    #     ids=[
    #         "missing_required_init_argument",
    #         "invalid_init_argument_type"
    #     ]
    # )
    # def test_invalid_initialization(self, init_kwargs, expected_exception):
    #     """Test that invalid initialization parameters raise appropriate exceptions."""
    #     with pytest.raises(expected_exception):
    #         MockInvariant(**init_kwargs)
    
    # @pytest.mark.parametrize(
    #     "state_kwargs, expected_exception",
    #     [
    #         ({}, KeyError),
    #         ({'x': 'invalid_type'}, TypeError)
    #     ],
    #     ids=[
    #         "missing_required_state_argument",
    #         "invalid_state_argument_type"
    #     ]
    # )
    # def test_invalid_state_inputs(self, state_kwargs, expected_exception, invariant_instance: InvariantABC):
    #     """Test that invalid state inputs raise appropriate exceptions."""
    #     with pytest.raises(expected_exception):
    #         invariant_instance(**state_kwargs)

        
# if __name__ == '__main__':
#     pytest.main([__file__])

if __name__ == '__main__':
    TestInvariantABC().test_initialization_and_specs(invariant_instance=invariant_instance._fixture_function())
    TestInvariantABC().test_string_representations(invariant_instance=invariant_instance._fixture_function())
    TestInvariantABC().test_component_information(invariant_instance=invariant_instance._fixture_function())
    TestInvariantABC().test_valid_invariant_evaluation(measurement=20.0, expected_evaluation=True, invariant_instance=invariant_instance._fixture_function(), request=FixtureRequest)