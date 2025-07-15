import pytest
from automaton.invariants import TrivialInvariant, InvariantABC

@pytest.fixture
def trivial_invariant_instance():
    return TrivialInvariant()

class TestTrivialInvariant:
    """test """
    def test_initialization_and_specs(self, trivial_invariant_instance: InvariantABC):
        """test the initialization and specifications of the class instance are valid"""
        assert trivial_invariant_instance.init_input_spec_names() == []
        assert trivial_invariant_instance.init_input_spec_types() == []
        assert trivial_invariant_instance.state_input_spec_names() == []
        assert trivial_invariant_instance.state_input_spec_types() == [] 

    def test_string_representations(self, trivial_invariant_instance: InvariantABC):
        """test the string representations of the guard instance"""
        assert repr(trivial_invariant_instance) == 'TrivialInvariant(initialized=True)'
        assert str(trivial_invariant_instance) == 'Invariant Function: TrivialInvariant'

    def test_invariant_evaluation(self, trivial_invariant_instance):
        """Comprehensive test for FailingInvariant."""
        assert trivial_invariant_instance() == True, 'Trivial invariant call should be true, but got false'


if __name__ == '__main__':
    pytest.main([__file__])