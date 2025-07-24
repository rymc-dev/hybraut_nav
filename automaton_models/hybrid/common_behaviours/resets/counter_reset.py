from automaton_models.hybrid.aci_interfaces import ResetInterface
from automaton.spec import IOSpec
from std_msgs.msg import Int32, Bool
from typing import Dict, Any

class CounterReset(ResetInterface):
    """
    Reset that increments or decrements a counter value.
    
    Useful for tracking attempts, iterations, or event counts in the system.
    """
    
    _init_input_spec = [
        IOSpec.create_io_spec("increment_value", int),
        IOSpec.create_io_spec("max_count", int),
        IOSpec.create_io_spec("reset_on_max", bool)
    ]
    
    _state_input_spec = [
        IOSpec.create_io_spec("current_count", Int32),
        IOSpec.create_io_spec("trigger_event", Bool)
    ]
    
    _reset_targets_spec = [
        IOSpec.create_io_spec("counter_value", int),
        IOSpec.create_io_spec("max_reached", bool)
    ]
    
    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:
        """evaluation runtime implementation"""        
        current_count = state_kwargs["current_count"].data
        new_count = current_count + self.increment_value
        
        # Check if max count is reached
        max_reached = new_count >= self.max_count
        
        # Reset to 0 if max reached and reset_on_max is True
        if max_reached and self.reset_on_max:
            new_count = 0
        elif max_reached:
            new_count = self.max_count
        
        return {
            'counter_value': new_count,
            'max_reached': max_reached
        }


def main():
    # Instantiate CounterReset with initialization parameters
    resetter = CounterReset(
        increment_value=2,
        max_count=5,
        reset_on_max=True
    )

    # Create a sample current state
    current_count_msg = Int32()
    current_count_msg.data = 4  # Starting just below max

    trigger_event_msg = Bool()
    trigger_event_msg.data = True  # Trigger is active

    # Call the reset logic
    reset_output = resetter(
        current_count=current_count_msg,
        trigger_event=trigger_event_msg
    )

    # Print the output
    print("Reset Output:")
    for key, value in reset_output.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
