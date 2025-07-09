import pytest
from colav_hybrid_automaton.automaton.guards.guard import GuardABC
from colav_hybrid_automaton.automaton._internal.types import InputSpec

class MockGuard(GuardABC):
    """
    This is a test of the guard condition abstract class.
    """
    _init_input_spec = [InputSpec(name='i', type=float)]
    _state_input_spec = [InputSpec(name='x', type=float)]

    def __call__(self, **state_kwargs):
        """a simple mock guard which returns true if class atribute i is greater than 10 and state arg too."""
        super().__call__(**state_kwargs)

        if self.__getattribute__('i') > 10 and state_kwargs.get('x') > 10:
            return True
        else:
            return False

@pytest.fixture
def guard_instance() -> GuardABC:
    return MockGuard(i=20.0)

class TestGuardABC:
    def test_guard_creation_and_calls(self, guard_instance: GuardABC):
        # Test valid creation
        assert guard_instance.i == 20.0
        assert guard_instance.is_initialized == True
        assert guard_instance.init_input_spec_names() == ['i']
        assert guard_instance.init_input_spec_types() == [float]
        assert guard_instance.state_input_spec_names() == ['x']
        assert guard_instance.state_input_spec_types() == [float]
        assert guard_instance.__repr__() == 'MockGuard(initialized=True)'
        assert guard_instance.__str__() == 'Guard Function: MockGuard'

        eval: bool = guard_instance.__call__(x=20.0)
        assert eval == True

        eval: bool = guard_instance.__call__(x=5.0)
        assert eval == False

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
    def test_invalid_state_inputs(self, state_kwargs, expected_exception, guard_instance: GuardABC):
        """Test that invalid state inputs raise appropriate exceptions."""
        guard = guard_instance
        
        with pytest.raises(expected_exception):
            guard(**state_kwargs)

if __name__ == '__main__':
    mock_guard = MockGuard(i=20.0)
    TestGuardABC.test_guard_creation_and_calls(mock_guard)