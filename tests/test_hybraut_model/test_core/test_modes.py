from hybraut_models.core.modes import Mode, ModeRegistry
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


    

class TestModeRegistry: ...


if __name__ == "__main__":
    pytest.main([__file__])
