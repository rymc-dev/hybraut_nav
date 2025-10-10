from hybraut_aci import ResetInterface, IOSpec
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from typing import Dict, Any


class EmergencyStopReset(ResetInterface):
    """
    Reset that immediately stops robot motion and sets emergency flags.

    Used when transitioning to an emergency or fault mode where the robot
    must cease all motion and enter a safe state.
    """

    _init_input_spec = [
        IOSpec.create_io_spec("stop_timeout", float),
        IOSpec.create_io_spec("emergency_code", int),
    ]

    _state_input_spec = [
        IOSpec.create_io_spec("current_velocity", Twist),
        IOSpec.create_io_spec("emergency_detected", Bool),
    ]

    _reset_targets_spec = [
        IOSpec.create_io_spec("target_velocity", tuple),
        IOSpec.create_io_spec("emergency_active", bool),
        IOSpec.create_io_spec("emergency_timestamp", float),
        IOSpec.create_io_spec("last_emergency_code", int),
    ]

    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:
        import time

        # Set all velocities to zero
        target_velocity = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # linear + angular

        return {
            "target_velocity": target_velocity,
            "emergency_active": True,
            "emergency_timestamp": time.time(),
            "last_emergency_code": self.emergency_code,
        }


def main():
    # Create instance of EmergencyStopReset with init parameters
    resetter = EmergencyStopReset(stop_timeout=1.0, emergency_code=42)

    # Create dummy state inputs
    current_velocity = Twist()
    current_velocity.linear.x = 1.0
    current_velocity.angular.z = 0.5
    emergency_detected = Bool(data=True)

    # Call the reset logic
    reset_outputs = resetter(
        current_velocity=current_velocity, emergency_detected=emergency_detected
    )

    # Display the outputs
    print("Reset Outputs:")
    for key, value in reset_outputs.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
