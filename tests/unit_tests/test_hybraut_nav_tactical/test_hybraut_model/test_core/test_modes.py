import pytest
from unittest.mock import MagicMock
from hybraut_models.core.modes import Mode, ModeRegistry


@pytest.fixture
def sample_mode():
    return Mode(
        id=0,
        name="Sample Mode",
        dynamics_ref="sample_dynamics",
        invariant_refs=["always_holds"],
        transition_refs={0: "tick_transition"},
        description="Sample Mode Description",
    )


@pytest.fixture
def sample_modes():
    mode0 = MagicMock()
    mode0.get_id.return_value = 0
    mode0.get_name.return_value = "Mode0"
    mode0.get_transition_refs_and_priorities.return_value = {1: None, 2: None}

    mode1 = MagicMock()
    mode1.get_id.return_value = 1
    mode1.get_name.return_value = "Mode1"
    mode1.get_transition_refs_and_priorities.return_value = {2: None}

    mode2 = MagicMock()
    mode2.get_id.return_value = 2
    mode2.get_name.return_value = "Mode2"
    mode2.get_transition_refs_and_priorities.return_value = {}

    return {0: mode0, 1: mode1, 2: mode2}


@pytest.fixture
def registry(sample_modes):
    return ModeRegistry(sample_modes)


class TestMode:
    def test_initialization(self, sample_mode):
        mode = sample_mode
        assert mode.get_id() == 0
        assert mode.get_name() == "Sample Mode"
        assert mode.get_dynamics_ref() == "sample_dynamics"
        assert mode.get_invariant_refs() == ["always_holds"]
        assert mode.get_transition_refs() == ["tick_transition"]
        assert mode.get_description() == "Sample Mode Description"
        assert mode.get_entry_actions() == []
        assert mode.get_exit_actions() == []
        assert not mode.get_is_goal_mode()

    def test_on_enter(self, sample_mode):
        worked = {"flag1": False, "flag2": False}
        from hybraut_models.ctx import EvaluationContext

        def dummy1(mode, ctx):
            worked["flag1"] = True

        def dummy2(mode, ctx):
            worked["flag2"] = True

        sample_mode._entry_actions = [dummy1, dummy2]
        sample_mode.on_enter(None)
        assert all(worked.values())

    def test_on_exit(self, sample_mode):
        worked = {"flag1": False, "flag2": False}
        from hybraut_models.ctx import EvaluationContext

        def dummy1(mode, ctx):
            worked["flag1"] = True

        def dummy2(mode, ctx):
            worked["flag2"] = True

        sample_mode._exit_actions = [dummy1, dummy2]
        sample_mode.on_exit(None)
        assert all(worked.values())

    def test_transition_refs_and_priorities(self, sample_mode):
        assert sample_mode.get_transition_refs_and_priorities() == {
            0: "tick_transition"
        }

    def test_repr(self, sample_mode):
        expected = (
            "Mode(id=0, name='Sample Mode', dynamics_ref='sample_dynamics', "
            "invariant_refs=['always_holds'], description='Sample Mode Description', "
            "transition_refs=[0], entry_actions=[], exit_actions=[], is_goal_mode=False)"
        )
        assert repr(sample_mode) == expected

    def test_str(self, sample_mode):
        expected = (
            "Mode 'Sample Mode' (ID: 0)\n"
            "  Dynamics: sample_dynamics\n"
            "  Invariants: always_holds\n"
            "  Description: Sample Mode Description\n"
            "  Entry actions: None\n"
            "  Exit actions: None\n"
            "  Goal mode: False\n"
            "  Transitions: [0]"
        )
        assert str(sample_mode) == expected


class TestModeRegistry:
    def test_build_graph(self, registry):
        assert registry._mode_graph == {0: [1, 2], 1: [2], 2: []}

    def test_get_reachable_modes(self, registry, sample_modes):
        assert set(m.get_id() for m in registry.get_reachable_modes(0)) == {1, 2}
        assert [m.get_id() for m in registry.get_reachable_modes(1)] == [2]
        assert registry.get_reachable_modes(2) == []

    def test_validate_connectivity(self, registry):
        assert registry.validate_mode_connectivity()

    def test_get_mode_and_is_mode(self, registry, sample_modes):
        assert registry.get_mode(0) == sample_modes[0]
        assert registry.get_mode(999) is None
        assert registry.is_mode(1)
        assert not registry.is_mode(999)

    def test_get_mode_ids(self, registry):
        assert set(registry.get_mode_ids()) == {0, 1, 2}

    def test_get_reachable_mode_ids(self, registry):
        assert registry.get_reachable_mode_ids(0) == [1, 2]
        assert registry.get_reachable_mode_ids(2) == []

    def test_is_to_mode_reachable_from(self, registry):
        assert registry.is_to_mode_reachable_from(0, 1)
        assert not registry.is_to_mode_reachable_from(0, 99)

    def test_str_and_repr(self, registry):
        expected_str = (
            "ModeRegistry with 3 modes\n"
            "Mode 0: Mode0 -> [1, 2]\n"
            "Mode 1: Mode1 -> [2]\n"
            "Mode 2: Mode2 -> [None]"
        )
        assert str(registry) == expected_str
        assert (
            repr(registry)
            == "ModeRegistry(modes=[0, 1, 2], graph={0: [1, 2], 1: [2], 2: []})"
        )


if __name__ == "__main__":
    pytest.main([__file__])
