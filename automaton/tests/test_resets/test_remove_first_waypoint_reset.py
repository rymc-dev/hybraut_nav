"""
Tests for RemoveFirstWaypoint reset class.

This module contains comprehensive tests for the RemoveFirstWaypoint reset function,
including initialization, validation, and execution tests.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Import the classes under test
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint
from geometry_msgs.msg import Point
from automaton.resets import RemoveVirtualWaypointReset, ResetABC # Replace with actual import path

@pytest.fixture
def reset_instance():
    return RemoveVirtualWaypointReset()

class TestRemoveVirtualWaypointReset:
    @pytest.mark.parametrize(
        "state_kwargs, vw_length_post_reset",
        [
            (
                {
                    "waypoints_state": ROSWaypointsState(
                        virtual_waypoints=[
                            ROSWaypoint(position=Point(x=1.0, y=2.0, z=0.0), acceptance_radius=10.0)
                        ]
                    )
                },
                0
            ),
            (
                {
                    "waypoints_state": ROSWaypointsState(
                        virtual_waypoints=[
                            ROSWaypoint(position=Point(x=1.0, y=2.0, z=0.0), acceptance_radius=10.0),
                            ROSWaypoint(position=Point(x=20.0, y=10.0, z=0.0), acceptance_radius=10.0)
                        ]
                    )
                },
                1
            )
        ],
        ids=["Test 1: Remove virtual waypoint with specific position", "Test 2: Remove virtual waypoint with duplicate position"]
    )
    def test_reset(self, state_kwargs: dict, vw_length_post_reset: dict, reset_instance):
        """test reset ouptput"""
        reset_outputs = reset_instance(**state_kwargs)

        reset_output: ROSWaypointsState = reset_outputs['waypoints_state']
        vws = reset_output.virtual_waypoints
        assert len(vws) == vw_length_post_reset, "Reset output does not match expected result"