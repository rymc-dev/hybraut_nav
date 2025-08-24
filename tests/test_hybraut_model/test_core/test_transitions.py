from hybraut_models.core.transitions import Transition, TransitionRegistry
from hybraut_models.const.urgency import UrgencyEnums
from hybraut_models.ctx.evaluation_context import EvaluationContext
from hybraut_models.core.modes import ModeRegistry
from hybraut_models.core.states import StateRegistry
from hybraut_models.core.guards import GuardRegistry
from hybraut_models.core.resets import ResetRegistry
from hybraut_models.core.dynamics import DynamicsRegistry
from hybraut_models.core.invariants import InvariantRegistry

from hybraut_interfaces.msg import GuardEvaluationMSG

from hybraut_aci.core import GuardInterface
from hybraut_aci import IOSpec
from hybraut_interfaces.msg import TransitionEvaluationMSG, TransitionEvaluationsMSG

import pytest
from unittest.mock import Mock
from hybraut_models.core import GuardWrapper


# --- Mock classes for testing ---
class DummyGuard(GuardInterface):
    _init_input_spec = [IOSpec.create_io_spec("threshold", float)]
    _state_input_spec = [
        IOSpec.create_io_spec("x", float),
        IOSpec.create_io_spec("y", float),
    ]

    def _evaluate(self, **state_kwargs):
        return (state_kwargs.get("x", 10.0) + state_kwargs.get("y", 0.5)) > getattr(
            self, "threshold", 0.0
        )


@pytest.fixture
def guard_wrapper_fixture():
    return GuardWrapper(
        name="dummy", component_class=DummyGuard, configuration={"threshold": 10.0}
    )


@pytest.fixture
def mock_guards():
    return {
        f"guard_{i}": Mock(
            spec=DummyGuard,
            _evaluate=Mock(return_value=GuardEvaluationMSG(guard_evaluation=True)),
        )
        for i in range(5)
    }


@pytest.fixture
def guard_registry_fixture(mock_guards):
    registry = GuardRegistry()
    registry._components = mock_guards
    return registry


@pytest.fixture
def transition_fixture():
    return Transition(
        name="SampleTransition",
        target_mode=1,
        guard_refs=["guard_1", "guard_2"],
        reset_refs=["reset_1", "reset_2"],
        priority=1,
        urgency=UrgencyEnums.EAGER,
        metadata={"info": "this is a sample transition"},
    )


@pytest.fixture
def mock_ctx_fixture(guard_registry_fixture):
    mock_state_registry = Mock(spec=StateRegistry)
    mock_transition_registry = Mock(spec=TransitionRegistry)
    mock_mode_registry = Mock(spec=ModeRegistry)
    mock_reset_registry = Mock(spec=ResetRegistry)
    mock_dynamics_registry = Mock(spec=DynamicsRegistry)
    mock_invariant_registry = Mock(spec=InvariantRegistry)
    import time

    return EvaluationContext(
        current_mode=0,
        stamp=time.time(),
        metadata={},
        mode_registry=mock_mode_registry,
        transition_registry=mock_transition_registry,
        states_registry=mock_state_registry,
        guard_registry=guard_registry_fixture,
        reset_registry=mock_reset_registry,
        invariant_registry=mock_invariant_registry,
    )


class TestTransition:
    def test_transition_initialization_and_attributes(self, transition_fixture):
        assert transition_fixture.get_name() == "SampleTransition"
        assert transition_fixture.get_target_mode() == 1
        assert transition_fixture.get_guard_refs() == ["guard_1", "guard_2"]
        assert transition_fixture.get_reset_refs() == ["reset_1", "reset_2"]
        assert transition_fixture.get_urgency() == UrgencyEnums.EAGER
        assert transition_fixture.get_metadata() == {
            "info": "this is a sample transition"
        }

    def test_evaluate_transition(self, transition_fixture, mock_ctx_fixture):
        msg = transition_fixture.evaluate_transition(mock_ctx_fixture)
        assert isinstance(msg, TransitionEvaluationMSG)
        assert msg.name == "SampleTransition"
        assert msg.target_mode == 1
        assert msg.priority == 1
        assert len(msg.guards) == 2
        assert msg._should_transition is True
        assert msg._expected_resets == ["reset_1", "reset_2"]

    def test_string_representations(self, transition_fixture):
        assert str(transition_fixture) == (
            "Transition 'SampleTransition' -> Mode 1 | Guards: ['guard_1', 'guard_2'] | Resets: ['reset_1', 'reset_2'] | Urgency: UrgencyEnums.EAGER"
        )
        assert repr(transition_fixture) == (
            "Transition(name='SampleTransition', target_mode=1, guards=['guard_1', 'guard_2'], resets=['reset_1', 'reset_2'], urgency=UrgencyEnums.EAGER)"
        )


