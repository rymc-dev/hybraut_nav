from colav_hybrid_automaton.automaton.resets import (
    GenerateVirtualWaypointReset,
    Reset
)
from typing import Dict
import pytest
from colav_interfaces.msg import WaypointsState as ROSWaypointsState
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState,
    WaypointsState as ROSWaypointsState
)


import pytest

@pytest.mark.parametrize(
    "init_kwargs, state_kwargs, expected_reset_output, test_description",
    [
        # Test 1:
        (
            {
                'longitudinal_offset_distance': 10.0,
                'lateral_offset_distance': 10.0,
                'virtual_waypoint_acceptance_radius': 10.0
            },  # init_kwargs
            {
                'agent_state': ROSAgentState(),
                'obstacles_state': ROSObstaclesState(),
                'unsafe_set_state': ROSUnsafeSetState(),
                'waypoints_state': ROSWaypointsState()
            },  # state_kwargs
            {
                'waypoints_state': ROSWaypointsState()
            },  # expected_reset_output
            'blah blah blah'  # test_description
        ),
        # Test 2 (placeholder - you should fill it in):
        (
            {},  # init_kwargs
            {},  # state_kwargs
            {},  # expected_reset_output
            'describe test 2 here'
        )
    ]
)
def test_generate_virtual_waypoint_reset_comprehensive(init_kwargs: dict, state_kwargs: dict, expected_reset_output: Dict[str, ROSWaypointsState], test_description: str):
    """
    compresive test of the virtual waypoint generator reset
    """

    reset: Reset = GenerateVirtualWaypointReset(**init_kwargs)
    actual_reset_output: Dict[str, ROSWaypointsState] = reset.__call__(**state_kwargs)

    assert expected_reset_output == actual_reset_output, test_description