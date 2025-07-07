# from  colav_hybrid_automaton.automaton.guards import LOSClearToWaypointGuard
# import math
# import pytest
# from colav_interfaces.msg import (
#     AgentState as ROSAgentState,
#     WaypointsState as ROSWaypointsState,
#     ObstaclesState as ROSObstaclesState,
#     UnsafeSetState as ROSUnsafeSetState,
#     Waypoint as ROSWaypoint
# )
# from geometry_msgs.msg import Pose, Point
# from std_msgs.msg import Float64MultiArray

# # TODO: Need to work on obstacles guard conditions
# @pytest.mark.parametrize(
#     "los_distance_threshold, agent_state, obstacles_state, unsafe_set_state, waypoints_state, expected_guard_evaluation, test_description",
#     [
#         # Test 1: No Unsafe Set Vertices, no obstacles and agent state is on waypoint state -> should evaluate as (False)
#         (
#             20.0,
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
#             ROSObstaclesState(),
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[])),  # Empty unsafe set
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius=5.0)),
#             False,
#             "test: no unsafe set or obstacles with agent on waypoints state -> expected guard evaluation: False"
#         ),
#         # Test 2: Unsafe set on LOS between agent and current waypoint, but interception just outside distance threshold
#         (
#             20.0,  # Distance threshold is 20.0
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
#             ROSObstaclesState(),
#             # Create unsafe polygon that intersects LOS at distance ~25 (outside threshold of 20)
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 23.0, -2.0,  # Bottom-left of obstacle
#                 27.0, -2.0,  # Bottom-right of obstacle  
#                 27.0, 2.0,   # Top-right of obstacle
#                 23.0, 2.0    # Top-left of obstacle
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=5.0)),
#             False,
#             "test: unsafe set on los to current waypoint but interception just outside distance threshold -> expected guard evaluation: False"
#         ),
#         # Test 3: Unsafe set on LOS between agent and current waypoint, interception occurs within the distance threshold -> should evaluate as True
#         (
#             30.0,  # Distance threshold is 30.0
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
#             ROSObstaclesState(),
#             # Create unsafe polygon that intersects LOS at distance ~15 (within threshold of 30)
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 13.0, -2.0,  # Bottom-left of obstacle
#                 17.0, -2.0,  # Bottom-right of obstacle
#                 17.0, 2.0,   # Top-right of obstacle
#                 13.0, 2.0    # Top-left of obstacle
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=5.0)),
#             True,
#             "test: unsafe set on los to current waypoint but interception just within the distance threshold -> expected guard evaluation: True"
#         ),

#         # Test 4: Unsafe set intersects LOS exactly at the distance threshold boundary
#         (
#             25.0,  # Distance threshold is 25.0
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
#             ROSObstaclesState(),
#             # Create unsafe polygon that intersects LOS at distance exactly 25 (at threshold boundary)
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 24.0, -1.0,  # Bottom-left of obstacle
#                 26.0, -1.0,  # Bottom-right of obstacle
#                 26.0, 1.0,   # Top-right of obstacle
#                 24.0, 1.0    # Top-left of obstacle
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=5.0)),
#             True,
#             "test: unsafe set intersects LOS exactly at distance threshold boundary -> expected guard evaluation: True"
#         ),

#         # Test 5: Very small distance threshold with nearby unsafe set
#         (
#             1.0,  # Very small distance threshold
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=2.0),
#             ROSObstaclesState(),
#             # Unsafe polygon very close to agent (within 1.0 threshold)
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 0.5, -0.5,   # Bottom-left of obstacle
#                 1.5, -0.5,   # Bottom-right of obstacle
#                 1.5, 0.5,    # Top-right of obstacle
#                 0.5, 0.5     # Top-left of obstacle
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=0.0, z=0.0), acceptance_radius=1.0)),
#             True,
#             "test: very small distance threshold with nearby unsafe set -> expected guard evaluation: True"
#         ),

#         # Test 6: Diagonal LOS path with unsafe set intersection
#         (
#             15.0,
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=5.0),
#             ROSObstaclesState(),
#             # Unsafe polygon intersecting diagonal LOS at distance ~7.07 (within threshold of 15)
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 4.0, 4.0,    # Bottom-left of obstacle
#                 6.0, 4.0,    # Bottom-right of obstacle
#                 6.0, 6.0,    # Top-right of obstacle
#                 4.0, 6.0     # Top-left of obstacle
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=20.0, y=20.0, z=0.0), acceptance_radius=3.0)),
#             True,
#             "test: diagonal LOS path with unsafe set intersection within threshold -> expected guard evaluation: True"
#         ),

