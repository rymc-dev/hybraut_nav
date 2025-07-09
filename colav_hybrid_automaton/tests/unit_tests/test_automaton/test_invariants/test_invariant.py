import pytest
from colav_hybrid_automaton.automaton.invariants.invariant import InvariantABC
from colav_hybrid_automaton.automaton._internal.types import InputSpec

class MockInvariant(InvariantABC): 
    """
    This is a test of the invariant condition abstract class.
    """
    _init_input_spec = [InputSpec(name='i', type=str)]
    _state_input_spec = [InputSpec(name='x', type=int)]

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)

        if self.__getattribute__('i') == 'hello world!' and state_kwargs.get('x') == 10:
            return True
        
        return False

@pytest.fixture
def invariant_instance():
    return MockInvariant(i='hello world!')

class TestInvariantABC:
    def test_initialization_and_specs(self, invariant_instance: InvariantABC): 
        # Test valid creation
        assert invariant_instance.is_initialized
        assert invariant_instance.i == 'hello world!'

        assert invariant_instance.init_input_spec_names() == ['i']
        assert invariant_instance.init_input_spec_types() == [str]
        assert invariant_instance.state_input_spec_names() == ['x']
        assert invariant_instance.state_input_spec_types() == [int]
    
    def test_string_representations(self, invariant_instance):
        assert repr(invariant_instance) == "MockInvariant(initialized=True)"
        assert str(invariant_instance) == "Invariant Function: MockInvariant"

    def test_invariant_evaluation(self, invariant_instance: InvariantABC):
        """Test that the invariant evaluation works"""
    
        # Test valid call with correct state
        assert invariant_instance(x=10) is True  # Should not raise
        assert invariant_instance(x=20) is False

    @pytest.mark.parametrize(
        "init_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'i': 1.0}, TypeError),
        ],
        ids=[
            "missing_required_init_argument",
            "invalid_init_argument_type"
        ]
    )
    def test_invalid_initialization(self, init_kwargs, expected_exception):
        """Test that invalid initialization parameters raise appropriate exceptions."""
        with pytest.raises(expected_exception):
            MockInvariant(**init_kwargs)
    
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
    def test_invalid_state_inputs(self, state_kwargs, expected_exception, invariant_instance: InvariantABC):
        """Test that invalid state inputs raise appropriate exceptions."""
        with pytest.raises(expected_exception):
            invariant_instance(**state_kwargs)

        
if __name__ == '__main__':
    pass