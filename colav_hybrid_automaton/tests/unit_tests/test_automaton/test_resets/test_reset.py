"""
Test class for ResetABC abstract class

In this class we utilize ResetABC to test 
the underlying functionalities for this abstract class to ensure it is working
as expected through the lifecycle of build and runtime.
"""

from colav_hybrid_automaton.automaton.resets import ResetABC
import pytest
from typing import Dict, Any
from colav_hybrid_automaton.automaton._internal.types import InputSpec

@pytest.fixture()
def TestResetFixture():
    """
     implementation of a simple ResetABC implemented class
    """
    class TestReset(ResetABC):
        """
        This is a test of the reset function abstract class.
        """
        
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
            # Define reset targets that this reset function will update
            super().__init__(**init_kwargs)
            self.i: float = init_kwargs.get('i')
            
        def __call__(self, **state_kwargs) -> Dict[str, Any]:
            super().__call__(**state_kwargs)
            # Reset logic: return updated values for the reset targets
            return {
                'output_x': state_kwargs['x'] * 2.0,
                'output_y': int(state_kwargs['x'])
            }
        
    yield TestReset

def test_reset_abstract_class_comprehensive(TestResetFixture):
    """
    This class tests the valid inputs/outputs initialization and runtime calls
    to ensure valid outputs based on the mock ResetABC implementation
    """
    reset_class = TestResetFixture
    reset: ResetABC = reset_class(i=10.0)

    assert reset.init_input_spec_names() == ['i']
    assert reset.init_input_spec_types() == [float]

    assert reset.state_input_spec_names() == ['x']
    assert reset.state_input_spec_types() == [float]

    assert reset.reset_target_spec_names() == ['output_x', 'output_y']
    assert reset.reset_target_spec_types() == [float, int]

    assert reset.__repr__() == "TestReset(initialized=True, targets=['output_x', 'output_y'])"
    assert reset.__str__() == 'Reset Function: TestReset (targets: 2)'

    assert reset.is_initialized == True
    assert reset.i == 10.0


    target_updates = reset.__call__(x=10.0)

    assert target_updates.get('output_x', -1.0) == 20.0
    assert target_updates.get('output_y', -1) == 10


@pytest.mark.parametrize(
        "init_kwargs, expected_exception",
        [
            # Test Case 1: no init args passed
            ({}, KeyError),
            # Test Case 2: appropriate kwarg passed but wrong type
            ({'': 'invalid type'}, TypeError),
        ],
        ids=[
            "Test Case 1: no init_kwargs for __init__ of reset, expect KeyError",
            "Test Case 2: correct init_kwarg required arg passed but wrong type, expect KeyError"
        ]
)
def test_reset_invalid_initialization(init_kwargs, expected_exception, TestResetFixture):
    """
    paramterize test for invalid build time __init__ arg inputs

    Each case checks if the class raises the expected exception type
    when initializaed with incomplete or incorrect types in kwargs
    """
    with pytest.raises(expected_exception):
        TestResetFixture(**init_kwargs)


@pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            # Test Case 1: no state_kwargs given
            ({}, KeyError),
            # Test Case 2: valid state_kwarg given but invalid type
            ({'x': 'invalid type'}, TypeError)
        ],
        ids=[
            'Test Case 1: no state args given, expect KeyError',
            'Test Case 2: valid state kwargs given but wrong type, expect TypeError'
        ]
)
def test_reset_invalid_state_inputs(state_kwargs, expected_exception, TestResetFixture):
    """
    paramaterized test for invalid runtime state inputs

    Each case checks if the class raises the expected exception type 
    on __call__.
    """
    reset:ResetABC = TestResetFixture(i=10.0)

    with pytest.raises(expected_exception):
        reset.__call__(**state_kwargs) 

if __name__ == '__main__':
    class TestReset(ResetABC):
            """
            This is a test of the reset function abstract class.
            """
            
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
                # Define reset targets that this reset function will update
                super().__init__(**init_kwargs)
                self.i: float = init_kwargs.get('i')
                
            def __call__(self, **state_kwargs) -> Dict[str, Any]:
                super().__call__(**state_kwargs)
                # Reset logic: return updated values for the reset targets
                return {
                    'output_x': state_kwargs['x'] * 2.0,
                    'output_y': int(state_kwargs['x'])
                }
    test_reset_abstract_class_comprehensive(
        TestResetFixture = TestReset
    )
