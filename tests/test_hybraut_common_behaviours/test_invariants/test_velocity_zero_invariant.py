# test_velocity_zero_invariant.py
# Unit tests for VelocityNonZeroInvariant in hybraut_common_behaviours.invariants.
# Verifies correct behavior for various velocity values.

import pytest
from geometry_msgs.msg import TwistStamped
from hybraut_common_behaviours.invariants import VelocityNonZeroInvariant


def make_twist(linear_x: float) -> TwistStamped:
    """Create a TwistStamped message with specified linear x velocity."""
    msg = TwistStamped()
    msg.twist.linear.x = linear_x
    return msg


@pytest.mark.parametrize(
    "velocity, expected",
    [
        (1.0, True),  # Positive velocity above threshold
        (0.0, False),  # Exactly zero velocity
        (-1.0, True),  # Negative velocity above threshold
        (0.0001, False),  # Positive velocity below threshold
        (-0.0001, False),  # Negative velocity below threshold
    ],
)
def test_velocity_non_zero_invariant(velocity: float, expected: bool):
    """Test VelocityNonZeroInvariant with various velocities."""
    invariant = VelocityNonZeroInvariant(min_velocity=0.5)
    msg = make_twist(velocity)
    assert invariant(velocity=msg) is expected


if __name__ == "__main__":
    pytest.main([__file__])
