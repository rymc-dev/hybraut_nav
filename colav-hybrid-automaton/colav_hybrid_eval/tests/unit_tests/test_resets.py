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
    "input_arg, expected_length, expected_waypoints, exception, description",
    [
        # Test Case 1: validation test — test with one valid virtual waypoint should return a list with one waypoint.
        (
            Waypoints(
                waypoints=[
                    Waypoint(),  # assumed invalid
                    Waypoint(
                        position=Point32(x=100.0, y=20.0, z=0.0),
                        acceptance_radius=10.0
                    )
                ]
            ),
            1,
            Waypoints(
                waypoints=[
                    Waypoint(
                        position=Point32(x=100.0, y=20.0, z=0.0),
                        acceptance_radius=10.0
                    )
                ]
            ),
            None,
            "Reset with list containing 1 virtual waypoint"
        ),
        # Test Case 2: exception handling — test with no valid virtual waypoints should return an exception
        (
            Waypoints(
                waypoints=[
                    Waypoint(),  # assumed invalid
                ]
            ),
            1,
            None,
            ValueError('waypoints list size less than 1, something has went wrong is guard condition'),
            "Reset with no virtual waypoints"
        ),
    ]
    # TODO: Test case on invalid arg type benig passed in
)
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
        
        assert str(exception) == str(e), \
            f"Test: {description}, expected: {exception}, got {e}"
        return

    assert len(waypoints.waypoints) == expected_length, \
        f"Test: {description}, expected: {expected_length}, got: {len(waypoints.waypoints)}"
    assert waypoints == expected_waypoints, \
        f"Test: {description}, expected: {waypoints}, got: {expected_waypoints}"

# TODO: This test needs work
@pytest.mark.parametrize("input_args, expected_length, expected_waypoints, exception, description", [
    # # Test Case 1: input-type validation; passing anything other than expected types should raise ValueError
    # (),
    # # Test Case 2: Empty unsafe set: if empty should raise does not contain any vertices error
    # (),
    # # Test Case 3: Invalid-polygon geometry: if the vertices form an invalid polyshape self-intersecting polygon raise exception
    # (),
    # #Test Case 4: No Visible Vertices: All vercies are occluded by the polygons own exterior raises no visible vertices error
    # (),
    # # Test Case 5: Agent Coincides with vertex
    # (),
    # # Test Case 6 
    # (),
    # """
    # Test Case 7: Nominal "Rightmost vertex selection and offset"
    # - Given a simple triangle of vertices, ensure that the vertex with the largest bearing from the agent is chosen and the new waypoint is 
    #   inserted at index 0 at the offset of VW_ACCEPTANCE_RADIUS/2 + 5
    # """
    # (),
])
def test_reset_CRUISE_to_T2LOS(input_args, expected_length, expected_waypoints, exception, description):
    """
    Test validates the reste_CRUISE_to_T2LOS logic
    """
    pass # TODO: THis needs worked on