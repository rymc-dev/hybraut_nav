from colav_hybrid_automaton.automaton.guards import WaypointReachedGuard
import pytest
from colav_interfaces.msg import (
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint,
    AgentState as ROSAgentState
)
from geometry_msgs.msg import Point
from geometry_msgs.msg import Pose

@pytest.mark.parametrize(
    "agent_state, waypoints_state, expected_guard_evaluation, test_description",
    [
        # If agent has entered the waypoint acceptance radius → guard should fire (True)
        (ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=10.0), ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius= 20.0)), True, "agent in waypoint current waypoint acceptance radius → True"),
    ]
)
def test_waypoint_reached_guard_comprehesive(agent_state:ROSAgentState, waypoints_state:ROSWaypointsState, expected_guard_evaluation:bool, test_description: str):
    """_summary_

    Args:
        agent_state (ROSAgentState): _description_
        waypoints_state (ROSWaypointsState): _description_
        expected_guard_evaluation (bool): _description_
        test_description (str): _description_
    """
    guard = WaypointReachedGuard()
    kwargs = {
        'agent_state': agent_state,
        'waypoints_state': waypoints_state
    }
    actual_guard_evaluation = guard.__call__(**kwargs)

    assert guard.__repr__() == "WaypointReachedGuard(initialized=True)"
    assert guard.__str__() == "Guard Function: WaypointReachedGuard" 
    assert guard.get_guard_info()["class_name"] == 'WaypointReachedGuard'
    assert guard.get_guard_info()["module"] == 'colav_hybrid_automaton.automaton.guards.waypoint_reached_guard'
    assert guard.get_guard_info()['is_initialized'] == True
    assert actual_guard_evaluation == expected_guard_evaluation, test_description