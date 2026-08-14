"""Unit tests for hybraut_nav_strategy.path_planning.downsample_path."""
import pytest
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from hybraut_nav_strategy.path_planning import downsample_path


def _make_path(points):
    path = Path()
    path.header.frame_id = "map"
    for x, y in points:
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        path.poses.append(pose)
    return path


def test_downsample_drops_start_pose():
    path = _make_path([(0, 0), (1, 0), (2, 0)])
    result = downsample_path(path, max_points=8)
    assert len(result.poses) == 2
    assert result.poses[0].pose.position.x == 1.0
    assert result.poses[-1].pose.position.x == 2.0


def test_downsample_passthrough_when_within_bound():
    path = _make_path([(0, 0), (1, 0), (2, 0), (3, 0)])
    result = downsample_path(path, max_points=8)
    assert len(result.poses) == 3


def test_downsample_bounds_point_count_and_keeps_goal():
    path = _make_path([(i, 0) for i in range(101)])  # start (0,0) .. goal (100,0)
    result = downsample_path(path, max_points=8)
    assert len(result.poses) <= 8
    assert result.poses[-1].pose.position.x == 100.0


def test_downsample_empty_interior_returns_empty_path():
    path = _make_path([(0, 0)])  # only the start pose, no real waypoints
    result = downsample_path(path, max_points=8)
    assert len(result.poses) == 0


def test_downsample_rejects_non_positive_max_points():
    path = _make_path([(0, 0), (1, 0)])
    with pytest.raises(ValueError):
        downsample_path(path, max_points=0)


if __name__ == '__main__':
    pytest.main([__file__])
