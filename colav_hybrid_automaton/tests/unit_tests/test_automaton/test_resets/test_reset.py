from colav_hybrid_automaton.automaton.resets import ResetABC
import pytest
from typing import Dict, Any
from colav_hybrid_automaton.automaton._internal.types import InputSpec

def test_reset_creation_and_calls():
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
        
    # Test valid creation
    kwargs = {'i': 10.0}
    reset_func = TestReset(**kwargs)
    assert reset_func.is_initialized
    assert reset_func.i == 10.0
    
    # Test valid call with correct state
    state_kwargs = {'x': 5.0}
    result = reset_func.__call__(**state_kwargs)
    assert isinstance(result, dict)
    assert result['output_x'] == 10.0  # 5.0 * 2.0
    assert result['output_y'] == 5     # int(5.0)
    
    # Test call with invalid state type
    invalid_kwargs = {'x': "not a float"}
    with pytest.raises(TypeError):
        reset_func.__call__(**invalid_kwargs)
    
    # Test call with missing state input
    with pytest.raises(KeyError):
        reset_func.__call__()
    
    # Test reset info
    reset_info = reset_func.get_reset_info()
    assert reset_info['class_name'] == 'TestReset'
    assert reset_info['module'] == 'test_reset'  # Will be __main__ when run in test context
    assert reset_info['is_initialized'] == True
    assert reset_info['target_count'] == 2
    assert reset_info['target_names'] == ['output_x', 'output_y']
    assert reset_info['description'] == 'This is a test of the reset function abstract class.'
    
    # Test string representations
    assert reset_func.__str__() == "Reset Function: TestReset (targets: 2)"
    assert reset_func.__repr__() == "TestReset(initialized=True, targets=['output_x', 'output_y'])"

if __name__ == '__main__':
    test_reset_creation_and_calls()

# def test_reset_initialization_validation():
#     """Test Reset class initialization validation"""
    
#     class TestReset(ResetABC):
#         def __init__(self, **init_kwargs):
#             reset_targets = [{'name': 'test_output', 'type': str}]
#             super().__init__(reset_targets=reset_targets, **init_kwargs)
            
#         def __call__(self, **state_kwargs) -> Dict[str, Any]:
#             super().__call__(**state_kwargs)
#             return {'test_output': 'test_value'}
    
#     # Test invalid reset_targets - not a list
#     with pytest.raises(TypeError, match="reset_targets must be a list"):
#         class BadReset1(ResetABC):
#             def __init__(self):
#                 super().__init__(reset_targets="not_a_list")
#             def __call__(self, **kwargs):
#                 return {}
#         BadReset1()
    
#     # Test empty reset_targets
#     with pytest.raises(ValueError, match="reset_targets cannot be empty"):
#         class BadReset2(ResetABC):
#             def __init__(self):
#                 super().__init__(reset_targets=[])
#             def __call__(self, **kwargs):
#                 return {}
#         BadReset2()
    
#     # Test invalid target structure - not a dict
#     with pytest.raises(TypeError, match="must be a dictionary"):
#         class BadReset3(ResetABC):
#             def __init__(self):
#                 super().__init__(reset_targets=["not_a_dict"])
#             def __call__(self, **kwargs):
#                 return {}
#         BadReset3()
    
#     # Test missing 'name' key
#     with pytest.raises(KeyError, match="must contain 'name' key"):
#         class BadReset4(ResetABC):
#             def __init__(self):
#                 super().__init__(reset_targets=[{'type': str}])
#             def __call__(self, **kwargs):
#                 return {}
#         BadReset4()
    
#     # Test missing 'type' key
#     with pytest.raises(KeyError, match="must contain 'type' key"):
#         class BadReset5(ResetABC):
#             def __init__(self):
#                 super().__init__(reset_targets=[{'name': 'test'}])
#             def __call__(self, **kwargs):
#                 return {}
#         BadReset5()

# def test_reset_output_validation():
#     """Test Reset class output validation"""
    
#     class TestReset(ResetABC):
#         def __init__(self):
#             reset_targets = [
#                 {'name': 'output_int', 'type': int},
#                 {'name': 'output_str', 'type': str}
#             ]
#             super().__init__(reset_targets=reset_targets)
            
#         def __call__(self, **state_kwargs) -> Dict[str, Any]:
#             super().__call__(**state_kwargs)
#             return {'output_int': 42, 'output_str': 'hello'}
    
#     reset_func = TestReset()
    
#     # Test valid output
#     valid_output = {'output_int': 42, 'output_str': 'hello'}
#     reset_func._validate_reset_output(valid_output)  # Should not raise
    
#     # Test invalid output type - not a dict
#     with pytest.raises(TypeError, match="Reset function must return a dictionary"):
#         reset_func._validate_reset_output("not_a_dict")
    
#     # Test missing required keys
#     incomplete_output = {'output_int': 42}  # missing 'output_str'
#     with pytest.raises(KeyError, match="Reset output missing required keys"):
#         reset_func._validate_reset_output(incomplete_output)
    
#     # Test wrong value type
#     wrong_type_output = {'output_int': "not_an_int", 'output_str': 'hello'}
#     with pytest.raises(TypeError, match="expected type int, got str"):
#         reset_func._validate_reset_output(wrong_type_output)