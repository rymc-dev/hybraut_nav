from hybraut_models.core.transitions import Transition, TransitionRegistry
from hybraut_models.const.urgency import UrgencyEnums
from hybraut_models.ctx.evaluation_context import EvaluationContext
import pytest


@pytest.fixture
def transition_fixture():
    return Transition(
        name="SampleTransition",
        target_mode=1,
        guard_refs=["guard_1", "guard_2"],
        reset_refs=["reset_1", "reset_2"],
        urgency=UrgencyEnums.EAGER,
        metadata={"info": "this is a sample transition"},
    )


@pytest.fixture
def mock_ctx_fixture():

    EvaluationContext()


class TestTransition:
    """
    test suite for Transition

    we execute several tests covering the functionalites of the Transition class
    """

    def test_transition_initialization_and_attributes(
        self, transition_fixture: Transition
    ):
        assert transition_fixture.get_name() == "SampleTransition"
        assert transition_fixture.get_target_mode() == 1
        assert transition_fixture.get_guard_refs() == ["guard_1", "guard_2"]
        assert transition_fixture.get_reset_refs() == ["reset_1", "reset_2"]
        assert transition_fixture.get_urgency() == UrgencyEnums.EAGER
        assert transition_fixture.get_metadata() == {
            "info": "this is a sample transition"
        }

    def test_evaluate_transition(
        self, transition_fixture: Transition, ctx_fixture: EvaluationContext
    ):
        pass

    def test_string_representations(self, transition_fixture: Transition):
        assert (
            str(transition_fixture)
            == "Transition 'SampleTransition' -> Mode 1 | Guards: ['guard_1', 'guard_2'] | Resets: ['reset_1', 'reset_2'] | Urgency: UrgencyEnums.EAGER"
        )
        assert (
            repr(transition_fixture)
            == "Transition(name='SampleTransition', target_mode=1, guards=['guard_1', 'guard_2'], resets=['reset_1', 'reset_2'], urgency=UrgencyEnums.EAGER)"
        )


class TestTransitionRegistry: ...


if __name__ == "__main__":
    pytest.main([__file__])
