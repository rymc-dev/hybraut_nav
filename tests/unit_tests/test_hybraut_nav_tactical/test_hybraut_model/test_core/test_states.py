import pytest
from hybraut_models.core.states import State, StateRegistry
from geometry_msgs.msg import PoseStamped
from typing import Dict


@pytest.fixture
def state():
    return State(
        name="pose_stamped",
        topic="/state/pose_stamped",
        msg_type=PoseStamped,
        update_hz=10,
        timeout_sec=1.0,
    )


@pytest.fixture
def mock_states():
    return {
        f"mock_state_{i}": State(
            name=f"mock_state_{i}",
            topic=f"/state/mock_state_{i}",
            msg_type=PoseStamped,
            update_hz=10,
            timeout_sec=1.0,
        )
        for i in range(5)
    }


@pytest.fixture
def state_registry(mock_states):
    return StateRegistry(_components=mock_states)


class TestState:
    def test_initialization(self, state):
        assert state.get_name() == "pose_stamped"
        assert state.get_topic() == "/state/pose_stamped"
        assert state.get_msg_type() == PoseStamped
        assert state.get_update_hz() == 10
        assert state.get_timeout_sec() == 1.0
        assert state.get_current_state() is None
        assert state.get_max_errors() == 10
        assert state.get_error_count() == 0

    def test_update_state(self, state):
        with pytest.raises(TypeError):
            state.update_state("new_state")
        state.update_state(PoseStamped())
        assert state.get_current_state() == PoseStamped()

    def test_get_current_state_age(self, state):
        assert float("inf") == state.get_current_state_age()

        state.update_state(PoseStamped())

        assert int(state.get_current_state_age()) == 0
        import time

        time.sleep(1.0)
        assert int(state.get_current_state_age()) == 1

    def test_error_count(self, state):
        state.increment_error_count()
        assert state.get_error_count() == 1
        state._error_count = 5
        state.reset_error_count()
        assert state.get_error_count() == 0

    def test_str_repr(self, state):
        assert str(state) == (
            "State 'pose_stamped' on topic '/state/pose_stamped', message type: PoseStamped, errors: 0/10"
        )
        assert repr(state) == (
            "State(name='pose_stamped', topic='/state/pose_stamped', msg_type=PoseStamped, update_hz=10, timeout_sec=1.0, error_count=0, max_errors=10, current_state=None)"
        )


class TestStateRegistry:
    def test_initialization(self, mock_states):
        registry = StateRegistry(_components=mock_states)
        assert registry.get_num_states() == len(mock_states)
        assert registry.get_state_names() == list(mock_states.keys())
        states = registry.get_states_by_name(registry.get_state_names())
        assert states == mock_states

    def test_update_state(self, state_registry):
        with pytest.raises(TypeError):
            state_registry.update_state("mock_state_0", "invalid_state")
        state_registry.update_state("mock_state_0", PoseStamped())
        assert (
            state_registry.get_current_state_by_state_name("mock_state_0")
            == PoseStamped()
        )

    def test_update_states(self, state_registry):
        updates = {name: PoseStamped() for name in state_registry.get_state_names()}
        state_registry.update_states(updates)
        for name in state_registry.get_state_names():
            assert state_registry.get_current_state_by_state_name(name) == PoseStamped()

    def test_get_current_states(self, state_registry):
        current = state_registry.get_current_states_by_state_names(
            state_registry.get_state_names()
        )
        for name in state_registry.get_state_names():
            assert current[name] is None

    def test_get_state_age_by_name(self, state_registry):
        for name in state_registry.get_state_names():
            assert state_registry.get_state_age_by_state_name(name) is not None

        for name in state_registry.get_state_names():
            state_registry.update_state(name, PoseStamped())
            assert int(state_registry.get_state_age_by_state_name(name)) == 0

        import time

        time.sleep(1.0)
        for name in state_registry.get_state_names():
            assert int(state_registry.get_state_age_by_state_name(name)) == 1

    def test_get_current_state(self, state_registry):
        for name in state_registry.get_state_names():
            assert state_registry.get_current_state_by_state_name(name) is None

    def test_str_repr(self, state_registry):
        assert str(state_registry) == (
            "StateRegistry with 5 states: mock_state_0, mock_state_1, mock_state_2, mock_state_3, mock_state_4"
        )
        assert repr(state_registry) == (
            "StateRegistry(num_states=5, state_names=['mock_state_0', 'mock_state_1', 'mock_state_2', 'mock_state_3', 'mock_state_4'])"
        )


if __name__ == "__main__":
    pytest.main([__file__])
