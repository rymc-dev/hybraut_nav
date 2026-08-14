"""Unit tests for hybraut_nav_strategy.path_planning.distance_to_path."""
import math
import pytest
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from hybraut_nav_strategy.path_planning import distance_to_path, Point


def _make_path(points):
    path = Path()
    path.header.frame_id = "map"
    for x, y in points:
        pose = PoseStamped()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        path.poses.append(pose)
    return path


def test_on_path_is_zero_deviation():
    path = _make_path([(0, 0), (10, 0)])
    assert distance_to_path(Point(5, 0), path) == pytest.approx(0.0)


def test_perpendicular_offset_from_segment():
    path = _make_path([(0, 0), (10, 0)])
    assert distance_to_path(Point(5, 3), path) == pytest.approx(3.0)


def test_uses_nearest_of_multiple_segments():
    path = _make_path([(0, 0), (10, 0), (10, 10)])
    assert distance_to_path(Point(11, 5), path) == pytest.approx(1.0)


def test_clamped_beyond_segment_endpoint():
    path = _make_path([(0, 0), (10, 0)])
    assert distance_to_path(Point(15, 0), path) == pytest.approx(5.0)


def test_single_pose_path_is_point_distance():
    path = _make_path([(0, 0)])
    assert distance_to_path(Point(3, 4), path) == pytest.approx(5.0)


def test_empty_path_is_infinite():
    path = Path()
    assert distance_to_path(Point(0, 0), path) == math.inf


if __name__ == '__main__':
    pytest.main([__file__])
