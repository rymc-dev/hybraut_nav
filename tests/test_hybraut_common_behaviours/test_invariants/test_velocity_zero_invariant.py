import pytest
from geometry_msgs.msg import TwistStamped
from hybraut_common_behaviours.invariants import VelocityNonZeroInvariant


def make_twist(linear_x: float) -> TwistStamped:
    """Helper to create a TwistStamped with given linear x velocity."""
    msg = TwistStamped()
    msg.twist.linear.x = linear_x
    return msg


@pytest.mark.parametrize(
    "velocity, expected",
    [
        (1.0, True),  # non-zero positive velocity, above threshold
        (0.0, False),  # exactly zero
        (-1.0, True),  # negative velocity, above threshold
        (0.0001, False),  # below threshold
        (-0.0001, False),  # below threshold
    ],
)
def test_velocity_non_zero_invariant(velocity: float, expected: bool):
    invariant = VelocityNonZeroInvariant(min_velocity=0.5)
    msg = make_twist(velocity)
    assert invariant(velocity=msg) is expected


if __name__ == "__main__":
    pytest.main([__file__])
