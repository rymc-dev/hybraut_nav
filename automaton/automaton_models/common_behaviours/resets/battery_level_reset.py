from automaton_models.hybrid.aci_interfaces import ResetInterface
from automaton.spec import IOSpec
from std_msgs.msg import Float64, Int32
from typing import Dict, Any


class BatteryLevelReset(ResetInterface):
    """
    Reset that adjusts system behavior based on battery level changes.
    
    Modifies power management settings, performance limits, and safety
    behaviors when battery level crosses certain thresholds.
    """
    
    _init_input_spec = [
        IOSpec.create_io_spec("low_battery_threshold", float),
        IOSpec.create_io_spec("critical_battery_threshold", float),
        IOSpec.create_io_spec("power_save_factor", float)
    ]
    
    _state_input_spec = [
        IOSpec.create_io_spec("battery_level", Float64),
        IOSpec.create_io_spec("current_power_mode", Int32)
    ]
    
    _reset_targets_spec = [
        IOSpec.create_io_spec("power_save_mode", bool),
        IOSpec.create_io_spec("max_performance_factor", float),
        IOSpec.create_io_spec("battery_status", int),
        IOSpec.create_io_spec("return_to_base_required", bool)
    ]
    
    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:
        
        battery_level = state_kwargs["battery_level"].data
        
        # Determine battery status and required actions
        if battery_level <= self.critical_battery_threshold:
            battery_status = 2  # Critical
            power_save_mode = True
            max_performance_factor = self.power_save_factor * 0.5
            return_to_base_required = True
        elif battery_level <= self.low_battery_threshold:
            battery_status = 1  # Low
            power_save_mode = True
            max_performance_factor = self.power_save_factor
            return_to_base_required = False
        else:
            battery_status = 0  # Normal
            power_save_mode = False
            max_performance_factor = 1.0
            return_to_base_required = False
        
        return {
            'power_save_mode': power_save_mode,
            'max_performance_factor': max_performance_factor,
            'battery_status': battery_status,
            'return_to_base_required': return_to_base_required
        }
    

def main():
    # Instantiate the BatteryLevelReset with initialization parameters
    battery_reset = BatteryLevelReset(
        low_battery_threshold=30.0,
        critical_battery_threshold=10.0,
        power_save_factor=0.7
    )

    # Create test cases with various battery levels and current power modes
    test_cases = [
        {"battery_level": 50.0, "current_power_mode": 0},  # Normal
        {"battery_level": 25.0, "current_power_mode": 1},  # Low battery
        {"battery_level": 5.0, "current_power_mode": 1},   # Critical battery
    ]

    for i, case in enumerate(test_cases, 1):
        battery_level_msg = Float64(data=case["battery_level"])
        current_power_mode_msg = Int32(data=case["current_power_mode"])

        output = battery_reset(
            battery_level=battery_level_msg,
            current_power_mode=current_power_mode_msg
        )

        print(f"Test case {i}: Battery level = {case['battery_level']}%")
        for key, value in output.items():
            print(f"  {key}: {value}")
        print()

if __name__ == "__main__":
    main()