#!/usr/bin/python3
"""
Unit Test Suite for COLAV Hybrid Automaton Reset Conditions.

This module contains unit tests to validate the behavior of individual reset functions
used in the COLAV Hybrid Automaton. Both standard and edge cases are tested to ensure full coverage
and confirm the expected functionality of each guard.

:author: Ryan McKee
:date: April 11, 2025
"""

import pytest

from colav_interfaces.msg import Waypoint, Waypoints
from geometry_msgs.msg import Point32

from colav_hybrid_eval.scripts.resets import (
    reset_WAYPOINT_REACHED_to_CRUISE,
    reset_CRUISE_to_T2LOS
)
from typing import List


@pytest.mark.parametrize(
"input_arg, expected_length, expected_waypoints, description",
[
    # Test Case 1: validation test: test with one virtual waypoint should return a list with one waypoint.
    (
        Waypoints(
            waypoints=[
                Waypoint(),
                Waypoint(
                    position=Point32(
                        x=float(100),
                        y=float(20),
                        z=float(0)),
                    acceptance_radius=float(10))
        ]),
        float(1),
        Waypoints(
            waypoints=[
                Waypoint(
                    position=Point32(
                        x=float(100),
                        y=float(20),
                        z=float(0)),
                    acceptance_radius=float(10)
                )
            ]),
        "Reset with list containing 1 virtual waypoint"
    )
])
def test_reset_WAYPOINT_REACHED_to_CRUISE(
    input_arg: Waypoints,
    expected_length: float,
    expected_waypoints: Waypoints,
    exception: Exception,
    description: str
):
    """
    test to ensure the WAYPOINT_REACHED_to_CRUISE functionality is working as expected
    """
    try:
        waypoints = reset_WAYPOINT_REACHED_to_CRUISE(input_arg)
    except Exception as e:
        if exception is None:
            assert False, f'Exception occured during test: {str(e)}'
        
        assert exception == e, \
            f"Test: {description}, expected: {exception}, got {e}"

    assert len(waypoints.waypoints) == expected_length, \
        f"Test: {description}, expected: {expected_length}, got: {len(waypoints.waypoints)}"
    assert waypoints == expected_waypoints, \
        f"Test: {description}, expected: {waypoints}, got: {expected_waypoints}"

# @pytest.mark.parametrize("input_args, expected_output, description", [
#     ()
# ])
# def test_reset_CRUISE_to_T2LOS():
#     pass
