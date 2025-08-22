"""
test suite for the hybraut_common_behaviours test_goal_reached_guard
this ensure this functionality works as expected.
"""

import pytest
from hybraut_common_behaviours.guards import GoalReachedGuard
from geometry_msgs.msg import PoseStamped


@pytest.mark.parametrize(
    "current_pos, goal_pos, tolerance, expected",
    [
        # Same position, tight tolerance
        ((0, 0, 0), (0, 0, 0), 0.1, True),
        # Far position, loose tolerance
        ((10, 0, 0), (0, 0, 0), 1.0, False),
        # Within tolerance
        ((0.05, 0.05, 0), (0, 0, 0), 0.1, True),
        # Just outside tolerance
        ((0.2, 0, 0), (0, 0, 0), 0.1, False),
        # Different z, within tolerance
        ((0, 0, 0.05), (0, 0, 0), 0.1, True),
    ],
)
def test_goal_reached_guard_param(current_pos, goal_pos, tolerance, expected):
    guard = GoalReachedGuard(tolerance=tolerance)
    current_pose = PoseStamped()
    goal_pose = PoseStamped()
    (
        current_pose.pose.position.x,
        current_pose.pose.position.y,
        current_pose.pose.position.z,
    ) = (float(current_pos[0]), float(current_pos[1]), float(current_pos[2]))
    goal_pose.pose.position.x, goal_pose.pose.position.y, goal_pose.pose.position.z = (
        float(goal_pos[0]),
        float(goal_pos[1]),
        float(goal_pos[2]),
    )
    assert guard(current_pose=current_pose, goal_pose=goal_pose) is expected


if __name__ == "__main__":
    pytest.main([__file__])
