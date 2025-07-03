import pytest
from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsABC
from typing import NamedTuple

def test_dynamic_creation_and_call():
    class TestDynamic(DynamicsABC):
        """
        This is a test of the dynamic condition abstract class.
        """

        class NamedTupleOutput(NamedTuple):
            velocity: float
            yaw_rate: float

        def __init__(self, **init_kwargs):
            super().__init__(self.NamedTupleOutput, **init_kwargs)
            self.target_velocity: float = init_kwargs.get('target_velocity')
            self.target_yaw_rate: float = init_kwargs.get('target_yaw_rate')

        def __call__(self, **state_kwargs) -> NamedTupleOutput:
            super().__call__(**state_kwargs)
            current_velocity = state_kwargs.get('current_velocity')
            current_yaw_rate = state_kwargs.get('current_yaw_rate')

            if current_velocity < self.target_velocity:
                current_velocity = current_velocity + 1.0

            return self.NamedTupleOutput(velocity=current_velocity, yaw_rate=current_yaw_rate)

        def _validate_states(self, **state_kwargs):
            if 'current_velocity' not in state_kwargs:
                raise ValueError("Missing state input 'current_velocity'")
            if not isinstance(state_kwargs.get('current_velocity'), float):
                raise TypeError("current_velocity state input is invalid")

        def _validate_initialization(self, **init_kwargs):
            if 'target_velocity' not in init_kwargs:
                raise KeyError("Missing required parameter 'target_velocity'")
            if not isinstance(init_kwargs.get('target_velocity'), float):
                raise TypeError("target_velocity is not valid type")
            if 'target_yaw_rate' not in init_kwargs:
                raise KeyError("Missing required parameter 'target_yaw_rate'")
            if not isinstance(init_kwargs.get('target_yaw_rate'), float):
                raise TypeError("target_yaw_rate is not valid type")

    # Test valid creation
    init_kwargs = {'target_velocity': 5.0, 'target_yaw_rate': 0.2}
    dynamic = TestDynamic(**init_kwargs)
    assert dynamic.is_initialized
    assert dynamic.target_velocity == 5.0
    assert dynamic.target_yaw_rate == 0.2

    # Test valid call
    output = dynamic(current_velocity=3.0, current_yaw_rate=0.1)
    assert isinstance(output, TestDynamic.NamedTupleOutput)
    assert output.velocity == 4.0  # velocity should have increased by 1
    assert output.yaw_rate == 0.1

    # Test call with velocity already above target (should stay the same)
    output = dynamic(current_velocity=6.0, current_yaw_rate=0.1)
    assert output.velocity == 6.0  # no change

    # Test call with invalid state type
    with pytest.raises(TypeError):
        dynamic(current_velocity="fast", current_yaw_rate=0.1)

    # Test call with missing state input
    with pytest.raises(ValueError):
        dynamic(current_yaw_rate=0.1)

    # Test creation with missing init parameter
    with pytest.raises(KeyError):
        TestDynamic(target_yaw_rate=0.1)  # missing target_velocity

    with pytest.raises(KeyError):
        TestDynamic(target_velocity=5.0)  # missing target_yaw_rate

    # Test creation with wrong type
    with pytest.raises(TypeError):
        TestDynamic(target_velocity="fast", target_yaw_rate=0.1)

    with pytest.raises(TypeError):
        TestDynamic(target_velocity=5.0, target_yaw_rate="turn")

    # Info check
    info = dynamic.get_dynamics_info()
    assert info['class_name'] == 'TestDynamic'
    assert 'dynamics' in info['module'] or 'test_dynamic' in info['module']
    assert info['is_initialized'] is True
    assert info['description'] == 'This is a test of the dynamic condition abstract class.'

    # String/representation
    # assert str(dynamic).startswith("Dynamic Function:")
    # assert repr(dynamic).startswith("TestDynamic(initialized=True)")

# def test_guard_invalid_initialization_missing_param():
#     class TestGuard(Guard):
#         def _validate_initialization(self, **kwargs):
#             if 'x' not in kwargs:
#                 raise ValueError("Missing required parameter 'x'")

#         def __call__(self, **state_kwargs):
#             return super().__call__(**state_kwargs)

#     with pytest.raises(ValueError):
#         TestGuard()  # Missing 'x'

# def test_guard_invalid_initialization_wrong_type():
#     class TestGuard(Guard):
#         def _validate_initialization(self, **kwargs):
#             if not isinstance(kwargs.get('x'), float):
#                 raise TypeError('x is not valid type')

#         def __call__(self, **state_kwargs):
#             return super().__call__(**state_kwargs)

#     with pytest.raises(TypeError):
#         TestGuard(x="not a float")

# def test_guard_call_before_init():
#     class TestGuard(Guard):
#         def __init__(self, **kwargs):
#             # Intentionally skip calling super().__init__ to simulate no init
#             self.is_initialized = False

#         def __call__(self, **state_kwargs):
#             return super().__call__(**state_kwargs)

#     guard = TestGuard()
#     with pytest.raises(RuntimeError):
#         guard.__call__(x=1.0)
