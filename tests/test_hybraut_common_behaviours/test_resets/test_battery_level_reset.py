from hybraut_common_behaviours.resets import BatteryLevelReset
import pytest

from std_msgs.msg import Float64, Int32, Bool
from typing import Dict, Any


test_cases = [
    {"battery_level": 50.0, "current_power_mode": 0},  # Normal
    {"battery_level": 25.0, "current_power_mode": 1},  # Low battery
    {"battery_level": 5.0, "current_power_mode": 1},  # Critical battery
]


@pytest.mark.parametrize(
    "battery_level, current_power_mode, expected_outputs",
    [
        (
            50.0,
            0,
            {
                "power_save_mode": Bool(_data=False),
                "max_performance_factor": Float64(_data=1.0),
                "battery_status": Int32(_data=0),
                "return_to_base_required": Bool(_data=False),
            },
        ),
        (
            25.0,
            1,
            {
                "power_save_mode": Bool(_data=True),
                "max_performance_factor": Float64(_data=0.7),
                "battery_status": Int32(_data=1),
                "return_to_base_required": Bool(_data=False),
            },
        ),
        (
            5.0,
            1,
            {
                "power_save_mode": Bool(_data=True),
                "max_performance_factor": Float64(_data=0.35),  # 0.7 * 0.5
                "battery_status": Int32(_data=2),
                "return_to_base_required": Bool(_data=True),
            },
        ),
    ],
    ids=["Normal", "Low Battery", "Critical Battery"],
)
def test_battery_level_reset(
    battery_level, current_power_mode: int, expected_outputs: Dict[str, Any]
):
    battery_reset = BatteryLevelReset(
        low_battery_threshold=30.0,
        critical_battery_threshold=10.0,
        power_save_factor=0.7,
    )


if __name__ == "__main__":
    pytest.main([__file__])
