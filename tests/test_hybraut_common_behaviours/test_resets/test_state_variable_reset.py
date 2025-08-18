from hybraut_common_behaviours.resets import StateVariableReset
import pytest
from std_msgs.msg import Bool


def test_state_variable_reset():
    # Create an instance of StateVariableReset

    variable_updates = {"speed": 0, "position": (0, 0)}
    conditional_updates = {"emergency_stop": True, "speed": 0}

    reset = StateVariableReset(
        variable_updates=variable_updates, conditional_updates=conditional_updates
    )

    current_state = {
        "speed": 5,
        "position": (10, 10),
        "battery": 90,
        "emergency_stop": False,
    }

    trigger_false = Bool(data=False)
    trigger_true = Bool(data=True)

    reset_result_no_trigger = reset(
        current_state=current_state, trigger_condition=trigger_false
    )

    print(reset_result_no_trigger)

    reset_result_trigger = reset(
        current_state=current_state, trigger_condition=trigger_true
    )

    print(reset_result_trigger)


if __name__ == "__main__":
    pytest.main([__file__])
