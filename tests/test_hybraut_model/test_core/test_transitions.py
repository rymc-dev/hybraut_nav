from hybraut_models.core.transitions import Transition, TransitionRegistry
from hybraut_models.const.urgency import UrgencyEnums
from hybraut_models.ctx.evaluation_context import EvaluationContext
from hybraut_models.core.modes import ModeRegistry
from hybraut_models.core.states import StateRegistry
from hybraut_models.core.guards import GuardRegistry
from hybraut_models.core.resets import ResetRegistry
from hybraut_models.core.dynamics import DynamicsRegistry
from hybraut_models.core.invariants import InvariantRegistry

from hybraut_interfaces.msg import TransitionEvaluationMSG, TransitionEvaluationsMSG


import pytest
from unittest.mock import Mock


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
    """"""
    mock_state_registry = Mock(spec=StateRegistry)
    mock_guard_registry = Mock(spec=GuardRegistry)
    mock_transition_registry = Mock(spec=TransitionRegistry)
    mock_mode_registry = Mock(spec=ModeRegistry)
    mock_reset_registry = Mock(spec=ResetRegistry)
    mock_dynamics_registry = Mock(spec=DynamicsRegistry)
    mock_invariant_registry = Mock(spec=InvariantRegistry)

    import time

    ctx = EvaluationContext(
        current_mode=0,
        stamp=time.time(),
        metadata={},
        mode_registry=mock_mode_registry,
        transition_registry=mock_transition_registry,
        states_registry=mock_state_registry,
        guard_registry=mock_guard_registry,
        reset_registry=mock_reset_registry,
        dynamics_registry=mock_dynamics_registry,
        invariant_registry=mock_invariant_registry,
    )

    return ctx


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
        # need to test the guard class first.
        transition_fixture.evaluate_transition(ctx_fixture)

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
