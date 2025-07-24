"""
Test class for GuardABC abstract class

Tests the underlying functionalities for the GuardABC abstract class to ensure it works
as expected through the lifecycle of build and runtime.
"""

import pytest
from automaton_models.hybraut_model.aci_interfaces.guard_interface import GuardABC
from nodes._internal.types import InputSpec


class MockGuard(GuardABC):
    """Mock implementation of GuardABC for testing purposes."""
    
    _init_input_spec = [InputSpec(name='i', type=float)]
    _state_input_spec = [InputSpec(name='x', type=float)]
    
    def __call__(self, **state_kwargs):
        """
        Simple mock guard that returns True if both class attribute 'i' and 
        state argument 'x' are greater than 10.
        """
        super().__call__(**state_kwargs)
        return self.i > 10 and state_kwargs.get('x') > 10


@pytest.fixture
def guard_instance():
    """Fixture providing a properly initialized MockGuard instance."""
    return MockGuard(i=20.0)


class TestGuardABC:
    """Test suite for GuardABC abstract class functionality."""
    
    def test_initialization_and_specs(self, guard_instance):
        """Test that guard instance initializes correctly with proper specs."""
        assert guard_instance.i == 20.0
        assert guard_instance.is_initialized
        
        # Test input specifications
        assert guard_instance.init_input_spec_names() == ['i']
        assert guard_instance.init_input_spec_types() == [float]
        
        # Test state input specifications
        assert guard_instance.state_input_spec_names() == ['x']
        assert guard_instance.state_input_spec_types() == [float]
    
    def test_string_representations(self, guard_instance):
        """Test string representation methods."""
        assert repr(guard_instance) == 'MockGuard(initialized=True)'
        assert str(guard_instance) == 'Guard Function: MockGuard'
    
    def test_guard_evaluation(self, guard_instance):
        """Test that guard evaluation works correctly."""
        # Both values > 10, should return True
        assert guard_instance(x=20.0) is True
        
        # State value <= 10, should return False
        assert guard_instance(x=5.0) is False
        
        # Edge case: exactly 10
        assert guard_instance(x=10.0) is False
    
    @pytest.mark.parametrize(
        "init_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'i': 'invalid_type'}, TypeError),
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
            ({'x': 'invalid_type'}, TypeError)
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


if __name__ == '__main__':
    pytest.main([__file__])
