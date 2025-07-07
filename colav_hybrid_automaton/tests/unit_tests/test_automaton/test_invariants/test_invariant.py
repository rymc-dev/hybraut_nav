# import pytest
# from colav_hybrid_automaton.automaton.invariants.invariant import InvariantABC

# def test_invariant_creation_and_calls():
#     class TestInvariant(InvariantABC):
#         """
#         This is a test of the invariant condition abstract class.
#         """
#         def __init__(self, **init_kwargs):
#             super().__init__(**init_kwargs)
#             self.x: float = init_kwargs.get('x')

#         def __call__(self, **state_kwargs):
#             return super().__call__(**state_kwargs)

#         def _validate_states(self, **state_kwargs):
#             if 'x' not in state_kwargs:
#                 raise ValueError("Missing state input 'x'")
#             if not isinstance(state_kwargs.get('x'), float):
#                 raise TypeError('x state input is invalid')

#         def _validate_initialization(self, **kwargs):
#             if 'x' not in kwargs:
#                 raise ValueError("Missing required parameter 'x'")
#             if not isinstance(kwargs.get('x'), float):
#                 raise TypeError('x is not valid type')

#     # Test valid creation
#     kwargs = {'x': 10.0}
#     invariant = TestInvariant(**kwargs)
#     assert invariant.is_initialized
#     assert invariant.x == 10.0

#     # Test valid call with correct state
#     kwargs = {'x':5.0 }
#     invariant.__call__(**kwargs)  # Should not raise

#     # Test call with invalid state type
#     kwargs = {'x':"not a float" }
#     with pytest.raises(TypeError):
#         invariant.__call__(kwargs)

#     # Test call with missing state input
#     with pytest.raises(ValueError):
#         invariant.__call__()

#     invariant_info = invariant.get_invariant_info()
#     assert invariant_info['class_name'] == 'TestInvariant'
#     assert invariant_info['module'] == 'test_invariant'
#     assert invariant_info['is_initialized'] == True
#     assert invariant_info['description'] == 'This is a test of the invariant condition abstract class.'

#     assert invariant.__str__() == "Invariant Function: TestInvariant"
#     assert invariant.__repr__() == "TestInvariant(initialized=True)"

# def test_invariant_invalid_initialization_missing_param():
#     class TestInvariant(Invariant):
#         def _validate_initialization(self, **kwargs):
#             if 'x' not in kwargs:
#                 raise ValueError("Missing required parameter 'x'")

#         def __call__(self, **state_kwargs):
#             return super().__call__(**state_kwargs)

#     with pytest.raises(ValueError):
#         TestInvariant()  # Missing 'x'

# def test_invariant_invalid_initialization_wrong_type():
#     class TestInvariant(Invariant):
#         def _validate_initialization(self, **kwargs):
#             if not isinstance(kwargs.get('x'), float):
#                 raise TypeError('x is not valid type')

#         def __call__(self, **state_kwargs):
#             return super().__call__(**state_kwargs)

#     with pytest.raises(TypeError):
#         TestInvariant(x="not a float")

# def test_invariant_call_before_init():
#     class TestInvariant(Invariant):
#         def __init__(self, **kwargs):
#             # Intentionally skip calling super().__init__ to simulate no init
#             self.is_initialized = False

#         def __call__(self, **state_kwargs):
#             return super().__call__(**state_kwargs)

#     invariant = TestInvariant()
#     with pytest.raises(RuntimeError):
#         invariant.__call__(x=1.0)
