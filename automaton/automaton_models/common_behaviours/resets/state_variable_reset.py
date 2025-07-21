from automaton_models.hybrid.aci_interfaces import ResetInterface
from automaton.spec import IOSpec
from std_msgs.msg import Bool
from typing import Dict, Any

class StateVariableReset(ResetInterface):
    """
    Generic reset for updating multiple state variables simultaneously.
    
    A flexible reset that can update various system state variables
    based on a configuration dictionary.
    """
    
    _init_input_spec = [
        IOSpec.create_io_spec("variable_updates", dict),
        IOSpec.create_io_spec("conditional_updates", dict)
    ]
    
    _state_input_spec = [
        IOSpec.create_io_spec("current_state", dict),
        IOSpec.create_io_spec("trigger_condition", Bool)
    ]
    
    _reset_targets_spec = [
        IOSpec.create_io_spec("updated_variables", dict),
        IOSpec.create_io_spec("update_timestamp", float)
    ]
    
    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:
        
        import time
        
        current_state = state_kwargs["current_state"]
        trigger_condition = state_kwargs["trigger_condition"].data
        
        # Start with current state
        updated_variables = current_state.copy()
        
        # Apply standard updates
        updated_variables.update(self.variable_updates)
        
        # Apply conditional updates if trigger is active
        if trigger_condition and self.conditional_updates:
            updated_variables.update(self.conditional_updates)
        
        return {
            'updated_variables': updated_variables,
            'update_timestamp': time.time()
        }
    

def main():
    # Define some sample updates
    variable_updates = {"speed": 0, "position": (0, 0)}
    conditional_updates = {"emergency_stop": True, "speed": 0}

    # Create an instance of the reset
    reset = StateVariableReset(variable_updates=variable_updates, conditional_updates=conditional_updates)

    # Create a mock current state
    current_state = {
        "speed": 5,
        "position": (10, 10),
        "battery": 90,
        "emergency_stop": False
    }

    # Simulate a trigger condition (using std_msgs/Bool)
    trigger_false = Bool(data=False)
    trigger_true = Bool(data=True)

    # Evaluate with trigger False (conditional updates should NOT apply)
    result_no_trigger = reset._evaluate(current_state=current_state, trigger_condition=trigger_false)
    print("Result with trigger_condition=False:")
    print(result_no_trigger)

    # Evaluate with trigger True (conditional updates SHOULD apply)
    result_with_trigger = reset._evaluate(current_state=current_state, trigger_condition=trigger_true)
    print("\nResult with trigger_condition=True:")
    print(result_with_trigger)

if __name__ == "__main__":
    main()