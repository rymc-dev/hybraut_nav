from hybraut_models.models.hybrid_automaton import HybridAutomaton
import pytest

from hybraut_models.core.modes import ModeRegistry
from hybraut_models.core.states import StateRegistry
from hybraut_models.core.guards import GuardRegistry
from hybraut_models.core.resets import ResetRegistry
from hybraut_models.core.dynamics import DynamicsRegistry
from hybraut_models.core.invariants import InvariantRegistry

from unittest.mock import Mock, MagicMock, patch

from hybraut_models.core.modes import ModeRegistry


@pytest.fixture
def mock_mode_registry_fixture():
    mock_instance = Mock(spec=ModeRegistry)
    return mock_instance


def mock_state_registry_fixture():
    mock_instance = Mock(spec=StateRegistry)
    return mock_instance


def mock_guard_registry_fixture():
    mock_instance: GuardRegistry = Mock(spec=GuardRegistry)
    from hybraut_interfaces.msg import GuardEvaluationMSG

    mock_instance.evaluate_guards_by_name.return_value = GuardEvaluationMSG()
    return mock_instance


def mock_reset_registry_fixture():
    mock_instance: ResetRegistry = Mock(spec=ResetRegistry)
    from hybraut_interfaces.msg import AutomatonReset

    mock_instance.evaluate_resets_by_names.return_value = AutomatonReset()
    return mock_instance


def mock_dynamics_registry_fixture():
    mock_instance: DynamicsRegistry = Mock(spec=DynamicsRegistry)
    from hybraut_interfaces.msg import AutomatonDynamicsEvaluation

    mock_instance.evaluate_dynamics_by_name.return_value = AutomatonDynamicsEvaluation()
    return mock_instance


def mock_invariant_registry_fixture():
    mock_instance = Mock(spec=InvariantRegistry)
    return mock_instance


@pytest.fixture
def hybrid_automaton_fixture(
    mock_mode_registry_fixture,
    mock_state_registry_fixture,
    mock_guard_registry_fixture,
    mock_reset_registry_fixture,
    mock_dynamics_registry_fixture,
    mock_invariant_registry_fixture,
):
    """
    generates an initialization of a HybridAutoaton instance
    """
    return HybridAutomaton(
        _name="sample_automaton",
        _description="a simple mock of a hybrid automaton for testing",
        _version="v0.0.1",
        _initial_mode="mode1",
        _goal_modes=["mode2", "mode3"],
        _modes=mock_mode_registry_fixture,
        _states=mock_state_registry_fixture,
        _guards=mock_guard_registry_fixture,
        _resets=mock_reset_registry_fixture,
        _dynamics=mock_dynamics_registry_fixture,
        _invariants=mock_invariant_registry_fixture,
    )


class TestHybridAutomaton:
    """
    test suite for automaton
    """

    def test_initialization_and_attributes(self, hybrid_automaton_fixture): ...

    def test_generate_evaluation_context(self, hybrid_automaton_fixture): ...

    def test_evaluate_invariants(self, hybrid_automaton_fixture): ...

    def test_evaluate_dynamics(self, hybrid_automaton_fixture): ...

    def test_perform_resets(self, hybrid_automaton_fixture): ...


if __name__ == "__main__":
    pytest.main([__file__])
