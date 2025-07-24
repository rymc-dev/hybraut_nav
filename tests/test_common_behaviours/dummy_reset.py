
from ...automaton_models.hybraut_model.aci_interfaces.reset_interface import ResetABC
from nodes._internal.types import InputSpec
from automaton_interfaces.msg import TestState

class DummyReset(ResetABC):
    """
    this is a simple dummy reset which will simply add a 1
    to the velocity for the TestState 
    """

    _state_input_spec = [
        InputSpec(name='test_state', type=TestState)
    ]
    _reset_targets_spec = [
        InputSpec(name='test_state', type=TestState)
    ]

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)
        test_state: TestState = state_kwargs['test_state']

        test_state.velocity = test_state.velocity + 1.0
        reset_output = {'test_state': test_state}
        self._validate_reset_output(reset_output)
        return reset_output

