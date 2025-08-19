from hybraut_models.core.transitions import Transition, TransitionRegistry
from hybraut_models.constants.urgency import UrgencyEnums
import pytest


@pytest.fixture
def sample_transition():
    return Transition(
        _name="SampleTransition",
        _target_mode=1,
        _guard_refs=["guard_1", "guard_2"],
        _reset_refs=["reset_1", "reset_2"],
        _urgency=UrgencyEnums.EAGER,
        _metadata={"info": "this is a sample transition"},
    )


class TestTransition:
    """
    test suite for Transition

    we execute several tests covering the functionalites of the Transition class
    """

    def test_transition_initialization_and_attributes(self, sample_transition):
        transition: Transition = sample_transition
        assert transition.get_name() == "SampleTransition"
        assert transition.get_target_mode() == 1
        assert transition.get_guard_refs() == ["guard_1", "guard_2"]
        assert transition.get_reset_refs() == ["reset_1", "reset_2"]
        assert transition.get_urgency() == UrgencyEnums.EAGER
        assert transition.get_metadata() == {"info": "this is a sample transition"}

    def test_evaluate_transition(): ...

    def test__repr__(self): ...

    def test__str__(self): ...

    def text_execute_transition(self): ...


class TestTransitionRegistry: ...


if __name__ == "__main__":
    pytest.main([__file__])
