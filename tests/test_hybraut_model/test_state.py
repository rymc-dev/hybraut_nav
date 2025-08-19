from hybraut_model.states import State, StateRegistry
import pytest
from geometry_msgs.msg import PoseStamped


# @pytest.fixture
def sample_state():
    state: State = State(
        name="pose_stamped",
        topic="/state/pose_stamped",
        msg_type=PoseStamped(),
        update_hz=10,
        timeout_sec=1.0,
    )

    return state


class TestState:
    def test_state_initialization_and_attributes(self, sample_state):
        state: State = sample_state
        assert state._name == "pose_stamped"
        assert state._topic == "/state/pose_stamped"
        assert state._msg_type == PoseStamped()
        assert state._update_hz == 10
        assert state._timeout_sec == 1.0
        assert state._current_state is None
        assert state._max_errors == 10
        assert state._error_count == 0
        assert state._last_update == None

    def test_update_state(self, sample_state):
        state: State = sample_state
        state.update_state("new_state")
        assert state._current_state == "new_state"

    def test_reset_error_count(self, sample_state):
        state: State = sample_state
        state._error_count = 5
        assert state._error_count == 5
        state.reset_error_count()
        assert state._error_count == 0

    def test_increment_error_count(self, sample_state):
        state: State = sample_state
        state.increment_error_count()
        assert state._error_count == 1

    # def test__str__(self, sample_state):
    #     state: State = sample_state
    #     assert str(state) == "State(pose_stamped)"

    # def test__repr__(self, sample_state): ...

    # def test_info(self, sample_state):
    #     state: State = sample_state
    #     assert state.info() == {
    #         "name": "pose_stamped",
    #         "topic": "/state/pose_stamped",
    #         "msg_type": PoseStamped(),
    #         "update_hz": 10,
    #         "timeout_sec": 1.0,
    #         "current_state": None,
    #         "max_errors": 10,
    #         "error_count": 0,
    #         "last_update": None,
    #     }

    def test_current_state(self, sample_state):
        state: State = sample_state
        state.update_state("new_state")
        assert state.current_state == "new_state"


# if __name__ == "__main__":
#     TestState().test_state_initialization_and_attributes(sample_state())
#     TestState().test_update_state(sample_state())
#     TestState().test_reset_error_count(sample_state())
#     TestState().test_increment_error_count(sample_state())
#     # TestState().test__str__(sample_state())
#     # TestState().test__repr__(sample_state())
#     # TestState().test_info(sample_state())
#     TestState().test_current_state(sample_state())


# class TestStateRegistry:
#     def test_state_registration_initialization(): ...


if __name__ == "__main__":
    pytest.main([__file__])
