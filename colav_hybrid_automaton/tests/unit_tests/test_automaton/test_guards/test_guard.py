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
    def test_guard_creation_and_calls(guard_instance: GuardABC):
        # Test valid creation
        print (guard_instance)
        # assert guard_instance.i == 20.0

        # # Test valid call with correct state
        # kwargs = {'x':5.0 }
        # guard.__call__(**kwargs)  # Should not raise

        # # Test call with invalid state type
        # kwargs = {'x':"not a float" }
        # with pytest.raises(TypeError):
        #     guard.__call__(kwargs)

        # # Test call with missing state input
        # with pytest.raises(ValueError):
        #     guard.__call__()

        # guard_info = guard.get_guard_info()
        # assert guard_info['class_name'] == 'TestGuard'
        # assert guard_info['module'] == 'test_guard'
        # assert guard_info['is_initialized'] == True
        # assert guard_info['description'] == 'This is a test of the guard condition abstract class.'

        # assert guard.__str__() == "Guard Function: TestGuard"
        # assert guard.__repr__() == "TestGuard(initialized=True)"

    # def test_guard_invalid_initialization_missing_param():
    #     class TestGuard(GuardABC):
    #         def _validate_initialization(self, **kwargs):
    #             if 'x' not in kwargs:
    #                 raise ValueError("Missing required parameter 'x'")

    #         def __call__(self, **state_kwargs):
    #             return super().__call__(**state_kwargs)

    #     with pytest.raises(ValueError):
    #         TestGuard()  # Missing 'x'

    # def test_guard_invalid_initialization_wrong_type():
    #     class TestGuard(GuardABC):
    #         def _validate_initialization(self, **kwargs):
    #             if not isinstance(kwargs.get('x'), float):
    #                 raise TypeError('x is not valid type')

    #         def __call__(self, **state_kwargs):
    #             return super().__call__(**state_kwargs)

    #     with pytest.raises(TypeError):
    #         TestGuard(x="not a float")

    # def test_guard_call_before_init():
    #     class TestGuard(GuardABC):
    #         def __init__(self, **kwargs):
    #             # Intentionally skip calling super().__init__ to simulate no init
    #             self.is_initialized = False

    #         def __call__(self, **state_kwargs):
    #             return super().__call__(**state_kwargs)

    #     guard = TestGuard()
    #     with pytest.raises(RuntimeError):
    #         guard.__call__(x=1.0)
