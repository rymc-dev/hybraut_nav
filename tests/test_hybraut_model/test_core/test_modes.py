from hybraut_models.core.modes import Mode, ModeRegistry
import pytest


@pytest.fixture
def sample_mode():
    return Mode(
        _id=0,
        _name="Sample Mode",
        _dynamics_ref="sample_dynamics",
        _invariant_refs=["always_holds"],
        _transition_refs=["tick_transition"],
        _description="Sample Mode Description",
    )


class TestMode:
    def test_mode_initialization_and_attributes(self, sample_mode):
        mode: Mode = sample_mode
        assert mode.get_id() == 0
        assert mode.get_name() == "Sample Mode"
        assert mode.get_dynamics_ref() == "sample_dynamics"
        assert mode.get_invariant_refs() == ["always_holds"]
        assert mode.get_transition_refs() == {0: "tick_transition"}
        assert mode.get_description() == "Sample Mode Description"
        assert mode.get_entry_actions() is None
        assert mode.get_exit_actions() is None
        assert mode.get_is_goal_mode() is False

    def test_on_enter(self):
        """this test has no functionality atm"""
        assert True

    def test_on_exit(self):
        """this function is still a stub"""
        assert True

    def test_get_transition_refs_and_priorities(self, sample_mode):
        sample_mode = sample_mode()
        assert sample_mode.get_transition_refs_and_priorities() == {
            0: "tick_transition"
        }


class TestModeRegistry: ...


if __name__ == "__main__":
    pytest.main([__file__])
