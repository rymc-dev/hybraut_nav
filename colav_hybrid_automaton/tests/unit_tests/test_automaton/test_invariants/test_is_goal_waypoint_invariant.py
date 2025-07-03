from colav_hybrid_automaton.automaton.invariants import IsGoalWaypointInvariant, InvariantABC
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint
import pytest
from geometry_msgs.msg import Pose, Point


@pytest.mark.parametrize(
    "state_kwargs, expected_invariant_evaluation, test_description",
    [
        # Test 1: Goal waypoint reached (current == goal, no virtual waypoints)
        (
            {
                'waypoints_state': ROSWaypointsState(
                    current_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0))),
                    goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0))),
                    virtual_waypoints=[]
                )
            }, 
            True, 
            'Current waypoint equals goal waypoint with no virtual waypoints -> True'
        ),
        
        # Test 2: Virtual waypoints exist (should return False regardless of current/goal)
        (
            {
                'waypoints_state': ROSWaypointsState(
                    current_waypoint=ROSWaypoint(position=Pose(position=Point(x=0.0, y=0.0))),
                    virtual_waypoints=[ROSWaypoint(position=Pose(position=Point(x=5.0, y=5.0)))],
                    goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0)))
                )
            },
            False,
            'Virtual waypoints exist -> False'
        ),
        
        # Test 3: Virtual waypoints exist, even when current == goal
        (
            {
                'waypoints_state': ROSWaypointsState(
                    current_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0))),
                    virtual_waypoints=[ROSWaypoint(position=Pose(position=Point(x=5.0, y=5.0)))],
                    goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0)))
                )
            },
            False,
            'Virtual waypoints exist even when current equals goal -> False'
        ),
        
        # Test 4: Multiple virtual waypoints
        (
            {
                'waypoints_state': ROSWaypointsState(
                    current_waypoint=ROSWaypoint(position=Pose(position=Point(x=0.0, y=0.0))),
                    virtual_waypoints=[
                        ROSWaypoint(position=Pose(position=Point(x=3.0, y=3.0))),
                        ROSWaypoint(position=Pose(position=Point(x=7.0, y=7.0)))
                    ],
                    goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0)))
                )
            },
            False,
            'Multiple virtual waypoints exist -> False'
        ),
        
        # Test 5: Empty virtual waypoints list, different current and goal
        # This should raise an Exception according to the logic
        (
            {
                'waypoints_state': ROSWaypointsState(
                    current_waypoint=ROSWaypoint(position=Pose(position=Point(x=0.0, y=0.0))),
                    virtual_waypoints=[],
                    goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0)))
                )
            },
            Exception,  # Special marker for exception test
            'No virtual waypoints and current != goal should raise Exception'
        )
    ]
)
def test_is_goal_waypoint_invariant_comprehensive(state_kwargs: dict, expected_invariant_evaluation, test_description: str):
    """
    Test IsGoalWaypointInvariant with various waypoint configurations.
    
    The invariant logic:
    1. If virtual_waypoints exist (len > 0) -> return False
    2. If no virtual waywaypoints AND current == goal -> return True  
    3. If no virtual waypoints AND current != goal -> raise Exception
    """
    invariant: InvariantABC = IsGoalWaypointInvariant()
    
    if expected_invariant_evaluation == Exception:
        # Test case expects an exception
        with pytest.raises(Exception, match="exception occured in.*unexpected waypoint state"):
            invariant.__call__(**state_kwargs)
    else:
        # Test case expects a boolean result
        actual_invariant_evaluation: bool = invariant.__call__(**state_kwargs)
        assert actual_invariant_evaluation == expected_invariant_evaluation, test_description

@pytest.mark.parametrize(
    "state_kwargs, expected_exception, test_description",
    [
        # No state args passed for __call__ ()
        ({}, KeyError, "No args -> pytest.error(ValueError)"),

        # If there are no virtual waypoints → guard should not fire (False)
        ({'waypoints_state': "invalid_type"}, TypeError, "Invalid State -> pytest.error(TypeError)"),
    ]
)
def test_virtual_waypoints_guard_invalid_state_kwargs(
    state_kwargs: ROSWaypointsState,
    expected_exception: Exception,
    test_description: str
):
    invariant:InvariantABC = IsGoalWaypointInvariant()

    with pytest.raises(expected_exception):
        invariant.__call__(**state_kwargs)