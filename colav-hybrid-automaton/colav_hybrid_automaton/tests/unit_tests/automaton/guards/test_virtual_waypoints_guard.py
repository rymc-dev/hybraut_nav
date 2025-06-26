from colav_hybrid_automaton.automaton.guards import VirtualWaypointsGuard
import pytest
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint


@pytest.mark.parametrize(
    "waypoints_state, expected_guard_evaluation, test_description",
    [
        # If there is at least one virtual waypoint → guard should fire (True)
        (ROSWaypointsState(virtual_waypoints=[ROSWaypoint()]), True, "One virtual waypoint → True"),

        # If there are no virtual waypoints → guard should not fire (False)
        (ROSWaypointsState(virtual_waypoints=[]), False, "Empty virtual_waypoints list → False"),

        # If the field is omitted (defaults to empty) → guard should not fire
        (ROSWaypointsState(), False, "No virtual_waypoints attribute set → False"),
    ]
)
def test_virtual_waypoints_guard_comprehensive(
    waypoints_state: ROSWaypointsState,
    expected_guard_evaluation: bool,
    test_description: str
):
    """
    Comprehensive tests for VirtualWaypointsGuard:
    - fires when there is at least one virtual waypoint
    - does not fire when there are none
    """
    guard = VirtualWaypointsGuard()

    # Call with only the waypoints_state
    actual = guard.__call__(waypoints_state=waypoints_state)

    assert actual == expected_guard_evaluation, test_description

@pytest.mark.parametrize(
    "state_kwargs, expected_exception, test_description",
    [
        # No state args passed for __call__ ()
        ({}, TypeError, "No args -> pytest.error(ValueError)"),

        # If there are no virtual waypoints → guard should not fire (False)
        ({'waypoints_state': "invalid_type"}, TypeError, "Invalid State -> pytest.error(TypeError)"),

        # If the field is omitted (defaults to empty) → guard should not fire
        ({'waypoints_state': ROSWaypointsState()}, AttributeError, "No virtual_waypoints attribute set → False"),
    ]
)
def test_virtual_waypoints_guard_invalid_state_kwargs(
    state_kwargs: ROSWaypointsState,
    expected_exception: Exception,
    test_description: str
):
    guard = VirtualWaypointsGuard()

    with pytest.raises(expected_exception):
        guard.__call__(**state_kwargs)