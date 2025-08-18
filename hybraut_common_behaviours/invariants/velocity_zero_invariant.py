from hybraut_aci import InvariantInterface, IOSpec
from geometry_msgs.msg import TwistStamped
import math


class VelocityNonZeroInvariant(InvariantInterface):
    _init_input_spec = [IOSpec.create_io_spec("min_velocity", float)]
    _state_input_spec = [IOSpec.create_io_spec("velocity", TwistStamped)]

    def _evaluate(self, **state_kwargs) -> bool:
        """Evaluate whether the velocity magnitude is above the minimum threshold."""
        velocity_msg: TwistStamped = state_kwargs["velocity"]
        linear = velocity_msg.twist.linear

        # Compute full 3D speed magnitude
        speed = math.sqrt(linear.x**2 + linear.y**2 + linear.z**2)

        return speed >= self.min_velocity


def main():
    # Initialize the invariant with a minimum velocity threshold
    invariant: InvariantInterface = VelocityNonZeroInvariant(min_velocity=0.5)

    # Create a sample TwistStamped message with some linear velocity
    velocity_msg = TwistStamped()
    velocity_msg.twist.linear.x = 0.3
    velocity_msg.twist.linear.y = 0.4
    velocity_msg.twist.linear.z = 0.0

    # Evaluate the invariant with the velocity message
    result = invariant(velocity=velocity_msg)

    print(f"VelocityNonZeroInvariant holds (speed >= 0.5): {result}")

    # Change velocity to test the failure case
    velocity_msg.twist.linear.x = 0.1
    velocity_msg.twist.linear.y = 0.1

    result = invariant(velocity=velocity_msg)
    print(f"VelocityNonZeroInvariant holds (speed >= 0.5): {result}")


if __name__ == "__main__":
    main()
