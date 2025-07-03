import pytest
from colav_hybrid_automaton.automaton.guards.guard import GuardABC

def test_guard_creation_and_calls():
    class TestGuard(GuardABC):
        """
        This is a test of the guard condition abstract class.
        """
        def __init__(self, **init_kwargs):
            super().__init__(**init_kwargs)
            self.x: float = init_kwargs.get('x')

        def __call__(self, **state_kwargs):
            return super().__call__(**state_kwargs)

        def _validate_states(self, **state_kwargs):
            if 'x' not in state_kwargs:
                raise ValueError("Missing state input 'x'")
            if not isinstance(state_kwargs.get('x'), float):
                raise TypeError('x state input is invalid')

        def _validate_initialization(self, **kwargs):
            if 'x' not in kwargs:
                raise ValueError("Missing required parameter 'x'")
            if not isinstance(kwargs.get('x'), float):
                raise TypeError('x is not valid type')

    # Test valid creation
    kwargs = {'x': 10.0}
    guard = TestGuard(**kwargs)
    assert guard.is_initialized
    assert guard.x == 10.0

    # Test valid call with correct state
    kwargs = {'x':5.0 }
    guard.__call__(**kwargs)  # Should not raise

    # Test call with invalid state type
    kwargs = {'x':"not a float" }
    with pytest.raises(TypeError):
        guard.__call__(kwargs)

    # Test call with missing state input
    with pytest.raises(ValueError):
        guard.__call__()

    guard_info = guard.get_guard_info()
    assert guard_info['class_name'] == 'TestGuard'
    assert guard_info['module'] == 'test_guard'
    assert guard_info['is_initialized'] == True
    assert guard_info['description'] == 'This is a test of the guard condition abstract class.'

    assert guard.__str__() == "Guard Function: TestGuard"
    assert guard.__repr__() == "TestGuard(initialized=True)"

def test_guard_invalid_initialization_missing_param():
    class TestGuard(GuardABC):
        def _validate_initialization(self, **kwargs):
            if 'x' not in kwargs:
                raise ValueError("Missing required parameter 'x'")

        def __call__(self, **state_kwargs):
            return super().__call__(**state_kwargs)

    with pytest.raises(ValueError):
        TestGuard()  # Missing 'x'

def test_guard_invalid_initialization_wrong_type():
    class TestGuard(GuardABC):
        def _validate_initialization(self, **kwargs):
            if not isinstance(kwargs.get('x'), float):
                raise TypeError('x is not valid type')

        def __call__(self, **state_kwargs):
            return super().__call__(**state_kwargs)

    with pytest.raises(TypeError):
        TestGuard(x="not a float")

def test_guard_call_before_init():
    class TestGuard(GuardABC):
        def __init__(self, **kwargs):
            # Intentionally skip calling super().__init__ to simulate no init
            self.is_initialized = False

        def __call__(self, **state_kwargs):
            return super().__call__(**state_kwargs)

    guard = TestGuard()
    with pytest.raises(RuntimeError):
        guard.__call__(x=1.0)
