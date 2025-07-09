import pytest
from colav_hybrid_automaton.automaton.invariants import FailingInvariant, InvariantABC

@pytest.fixture
def failing_invariant_instance():
    return FailingInvariant()

class TestFailingInvariant:
    """test """
    def test_initialization_and_specs(self, failing_invariant_instance: InvariantABC):
        """test the initialization and specifications of the class instance are valid"""
        assert failing_invariant_instance.init_input_spec_names() == []
        assert failing_invariant_instance.init_input_spec_types() == []
        assert failing_invariant_instance.state_input_spec_names() == []
        assert failing_invariant_instance.state_input_spec_types() == [] 

    def test_string_representations(self, failing_invariant_instance: InvariantABC):
        """test the string representations of the guard instance"""
        assert repr(failing_invariant_instance) == 'FailingInvariant(initialized=True)'
        assert str(failing_invariant_instance) == 'Invariant Function: FailingInvariant'

    def test_invariant_evaluation(self, failing_invariant_instance):
        """Comprehensive test for FailingInvariant."""
        assert failing_invariant_instance() == False, 'Failing invariant call should be false, but got true'


if __name__ == '__main__':
    pytest.main([__file__])