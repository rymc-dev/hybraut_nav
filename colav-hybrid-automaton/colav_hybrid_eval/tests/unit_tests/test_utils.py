#!/usr/bin/python3
"""
Unit Test Suite for COLAV Hybrid Automaton utils functions.

This module contains unit tests to validate the behavior of individual utils
used in the COLAV Hybrid Automaton. Both standard and edge cases are tested to ensure full coverage
and confirm the expected functionality of each guard.

:author: Ryan McKee
:date: April 15, 2025
"""

import pytest
import sys
from typing import Tuple, Union
from std_msgs.msg import Float64MultiArray
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint
from colav_hybrid_eval.utils import (
    delta_heading,
    euclidean_distance,
    generate_circle_points,
    extract_polygon_vertices,
    quaternion_to_heading,
    get_current_ros_time,
    validate_timestamps_within_tolerance,
    normalize_angle
)

import pytest
import numpy as np
from typing import Tuple, Union


@pytest.mark.parametrize("point1, point2, expected, description", [
    # Identical Points: Expected distance is zero.
    ((0, 0), (0, 0), 0.0, "Identical points should have zero distance"),

    # Standard distance using a 3-4-5 right triangle.
    ((0, 0), (3, 4), 5.0, "Distance calculated using the 3-4-5 triangle"),

    # Test with negative coordinates.
    ((-1, -1), (2, 3), 5.0, "Distance with negative to positive coordinates"),

    # Floating point arithmetic: differences are 2 in both directions.
    ((1.5, 2.5), (3.5, 4.5), np.sqrt(2**2 + 2**2), "Floating point arithmetic test"),

    # Horizontal distance: Only the x-coordinate changes.
    ((10, 10), (20, 10), 10.0, "Horizontal line: distance should equal the difference in x values"),

    # Vertical distance: Only the y-coordinate changes.
    ((5, 5), (5, 15), 10.0, "Vertical line: distance should equal the difference in y values"),
])
def test_euclidean_distance(point1, point2, expected, description):
    result = euclidean_distance(point1, point2)
    # Using np.isclose to account for any floating point arithmetic issues
    assert np.isclose(result, expected), f"{description}: expected {expected}, got {result}"

"""utils.parametic_equations unit tests"""

@pytest.mark.parametrize("input_args, expected_output, description", [
    (
        # Test case 1: Unit circle with 4 points at center (0,0), radius 1.
        (0.0, 0.0, 1.0, 4),
        (
            np.array([1.0, -0.5, -0.5, 1.0]),             # x_points
            np.array([0.0, 0.8660254, -0.8660254, 0.0])      # y_points
        ),
        "Unit circle with 4 points at cardinal directions (using linspace angles)"
    ),
    (
        # Test case 2: Zero radius - all generated points should equal the center.
        (5.0, -3.0, 0.0, 10),
        (
            np.full(10, 5.0),  # x_points: all 5.0
            np.full(10, -3.0)  # y_points: all -3.0
        ),
        "Zero radius: all points should equal the center coordinates"
    ),
    (
        # Test case 3: Non-zero center and non-unit radius with default num_points (100).
        # Here we only check the length and the first point.
        (2.0, -1.0, 3.0, 100),
        (
            None,  # We'll check properties of the output arrays instead of exact values.
            None
        ),
        "Non-zero center with 100 points: check array shapes and the first point"
    )
])
def test_generate_circle_points(input_args, expected_output, description):
    x, y, radius, num_points = input_args
    x_points, y_points = generate_circle_points(x, y, radius, num_points)

    # Test case 1 and 2: expected outputs provided explicitly.
    if expected_output[0] is not None:
        exp_x, exp_y = expected_output
        # Compare using np.allclose for floating point precision
        assert np.allclose(x_points, exp_x), f"{description} (x_points): expected {exp_x}, got {x_points}"
        assert np.allclose(y_points, exp_y), f"{description} (y_points): expected {exp_y}, got {y_points}"
    else:
        # Test case 3: Check shapes and first point
        assert x_points.shape == (num_points,), f"{description}: x_points shape is incorrect"
        assert y_points.shape == (num_points,), f"{description}: y_points shape is incorrect"
        # For angle 0, the computed point should be (x + radius, y)
        expected_first_x = x + radius * np.cos(0)
        expected_first_y = y + radius * np.sin(0)
        assert np.allclose(x_points[0], expected_first_x), f"{description} (first x_point): expected {expected_first_x}, got {x_points[0]}"
        assert np.allclose(y_points[0], expected_first_y), f"{description} (first y_point): expected {expected_first_y}, got {y_points[0]}"