#         # Test 7: Multiple intersections with unsafe set (complex polygon)
#         (
#             40.0,
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=8.0),
#             ROSObstaclesState(),
#             # L-shaped unsafe polygon that intersects LOS multiple times, closest at ~10 units
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 8.0, -3.0,   # Bottom-left of vertical part
#                 12.0, -3.0,  # Bottom-right of vertical part
#                 12.0, 1.0,   # Corner point
#                 25.0, 1.0,   # Bottom-right of horizontal part
#                 25.0, 3.0,   # Top-right of horizontal part
#                 8.0, 3.0     # Top-left (back to start)
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=4.0)),
#             True,
#             "test: complex polygon with multiple LOS intersections, closest within threshold -> expected guard evaluation: True"
#         ),

#         # Test 8: Unsafe set very close to waypoint but outside threshold from agent
#         (
#             10.0,
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=5.0),
#             ROSObstaclesState(),
#             # Unsafe polygon near waypoint at distance ~45 from agent (outside threshold of 10)
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 43.0, -2.0,  # Bottom-left near waypoint
#                 47.0, -2.0,  # Bottom-right near waypoint
#                 47.0, 2.0,   # Top-right near waypoint
#                 43.0, 2.0    # Top-left near waypoint
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=2.0)),
#             False,
#             "test: unsafe set near waypoint but outside distance threshold from agent -> expected guard evaluation: False"
#         ),

#         # Test 9: Agent and waypoint at same position (zero distance LOS)
#         (
#             5.0,
#             ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=3.0),
#             ROSObstaclesState(),
#             # Unsafe polygon nearby but shouldn't affect zero-length LOS
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 8.0, 8.0,    # Bottom-left
#                 12.0, 8.0,   # Bottom-right
#                 12.0, 12.0,  # Top-right
#                 8.0, 12.0    # Top-left
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius=1.0)),
#             False,
#             "test: agent and waypoint at same position with nearby unsafe set -> expected guard evaluation: False"
#         ),

#         # Test 10: Very large distance threshold should catch distant intersections
#         (
#             1000.0,  # Very large threshold
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=15.0),
#             ROSObstaclesState(),
#             # Unsafe polygon far from agent but within large threshold
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 198.0, -5.0,  # Bottom-left at distance ~200
#                 202.0, -5.0,  # Bottom-right at distance ~200
#                 202.0, 5.0,   # Top-right at distance ~200
#                 198.0, 5.0    # Top-left at distance ~200
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=500.0, y=0.0, z=0.0), acceptance_radius=10.0)),
#             True,
#             "test: very large distance threshold catches distant intersection -> expected guard evaluation: True"
#         ),

#         # Test 11: Negative coordinates test
#         (
#             20.0,
#             ROSAgentState(pose=Pose(position=Point(x=-10.0, y=-10.0, z=0.0)), safety_radius=5.0),
#             ROSObstaclesState(),
#             # Unsafe polygon in negative coordinate space, intersecting LOS at distance ~7.07
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 -6.0, -6.0,  # Bottom-left
#                 -4.0, -6.0,  # Bottom-right
#                 -4.0, -4.0,  # Top-right
#                 -6.0, -4.0   # Top-left
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius=3.0)),
#             True,
#             "test: negative coordinates with unsafe set intersection within threshold -> expected guard evaluation: True"
#         ),

#         # Test 12: Unsafe set touches LOS line but doesn't truly intersect (edge case)
#         (
#             25.0,
#             ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=4.0),
#             ROSObstaclesState(),
#             # Very thin unsafe polygon that just touches the LOS line at distance 20
#             ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
#                 20.0, 0.0,   # Point touching LOS
#                 20.1, -0.1,  # Bottom-right (very small)
#                 20.1, 0.1,   # Top-right (very small)
#                 20.0, 0.0    # Back to touching point
#             ])),
#             ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=2.0)),
#             True,
#             "test: unsafe set barely touches LOS line within threshold -> expected guard evaluation: True"
#         )
#     ]
# )
# def test_los_clear_to_waypoint_comprehensive(
#     los_distance_threshold: float,
#     agent_state: ROSAgentState,
#     obstacles_state: ROSObstaclesState,
#     unsafe_set_state: ROSUnsafeSetState,
#     waypoints_state: ROSWaypointsState,
#     expected_guard_evaluation: bool,
#     test_description: str
# ):
#     """Comprehensive test for LOSClearToWaypointGuard with boundary conditions.
    
#     Args:
#         los_distance_threshold (float): The distance threshold for LOS analysis.
#         agent_state (ROSAgentState): The agent's current state.
#         obstacles_state (ROSObstaclesState): State of obstacles in the environment.
#         unsafe_set_state (ROSUnsafeSetState): State of the unsafe set.
#         waypoints_state (ROSWaypointsState): State of waypoints.
#         expected_guard_evaluation (bool): Expected result of guard evaluation.
#         test_description (str): Description of the test case.
#     """
#     init_kwargs = {
#         'los_distance_threshold': los_distance_threshold
#     }
    
#     guard = LOSClearToWaypointGuard(**init_kwargs)
    
#     assert guard.__repr__() == "LOSClearToWaypointGuard(initialized=True)"
#     assert guard.__str__() == "Guard Function: LOSClearToWaypointGuard"
    
