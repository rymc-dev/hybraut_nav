# from  colav_hybrid_automaton.automaton.guards import LOSClearToWaypointGuard
# import math
# import pytest
# from colav_interfaces.msg import (
#     AgentState as ROSAgentState,
#     WaypointsState as ROSWaypointsState,
#     ObstaclesState as ROSObstaclesState
# )


# @pytest.mark.parametrize(
#     "",
#     [
#     ]
# )
# def test_los_clear_to_waypoint(
#     heading_tolerance: float,
#     agent_x: float,
#     agent_y: float,
#     agent_yaw: float,
#     waypoint_x: float,
#     waypoint_y: float,
#     expected_guard_evaluation: bool,
#     test_description: str
# ):
#     """Comprehensive test for HeadingNotWithinToleranceGuard with boundary conditions.
    
#     Args:
#         heading_tolerance (float): The heading tolerance value.
#         agent_x, agent_y (float): Agent position coordinates.
#         agent_yaw (float): The agent's yaw angle in radians.
#         waypoint_x, waypoint_y (float): Waypoint position coordinates.
#         expected_guard_evaluation (bool): Expected result of guard evaluation.
#         test_description (str): Description of the test case.
#     """
#     # Create agent state
#     agent_state = ROSAgentState(
#         pose=Pose(
#             position=Point(x=agent_x, y=agent_y, z=0.0),
#             orientation=quaternion_from_euler(0.0, 0.0, agent_yaw)
#         )
#     )
    
#     # Create current waypoint (this is what your guard expects)
#     current_waypoint = ROSWaypoint(
#         position=Point(x=waypoint_x, y=waypoint_y, z=0.0)
#     )
    
#     # Create waypoint state with current_waypoint attribute
#     waypoints_state = ROSWaypointsState(
#         current_waypoint=current_waypoint
#     )
    
#     # Test guard creation and evaluation
#     init_kwargs = {"heading_tolerance": heading_tolerance}
#     guard = HeadingNotWithinToleranceGuard(**init_kwargs)
    
#     assert guard.__str__() == 'Guard Function: HeadingNotWithinToleranceGuard'
#     assert guard.__repr__() == "HeadingNotWithinToleranceGuard(initialized=True)"
    
#     state_kwargs = {
#         'agent_state': agent_state,
#         'waypoints_state': waypoints_state
#     }
    
#     actual_guard_evaluation = guard.__call__(**state_kwargs)
#     assert actual_guard_evaluation == expected_guard_evaluation, \
#         f"Test case '{test_description}' failed: expected {expected_guard_evaluation}, got {actual_guard_evaluation}"