"""utils.rotation_utils unit tests"""
@pytest.mark.parametrize("input_args, expected_output, description", [
    # Agent and waypoint at same position => no heading change
    (
        (10.0, 10.0, 0.0, 10.0, 10.0),
        0.0,
        "Agent and waypoint at same location"
    ),

    # Agent facing directly toward waypoint
    (
        (0.0, 0.0, 0.0, 10.0, 0.0),
        0.0,
        "Facing directly east toward waypoint"
    ),

    # Agent facing directly away from waypoint
    (
        (0.0, 0.0, np.pi, 10.0, 0.0),
        -np.pi,
        "Facing opposite direction of waypoint"
    ),

    # 90 degree turn needed (waypoint directly above)
    (
        (0.0, 0.0, 0.0, 0.0, 10.0),
        np.pi / 2,
        "Waypoint directly north, agent facing east"
    ),

    # -90 degree turn (waypoint directly below)
    (
        (0.0, 0.0, 0.0, 0.0, -10.0),
        -np.pi / 2,
        "Waypoint directly south, agent facing east"
    ),
    # Small angle difference
    (
        (0.0, 0.0, np.pi / 4, 1.0, 1.0),
        0.0,
        "Already facing waypoint at 45 degrees"
    ),

    # Angle wraparound near +π
    (
        (0.0, 0.0, -np.pi + 0.1, -10.0, 0.0),
        -0.1,
        "Wraparound case near -π"
    ),
])
def test_delta_heading(
    input_args: Tuple[float, float, float, float, float],
    expected_output: Union[float, Exception],
    description: str
):
    """
    test if delta_heading works as expected

    This test verifies:
        1. Correct heading difference calculation in all quadrants
        2. Proper angle normalization between -pi and pi
        3. Accuracy when agent and waypoint are co-located or facing the same
        direction

    :raises:
    """
    actual = delta_heading(*input_args)
    assert np.isclose(actual, expected_output, atol=1e-6), f"{description}: expected {expected_output}, got {actual}"

# TODO: Need to write tests for normalize angle
# @pytest.mark.parametrize("input_args, expected_output, description", [

# ])
# def test_normalize_angle(input_args, expected_output, description):
#     pass

@pytest.mark.parametrize("input_args, expected_output, description", [
    (
        (0.0, 0.0, 0.0, 1.0),
        0.0,
        "Identity quaternion: no rotation → heading = 0"
    ),
    (
        (0.0, 0.0, 1.0, 0.0),
        np.pi,
        "180° rotation around Z → heading = π"
    ),
    (
        (0.0, 0.0, np.sin(np.pi/4), np.cos(np.pi/4)),
        np.pi/2,
        "90° rotation around Z → heading = π/2"
    ),
    (
        (0.0, 0.0, np.sin(-np.pi/4), np.cos(-np.pi/4)),
        -np.pi/2,
        "-90° rotation around Z → heading = -π/2"
    ),
    (
        (0.0, 0.0, np.sin(3*np.pi/4), np.cos(3*np.pi/4)),
        -np.pi/2,
        "135° rotation → normalized heading = -π/2 (since 3π/4 + π = 7π/4 % 2π = -π/2)"
    ),
    (
        (0.0, 0.0, np.nan, 1.0),
        ValueError,
        "Invalid quaternion with NaN → should raise error"
    ),
    (
        ('0', '0', '0', '1'),
        ValueError,
        "Invalid string input → should raise error"
    ),
])
def test_quaternion_to_heading(input_args, expected_output, description):
    qx, qy, qz, qw = input_args
    if isinstance(expected_output, type) and issubclass(expected_output, Exception):
        with pytest.raises(Exception):
            quaternion_to_heading(qx, qy, qz, qw)
    else:
        heading = quaternion_to_heading(qx, qy, qz, qw)
        assert np.isclose(heading, normalize_angle(expected_output), atol=1e-6), (
            f"{description} — Expected: {normalize_angle(expected_output)}, Got: {heading}"
        )

"""utils.unsafe_set_utils unit tests"""

# Define the parametrize test cases.
# @pytest.mark.parametrize("input_args, expected_output, description", [
#     (
#         (UnsafeSet(vertices=Float64MultiArray(data=[0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]))),
#         [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
#         "Square shape with four vertices"
#     ),
#     # (
#     #     (None, None, DummyUnsafeSet([0.0, 0.0, 1.0, 1.0, 2.0]), None, 0.0),
#     #     [(0.0, 0.0), (1.0, 1.0)],  # Note: Last element (2.0) is dropped
#     #     "Odd number of data elements: last element dropped"
#     # ),
#     # (
#     #     (None, None, DummyUnsafeSet([]), None, 0.0),
#     #     [],
#     #     "Empty data list should return an empty list"
#     # )
# ])
# def test_extract_polygon_vertices(input_args, expected_output, description):
#     # The function under test accepts only the UnsafeSet argument.
#     # We unpack the tuple. (None, None, unsafe_set, None, float)

#     result = extract_polygon_vertices(*input_args)
#     assert result == expected_output, f"Failed: {description}"

# @pytest.mark.parametrize("input_args, expected_output, description", [

# ])
# def test_is_inside_unsafe_set(
#     input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, float],
#     expected_output: Union[bool, Exception],
#     description: str
# ):
#     pass

# @pytest.mark.parametrize("input_args, expected_output, description", [

# ])
# def test_is_imminent_collision(
#     input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, float],
#     expected_output: Union[bool, Exception],
#     description: str
# ):
#     pass

"""utils.validate_timestamps unit tests"""

# @pytest.mark.parametrize("input_args, expected_output, description", [

# ])
# def test_get_current_ros_time(
#     input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, float],
#     expected_output: Union[bool, Exception],
#     description: str
# ):
#     pass

@pytest.mark.parametrize("input_args, expected_output, description", [

])
def test_validate_timestamps_within_tolerance(
    input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, float],
    expected_output: Union[bool, Exception],
    description: str
):
    pass

if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