from unittest.mock import MagicMock


@pytest.fixture
def mock_guard_pass():
    """Mock guard that always passes."""
    guard = MagicMock(spec=GuardWrapper)
    eval_msg = GuardEvaluationMSG()
    eval_msg.guard_evaluation = True
    eval_msg.error = False
    eval_msg.message = "guard passed"
    guard._evaluate.return_value = eval_msg
    return guard


@pytest.fixture
def mock_guard_fail():
    """Mock guard that always fails."""
    guard = MagicMock(spec=GuardWrapper)
    eval_msg = GuardEvaluationMSG()
    eval_msg.guard_evaluation = False
    eval_msg.error = False
    eval_msg.message = "guard failed"
    guard._evaluate.return_value = eval_msg
    return guard


@pytest.fixture
def evaluation_context(mock_guard_pass, mock_guard_fail):
    """Minimal fake evaluation context with a guard registry."""
    ctx = EvaluationContext(
        stamp=0,
        metadata={},
        mode_registry=MagicMock(),
        transition_registry=MagicMock(),
        states_registry=MagicMock(),
        guard_registry=MagicMock(),
        reset_registry=MagicMock(),
        invariant_registry=MagicMock(),
        current_mode=0,
    )

    # Patch guard registry to return mocks
    ctx.guard_registry.get_guards_by_names.return_value = [
        mock_guard_pass,
        mock_guard_fail,
    ]
    ctx.guard_registry.get_components_by_names.return_value = {
        "guard_pass": mock_guard_pass,
        "guard_fail": mock_guard_fail,
    }

    return ctx


class TestTransitionAndRegistry:
    def test_transition_evaluate_success(self, evaluation_context, mock_guard_pass):
        transition = Transition(
            name="T1",
            target_mode=1,
            guard_refs=["guard_pass"],
            reset_refs=["reset1"],
            priority=1,
            urgency=UrgencyEnums.EAGER,
        )

        evaluation_context.guard_registry.get_guards_by_names.return_value = [
            mock_guard_pass
        ]

        msg = transition.evaluate_transition(evaluation_context)

        assert msg.name == "T1"
        assert msg.target_mode == 1
        assert msg._should_transition is True
        assert not msg.error
        assert msg._expected_resets == ["reset1"]
        assert msg.guards[0].guard_evaluation is True

    def test_transition_evaluate_failure(self, evaluation_context, mock_guard_fail):
        transition = Transition(
            name="T2",
            target_mode=2,
            guard_refs=["guard_fail"],
            reset_refs=[],
            priority=2,
        )

        evaluation_context.guard_registry.get_guards_by_names.return_value = [
            mock_guard_fail
        ]

        msg = transition.evaluate_transition(evaluation_context)

        assert msg._should_transition is False
        assert not msg.error
        assert msg.guards[0].guard_evaluation is False

    # def test_registry_evaluate_multiple_transitions(
    #     self, evaluation_context, mock_guard_pass, mock_guard_fail
    # ):
    #     t1 = Transition("T1", 1, ["guard_pass"], ["reset1"], priority=1)
    #     t2 = Transition("T2", 2, ["guard_fail"], [], priority=2)

    #     registry = TransitionRegistry()
    #     registry._components = {"T1": t1, "T2": t2}

    #     transitions = {1: "T1", 2: "T2"}
    #     msg = registry.evaluate_transitions(transitions, evaluation_context)

    #     assert msg.current_mode == evaluation_context.current_mode
    #     assert len(msg.transition_evaluations) == 2

    #     # First transition should pass
    #     t1_eval = msg.transition_evaluations[0]
    #     assert t1_eval.name == "T1"
    #     assert t1_eval.should_transition is True

    #     # Second transition should fail
    #     t2_eval = msg.transition_evaluations[1]
    #     assert t2_eval.name == "T2"
    #     assert t2_eval.should_transition is False


if __name__ == "__main__":
    pytest.main([__file__])
