import pytest
from unittest.mock import Mock, patch
from hybraut_models.core.guards import GuardWrapper, GuardRegistry
from hybraut_models.ctx import EvaluationContext
from hybraut_aci import GuardInterface, IOSpec
from hybraut_interfaces.msg import GuardEvaluationMSG


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
    guards = {}
    for i in range(5):
        mock_guard = Mock(spec=DummyGuard)
        mock_guard._evaluate.return_value = GuardEvaluationMSG()
        guards[f"guard_{i}"] = mock_guard
    return guards


@pytest.fixture
def guard_registry_fixture(mock_guards):
    registry = GuardRegistry()
    registry._components = mock_guards
    return registry


class TestGuardWrapper:
    def test_initialization_and_attributes(self, guard_wrapper_fixture):
        assert guard_wrapper_fixture.get_guard_name() == "dummy"
        assert guard_wrapper_fixture.get_initialization_configuration() == {
            "threshold": 10.0
        }
        assert (
            guard_wrapper_fixture.get_initialization_configuration_names_and_types()
            == {"threshold": float}
        )
        assert guard_wrapper_fixture.get_state_configuration_names_and_types() == {
            "x": float,
            "y": float,
        }

    def test_evaluate_success(self, guard_wrapper_fixture):
        with patch("hybraut_models.ctx.EvaluationContext") as MockEvalCtx:
            MockEvalCtx.return_value.get_state_values.return_value = {
                "x": 10.0,
                "y": 2.0,
            }
            ctx = MockEvalCtx()
            msg = guard_wrapper_fixture(ctx)
        assert isinstance(msg, GuardEvaluationMSG)
        assert msg.guard_name == "dummy"
        assert msg.guard_evaluation is True
        assert not msg.error
        assert msg.message == ""

    def test_exception_no_evaluation_context(self, guard_wrapper_fixture):
        ctx = Mock(spec=EvaluationContext)
        msg = guard_wrapper_fixture._evaluate(ctx)
        assert msg.guard_name == "dummy"
        assert msg.error is True

    def test_string_representation(self, guard_wrapper_fixture):
        assert (
            str(guard_wrapper_fixture) == "GuardWrapper(name=dummy, class=DummyGuard)"
        )
        assert (
            repr(guard_wrapper_fixture)
            == "<GuardWrapper name='dummy', class=DummyGuard, initialized=True>"
        )


class TestGuardRegistry:
    def test_initialization_and_attributes(self, guard_registry_fixture):
        assert guard_registry_fixture.get_num_guards() == 5
        assert set(guard_registry_fixture.get_guard_names()) == {
            "guard_0",
            "guard_1",
            "guard_2",
            "guard_3",
            "guard_4",
        }

    @pytest.mark.parametrize(
        "name,exists",
        [
            ("guard_2", True),
            ("nonexistent", False),
        ],
    )
    def test_get_guard_by_name(self, guard_registry_fixture, name, exists):
        guard = guard_registry_fixture.get_guard_by_name(name)
        if exists:
            assert guard is guard_registry_fixture._components[name]
        else:
            assert guard is None

    def test_get_guards_by_names(self, guard_registry_fixture):
        names = ["guard_1", "guard_3"]
        guards = guard_registry_fixture.get_guards_by_names(names)
        assert guards == [
            guard_registry_fixture._components["guard_1"],
            guard_registry_fixture._components["guard_3"],
        ]
        guards = guard_registry_fixture.get_guards_by_names(["guard_0", "missing"])
        assert len(guards) == 1

    def test_evaluate_guard_by_name(self, guard_registry_fixture):
        with patch("hybraut_models.ctx.EvaluationContext") as MockEvalCtx:
            MockEvalCtx.return_value.get_state_values.return_value = {
                "x": 10.0,
                "y": 2.0,
            }
            ctx = MockEvalCtx()
            msg = guard_registry_fixture.evaluate_guard_by_name("guard_1", ctx=ctx)
        assert isinstance(msg, GuardEvaluationMSG)

    def test_evaluate_guards_by_name(self, guard_registry_fixture):
        with patch("hybraut_models.ctx.EvaluationContext") as MockEvalCtx:
            MockEvalCtx.return_value.get_state_values.return_value = {
                "x": 10.0,
                "y": 2.0,
            }
            ctx = MockEvalCtx()
            msg = guard_registry_fixture.evaluate_guards_by_name(
                guard_names=["guard_1", "guard_2"], ctx=ctx
            )
        assert len(msg) == 2
        assert all(isinstance(m, GuardEvaluationMSG) for m in msg)

    def test_string_representations(self, guard_registry_fixture):
        assert str(guard_registry_fixture) == (
            f"GuardRegistry(num_guards={guard_registry_fixture.get_num_guards()}, "
            f"guards={guard_registry_fixture.get_guard_names()})"
        )
        assert repr(guard_registry_fixture) == (
            "<GuardRegistry num_guards=5, guards={ guard_0: Mock, guard_1: Mock, guard_2: Mock, guard_3: Mock, guard_4: Mock }>"
        )


if __name__ == "__main__":
    pytest.main([__file__])
