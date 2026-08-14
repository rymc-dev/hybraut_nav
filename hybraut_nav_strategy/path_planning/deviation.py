#!/usr/bin/env python3
"""
Cross-track deviation utility: how far a point sits off a planned path.

Used by the strategic layer's slow-frequency plan-check timer to decide
whether the agent has drifted far enough off its global plan to warrant a
replan.
"""
import math
from nav_msgs.msg import Path
from .planner import Point


def distance_to_path(point: Point, path: Path) -> float:
    """
    Minimum distance from `point` to the polyline formed by `path.poses`.

    Args:
        point: The point to measure from (e.g. the agent's current position).
        path: A nav_msgs/Path with at least one pose.

    Returns:
        The shortest distance from `point` to any segment of the polyline,
        or `math.inf` if `path` has no poses.

    Example:
        >>> deviation = distance_to_path(current_position, global_path)
        >>> if deviation > tolerance: ...
    """
    if not path.poses:
        return math.inf

    if len(path.poses) == 1:
        p = path.poses[0].pose.position
        return math.hypot(point.x - p.x, point.y - p.y)

    best = math.inf
    for a, b in zip(path.poses, path.poses[1:]):
        ax, ay = a.pose.position.x, a.pose.position.y
        bx, by = b.pose.position.x, b.pose.position.y
        dx, dy = bx - ax, by - ay
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0.0:
            t = 0.0
        else:
            t = max(0.0, min(1.0, ((point.x - ax) * dx + (point.y - ay) * dy) / seg_len_sq))
        cx, cy = ax + t * dx, ay + t * dy
        best = min(best, math.hypot(point.x - cx, point.y - cy))

    return best
