from automaton.core_interfaces import ResetInterface
from automaton.spec import IOSpec
from std_msgs.msg import Float64, Bool
from typing import Dict, Any

class TimerReset(ResetInterface):
    """
    Reset that initializes or resets a timer with a specific duration.
    
    Used for timeout behaviors, periodic actions, or time-based state transitions.
    """
    
    _init_input_spec = [
        IOSpec.create_io_spec("timer_duration", float),
        IOSpec.create_io_spec("auto_restart", bool)
    ]
    
    _state_input_spec = [
        IOSpec.create_io_spec("current_time", Float64),
        IOSpec.create_io_spec("timer_active", Bool)
    ]
    
    _reset_targets_spec = [
        IOSpec.create_io_spec("timer_start_time", float),
        IOSpec.create_io_spec("timer_end_time", float),
        IOSpec.create_io_spec("timer_running", bool)
    ]
    
    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:
        
        current_time = state_kwargs["current_time"].data
        start_time = current_time
        end_time = current_time + self.timer_duration
        
        return {
            'timer_start_time': start_time,
            'timer_end_time': end_time,
            'timer_running': True
        }

def main():
    # Instantiate the reset with init parameters
    timer_reset = TimerReset(
        timer_duration=5.0,
        auto_restart=True  # Currently unused but could affect future logic
    )

    # Simulate current state input
    current_time_msg = Float64()
    current_time_msg.data = 12.3  # Arbitrary "current time" value

    timer_active_msg = Bool()
    timer_active_msg.data = False  # Not used in current logic, placeholder

    # Call the reset logic
    reset_output = timer_reset(
        current_time=current_time_msg,
        timer_active=timer_active_msg
    )

    # Print the results
    print("Timer Reset Output:")
    for key, value in reset_output.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()