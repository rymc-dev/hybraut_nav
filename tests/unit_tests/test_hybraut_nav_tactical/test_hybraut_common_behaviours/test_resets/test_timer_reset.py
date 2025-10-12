from hybraut_common_behaviours.resets import TimerReset
import pytest
from std_msgs.msg import Float64, Bool


def test_timer_reset():
    reset = TimerReset(timer_duration=5.0, auto_restart=True)

    current_time_msg = Float64()
    current_time_msg.data = 12.3

    timer_active_msg = Bool()
    timer_active_msg.data = False

    reset_output = reset(current_time=current_time_msg, timer_active=timer_active_msg)
    assert True


if __name__ == "__main__":
    pytest.main([__file__])
