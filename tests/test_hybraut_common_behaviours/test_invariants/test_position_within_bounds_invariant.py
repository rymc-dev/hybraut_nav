from hybraut_common_behaviours.invariants import PositionWithinBoundsInvariant
from geometry_msgs.msg import PoseStamped
import pytest


def test_position_within_bounds_invariant():
    # Initialize invariant with bounds
    invariant = PositionWithinBoundsInvariant(
        x_min=0.0, x_max=10.0, y_min=0.0, y_max=10.0
    )

    # Create a sample pose within bounds
    pose_msg_within_bounds = PoseStamped()
    pose_msg_within_bounds.pose.position.x = 5.0
    pose_msg_within_bounds.pose.position.y = 7.0

    # Evaluate the invariant
    result_within_bounds = invariant(pose=pose_msg_within_bounds)

    # Assert the result is True
    assert result_within_bounds is True

    # Create a sample pose outside bounds
    pose_msg_outside_bounds = PoseStamped()
    pose_msg_outside_bounds.pose.position.x = 15.0
    pose_msg_outside_bounds.pose.position.y = 12.0

    # Evaluate the invariant
    result_outside_bounds = invariant(pose=pose_msg_outside_bounds)

    # Assert the result is False
    assert result_outside_bounds is False


if __name__ == "__main__":
    pytest.main([__file__])
