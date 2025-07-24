
"""
Test class for GuardInterface interface class

Tests the underlying functionalities for the GuardABC abstract class to ensure it works
as expected through the lifecycle of build and runtime.
"""

import pytest
from automaton_models.hybraut_model.aci_interfaces.guard_interface import GuardInterface
from automaton.spec.io_spec import IOSpec
from enum import Enum, auto
from _pytest.fixtures import FixtureRequest

class MockGuard(GuardInterface):
    """Mock implementation of GuardABC for testing purposes."""
    
    class DirectionEnum(Enum):
        UP = auto()
        DOWN = auto()

    _init_input_spec = [IOSpec.create_io_spec(name='threshold', type=float)]
    _state_input_spec = [
        IOSpec.create_io_spec(name='value', type=float),
        IOSpec.create_io_spec(name='direction', type=DirectionEnum)
    ]
    
    def _evaluate(self, **state_kwargs) -> bool:
        """
        Simple mock guard that returns True if both class attribute 'threshold' and 
        state argument 'value' are greater than 10.
        """
        threshold: float = self.threshold
        value: float = state_kwargs.get("value")
        direction = state_kwargs.get("direction")


        if direction == MockGuard.DirectionEnum.UP:
            return value > threshold
        elif direction == MockGuard.DirectionEnum.DOWN:
            return value < threshold
        else:
            return False  # Defensive fallback

@pytest.fixture
def guard_instance():
    """Fixture providing a properly initialized MockGuard instance."""
    return MockGuard(threshold=20.0)


class TestGuardABC:
    """Test suite for GuardABC abstract class functionality."""
    
    def test_initialization_and_specs(self, guard_instance: GuardInterface):
        """Test that guard instance initializes correctly with proper specs."""
        assert guard_instance.threshold == 20.0
        assert guard_instance.is_initialized
        
        # Test input specifications
        assert guard_instance.get_init_input_spec_names() == ['threshold']
        assert guard_instance.get_init_input_spec_types() == [float]
        
        # Test state input specifications
        assert guard_instance.get_state_input_spec_names() == ['value', 'direction']
        assert guard_instance.get_state_input_spec_types() == [float, MockGuard.DirectionEnum]
    
    def test_string_representations(self, guard_instance):
        """Test string representation methods."""
        assert repr(guard_instance) == 'MockGuard(initialized=True)'
        assert str(guard_instance) == 'Hybrid Automaton Guard: MockGuard'
    
    @pytest.mark.parametrize(
        "value, direction, expected_evaluation",
        [
            (40.0, MockGuard.DirectionEnum.UP, True),
            (40.0, MockGuard.DirectionEnum.DOWN, False),
            (20.0, MockGuard.DirectionEnum.UP, False)
        ],
        ids=[
            "threshold 20, value 40 and we are thresholding up, expected guard evaluation is True",
            "threshold 20.0, value: 40, threshold direction DOWN, expected guard evaluation is False",
            "threshold 20.0, value: 20.0, expected evaluation due to strict inequation of evaluation is False"
        ]
    )
    def test_valid_guard_evaluation(self, value: float, direction: MockGuard.DirectionEnum, expected_evaluation: bool, guard_instance: GuardInterface, request: FixtureRequest):
        """Test that guard evaluation works correctly."""
        # Both values > 10, should return True
        assert guard_instance(value=value, direction=direction) == expected_evaluation, \
                f"{request.node.callspec.id}"
    
    @pytest.mark.parametrize(
        "init_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'threshold': 'invalid_type'}, TypeError),
        ],
        ids=[
            "missing_required_init_argument",
            "invalid_init_argument_type"
        ]
    )
    def test_invalid_initialization(self, init_kwargs, expected_exception):
        """Test that invalid initialization parameters raise appropriate exceptions."""
        with pytest.raises(expected_exception):
            MockGuard(**init_kwargs)
    
    @pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'value': 'invalid_type', 'direction': MockGuard.DirectionEnum.UP}, TypeError)
        ],
        ids=[
            "missing_required_state_argument",
            "invalid_state_argument_type"
        ]
    )
    def test_invalid_state_inputs(self, state_kwargs, expected_exception, guard_instance):
        """Test that invalid state inputs raise appropriate exceptions."""
        with pytest.raises(expected_exception):
            guard_instance(**state_kwargs)


# if __name__ == '__main__':
#     pytest.main([__file__])

if __name__ == '__main__':

    TestGuardABC().test_initialization_and_specs(guard_instance._fixture_function())
    TestGuardABC().test_string_representations(guard_instance._fixture_function())
    TestGuardABC().test_valid_guard_evaluation(20.0, MockGuard.DirectionEnum.UP, False, guard_instance._fixture_function(), "")
