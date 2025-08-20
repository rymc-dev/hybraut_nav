""" 
Test Suite for 
"""

from hybraut_models.core.modes import Mode, ModeRegistry
from unittest.mock import MagicMock
import pytest


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
    # Fake Mode objects with mocked methods
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
    """ 
    test suite for the hybraut_models.core Modes
    """

    def test_mode_initialization_and_attributes(self, sample_mode):
        """ 
        tests the mode initialization and attributes
        """
        mode: Mode = sample_mode
        assert mode.get_id() == 0
        assert mode.get_name() == "Sample Mode"
        assert mode.get_dynamics_ref() == "sample_dynamics"
        assert mode.get_invariant_refs() == ["always_holds"]
        assert mode.get_transition_refs() == ["tick_transition"]
        assert mode.get_description() == "Sample Mode Description"
        assert mode.get_entry_actions() == []
        assert mode.get_exit_actions() == []
        assert mode.get_is_goal_mode() is False

    def test_on_enter(_, sample_mode):
        """ 
        tests the on_enter function of the on_enter function
        """
        worked = {"flag1": False, "flag2": False}  # use a dict to allow mutation in closure
        from hybraut_models.ctx import EvaluationContext

        def dummy_on_enter(mode, ctx: EvaluationContext):
            worked["flag1"] = True

        def dummy_on_enter1(mode, ctx: EvaluationContext):
            worked["flag2"] = True

        sample_mode._entry_actions = [dummy_on_enter, dummy_on_enter1]
        sample_mode.on_enter(None)

        assert worked["flag1"]
        assert worked["flag2"]

    def test_on_exit(_, sample_mode):
        """
        tests the on_exit functionality of the mode class
        """
        worked = {"flag1": False, "flag2": False}  # use a dict to allow mutation in closure
        from hybraut_models.ctx import EvaluationContext

        def dummy_on_exit_1(mode, ctx: EvaluationContext):
            worked["flag1"] = True

        def dummy_on_exit_2(mode, ctx: EvaluationContext):
            worked["flag2"] = True

        sample_mode._exit_actions = [dummy_on_exit_1, dummy_on_exit_2]
        sample_mode.on_exit(None)

        assert worked["flag1"]
        assert worked["flag2"]

    def test_get_transition_refs_and_priorities(self, sample_mode):
        """ 
        test the getter for transition_refs and their associated priorities
        """
        mode: Mode = sample_mode
        assert mode.get_transition_refs_and_priorities() == {
            0: "tick_transition"
        }

    def test__repr__(self, sample_mode):
        """ 
        test the __repr__ representation of the class
        """
        execpted = (
            "Mode(id=0, name='Sample Mode', dynamics_ref='sample_dynamics', invariant_refs=['always_holds'], description='Sample Mode Description', transition_refs=[0], entry_actions=[], exit_actions=[], is_goal_mode=False)"
        )
        assert repr(sample_mode) == execpted

    def test__str__(self, sample_mode):
        """ 
        Test the string represnetation of the mode class
        """
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

        assert expected == str(sample_mode)

class TestModeRegistry:
    def test_build_graph(self, registry):
        assert registry._mode_graph == {
            0: [1, 2],
            1: [2],
            2: [],
        }

    def test_get_reachable_modes(self, registry, sample_modes):
        reachable_from_0 = registry.get_reachable_modes(0)
        ids = [m.get_id() for m in reachable_from_0]
        assert set(ids) == {1, 2}

        reachable_from_1 = registry.get_reachable_modes(1)
        ids = [m.get_id() for m in reachable_from_1]
        assert ids == [2]

        reachable_from_2 = registry.get_reachable_modes(2)
        assert reachable_from_2 == []

    def test_validate_mode_connectivity(self, registry):
        assert registry.validate_mode_connectivity() is True

    def test_get_mode_and_is_mode(self, registry, sample_modes):
        assert registry.get_mode(0) == sample_modes[0]
        assert registry.get_mode(999) is None
        assert registry.is_mode(1) is True
        assert registry.is_mode(999) is False

    def test_get_mode_ids(self, registry):
        ids = registry.get_mode_ids()
        assert set(ids) == {0, 1, 2}

    def test_get_reachable_mode_ids(self, registry):
        assert registry.get_reachable_mode_ids(0) == [1, 2]
        assert registry.get_reachable_mode_ids(2) == []

    def test_is_to_mode_reachable_from(self, registry):
        assert registry.is_to_mode_reachable_from(0, 1) is True
        assert registry.is_to_mode_reachable_from(0, 99) is False

    # def test_str_and_repr(self, registry):
    #     s = str(registry)
    #     assert "ModeRegistry with 3 modes" in s
    #     assert "Mode 0: Mode0 -> [1, 2]" in s
    #     assert "Mode 1: Mode1 -> [2]" in s
    #     assert "Mode 2: Mode2 -> [None" not in s  # should say None when empty

    #     r = repr(registry)
    #     assert "ModeRegistry(modes=" in r
    #     assert "graph=" in r


if __name__ == "__main__":
    pytest.main([__file__])
