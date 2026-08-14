#!/usr/bin/env python3
"""
Downsampling utility for planner-produced paths.

A* (and the other planners here) return a path with one pose per grid cell
visited, which is far denser than a sane number of waypoints to hand off,
one leg at a time, to the tactical layer's automaton. This trims a dense
path down to a bounded number of intermediate waypoints.
"""
import numpy as np
from nav_msgs.msg import Path


def downsample_path(path: Path, max_points: int) -> Path:
    """
    Downsample a dense planner path into at most `max_points` waypoints.

    Drops `poses[0]` (the agent's position at plan time - not a real
    target) and always keeps the final pose (the goal). If what remains
    already fits within `max_points`, it is returned unchanged; otherwise
    it is reduced to `max_points` evenly-spaced poses.

    Args:
        path: Dense nav_msgs/Path as produced by a Planner (e.g. AStar),
              ordered start -> goal, with poses[0] == start.
        max_points: Maximum number of waypoints to keep. Must be >= 1.

    Returns:
        A new nav_msgs/Path (same header) with at most `max_points` poses,
        in order, always ending on the original goal pose.

    Raises:
        ValueError: if max_points < 1.

    Example:
        >>> downsampled = downsample_path(astar_path, max_points=8)
    """
    if max_points < 1:
        raise ValueError("max_points must be >= 1")

    downsampled = Path()
    downsampled.header = path.header

    interior = path.poses[1:]  # drop the start pose - not a real target
    if not interior:
        return downsampled

    if len(interior) <= max_points:
        downsampled.poses = list(interior)
        return downsampled

    indices = sorted({int(round(i)) for i in np.linspace(0, len(interior) - 1, max_points)})
    if indices[-1] != len(interior) - 1:
        # always keep the goal, even if rounding didn't land on it
        indices[-1] = len(interior) - 1

    downsampled.poses = [interior[i] for i in indices]
    return downsampled