#     guard_info = guard.get_guard_info()
#     assert guard_info["class_name"] == 'LOSClearToWaypointGuard'
#     assert guard_info["module"] == 'colav_hybrid_automaton.automaton.guards.los_clear_to_waypoint_guard'
#     assert guard_info['is_initialized'] == True
    
#     state_kwargs = {
#         'agent_state': agent_state,
#         'obstacles_state': obstacles_state,
#         'unsafe_set_state': unsafe_set_state,
#         'waypoints_state': waypoints_state
#     }
    
#     actual_guard_evaluation = guard.__call__(**state_kwargs)
#     assert actual_guard_evaluation == expected_guard_evaluation, test_description

# @pytest.mark.parametrize(
#     "init_kwargs, expected_exception, test_description",
#     [
#         # Test 1: No init kwargs passed for __init__()
#         ({}, KeyError, "No args -> pytest.error(KeyError)"),

#         # Test 2: invalid distance threshold data type → should throw pytest.error(TypeError)
#         ({'los_distance_threshold': "invalid_type"}, TypeError, "Invalid distance threshold type -> pytest.error(TypeError)"),

#         # Test 3: invalid distance threshold value (los_distance_threshold < 0.0) -> should throw pytest.error(ValueError)
#         ({'los_distance_threshold': -0.01}, ValueError, "Negative los_distance_threshold → pytest.error(ValueError)"),
#     ]
# )
# def test_los_clear_to_virtual_waypoint_invalid_init_kwargs(
#     init_kwargs: ROSWaypointsState,
#     expected_exception: Exception,
#     test_description: str
# ):
#     with pytest.raises(expected_exception):
#         LOSClearToWaypointGuard(**init_kwargs)

# @pytest.mark.parametrize(
#     "state_kwargs, expected_exception, test_description",
#     [
#         # No state args passed
#         ({}, KeyError, "No args -> KeyError('agent state not given')"),
        
#         # Missing agent_state
#         ({
#             'waypoints_state': ROSWaypointsState(),
#             'unsafe_set_state': ROSUnsafeSetState(),
#             'obstacles_state': ROSObstaclesState()
#         }, KeyError, "Missing agent_state -> KeyError('agent state not given')"),
        
#         # Wrong type for agent_state
#         ({
#             'agent_state': "wrong_type",
#             'waypoints_state': ROSWaypointsState(),
#             'unsafe_set_state': ROSUnsafeSetState(),
#             'obstacles_state': ROSObstaclesState()
#         }, KeyError, "Wrong agent_state type -> KeyError('agent state given not current type')"),
        
#         # Missing waypoints_state
#         ({
#             'agent_state': ROSAgentState(),
#             'unsafe_set_state': ROSUnsafeSetState(),
#             'obstacles_state': ROSObstaclesState()
#         }, KeyError, "Missing waypoints_state -> KeyError('waypoints_state not given')"),
        
#         # Wrong type for waypoints_state
#         ({
#             'agent_state': ROSAgentState(),
#             'waypoints_state': "wrong_type",
#             'unsafe_set_state': ROSUnsafeSetState(),
#             'obstacles_state': ROSObstaclesState()
#         }, KeyError, "Wrong waypoints_state type -> KeyError('waypoints state given not correct type.')"),
        
#         # Missing unsafe_set_state
#         ({
#             'agent_state': ROSAgentState(),
#             'waypoints_state': ROSWaypointsState(),
#             'obstacles_state': ROSObstaclesState()
#         }, KeyError, "Missing unsafe_set_state -> KeyError('unsafe set state not given')"),
        
#         # Wrong type for unsafe_set_state
#         ({
#             'agent_state': ROSAgentState(),
#             'waypoints_state': ROSWaypointsState(),
#             'unsafe_set_state': "wrong_type",
#             'obstacles_state': ROSObstaclesState()
#         }, KeyError, "Wrong unsafe_set_state type -> KeyError('unsafe set input not of correct type ROSUnsafeSet')"),
        
#         # Missing obstacles_state
#         ({
#             'agent_state': ROSAgentState(),
#             'waypoints_state': ROSWaypointsState(),
#             'unsafe_set_state': ROSUnsafeSetState()
#         }, KeyError, "Missing obstacles_state -> KeyError('obstacles state not given')"),
        
#         # Wrong type for obstacles_state
#         ({
#             'agent_state': ROSAgentState(),
#             'waypoints_state': ROSWaypointsState(),
#             'unsafe_set_state': ROSUnsafeSetState(),
#             'obstacles_state': "wrong_type"
#         }, KeyError, "Wrong obstacles_state type -> KeyError('obstacles state not of the correct type ROSObstaclesState')"),
#     ]
# )
# def test_los_clear_to_virtual_waypoint_invalid_state_kwargs(
#     state_kwargs: dict,
#     expected_exception: Exception,
#     test_description: str
# ):
#     guard = LOSClearToWaypointGuard(los_distance_threshold=10.0)
#     with pytest.raises(expected_exception):
#         guard.__call__(**state_kwargs)