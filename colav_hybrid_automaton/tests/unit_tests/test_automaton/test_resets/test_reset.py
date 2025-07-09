"""
Test class for ResetABC abstract class

Tests the underlying functionalities for the ResetABC abstract class to ensure it works
as expected through the lifecycle of build and runtime.
"""

import pytest
from typing import Dict, Any

from colav_hybrid_automaton.automaton.resets import ResetABC
from colav_hybrid_automaton.automaton._internal.types import InputSpec


class MockReset(ResetABC):
    """Test implementation of ResetABC for testing purposes."""
    
    _init_input_spec = [
        InputSpec(name='i', type=float)
    ]

    _state_input_spec = [
        InputSpec(name='x', type=float)
    ]

    _reset_targets_spec = [
        InputSpec(name='output_x', type=float),
        InputSpec(name='output_y', type=int)
    ]

    def __init__(self, **init_kwargs):
        super().__init__(**init_kwargs)
        self.i: float = init_kwargs.get('i')
        
    def __call__(self, **state_kwargs) -> Dict[str, Any]:
        super().__call__(**state_kwargs)
        # Reset logic: return updated values for the reset targets
        return {
            'output_x': state_kwargs['x'] * 2.0,
            'output_y': int(state_kwargs['x'])
        }


@pytest.fixture
def reset_instance():
    """Fixture providing a properly initialized TestReset instance."""
    return MockReset(i=10.0)


class TestResetABC:
    """Test suite for ResetABC abstract class functionality."""
    
    def test_initialization_and_specs(self, reset_instance):
        """Test that reset instance initializes correctly with proper specs."""
        reset = reset_instance
        
        # Test input specifications
        assert reset.init_input_spec_names() == ['i']
        assert reset.init_input_spec_types() == [float]
        
        # Test state input specifications
        assert reset.state_input_spec_names() == ['x']
        assert reset.state_input_spec_types() == [float]
        
        # Test reset target specifications
        assert reset.reset_target_spec_names() == ['output_x', 'output_y']
        assert reset.reset_target_spec_types() == [float, int]
        
        # Test initialization status and attributes
        assert reset.is_initialized is True
        assert reset.i == 10.0
    
    def test_string_representations(self, reset_instance):
        """Test string representation methods."""
        reset = reset_instance
        
        expected_repr = "MockReset(initialized=True, targets=['output_x', 'output_y'])"
        expected_str = 'Reset Function: MockReset (targets: 2)'
        
        assert repr(reset) == expected_repr
        assert str(reset) == expected_str
    
    def test_valid_call_execution(self, reset_instance):
        """Test that valid calls produce expected outputs."""
        reset = reset_instance
        
        target_updates = reset(x=10.0)
        
        assert target_updates['output_x'] == 20.0
        assert target_updates['output_y'] == 10
    
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
            MockReset(**init_kwargs)
    
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
    def test_invalid_state_inputs(self, state_kwargs, expected_exception, reset_instance):
        """Test that invalid state inputs raise appropriate exceptions."""
        reset = reset_instance
        
        with pytest.raises(expected_exception):
            reset(**state_kwargs)