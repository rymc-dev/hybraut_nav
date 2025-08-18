from hybraut_common_behaviours.guards import GoalReachedGuard
from geometry_msgs.msg import PoseStamped
import pytest


def test_goal_reached_guard():
    """ """
    guard = GoalReachedGuard(tolerance=0.1)

    current_pose = PoseStamped()
    goal_pose = PoseStamped()
    assert guard(current_pose=current_pose, goal_pose=goal_pose) is True

    guard = GoalReachedGuard(tolerance=1.0)
    current_pose.pose.position.x = 10.0

    assert guard(current_pose=current_pose, goal_pose=goal_pose) is False


if __name__ == "__main__":
    pytest.main([__file__])
