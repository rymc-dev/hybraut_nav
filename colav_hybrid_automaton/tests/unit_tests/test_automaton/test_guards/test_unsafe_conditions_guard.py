# from colav_hybrid_automaton.automaton.guards import UnsafeConditionsGuard
# import pytest
# from colav_interfaces.msg import (
#     AgentState as ROSAgentState,
#     ObstaclesState as ROSObstaclesState,
#     UnsafeSetState as ROSUnsafeSetState
# )
# from geometry_msgs.msg import Pose, Point
# from std_msgs.msg import Float64MultiArray


# @pytest.mark.parametrize(
#     "state_kwargs, expected_guard_evaluation, test_description",
#     [
#         # Test 1: No unsafe set → should return False
#         (
#             {
#                 'agent_state': ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=10.0),
#                 'unsafe_set_state': ROSUnsafeSetState(),
#                 'obstacles_state': ROSObstaclesState() 
#             },
#             False,
#             "No unsafe set data provided → False"
#         ),
#         # Test 2: Unsafe set is provided but does not intersect agent circle
#         (
#             {
#                 'agent_state': ROSAgentState(pose=Pose(position=Point(x=100.0, y=100.0, z=0.0)), safety_radius=5.0),
#                 'unsafe_set_state': ROSUnsafeSetState(
#                     convex_hull_vertices=Float64MultiArray(data=[
#                         0.0, 0.0,
#                         0.0, 20.0,
#                         20.0, 20.0,
#                         20.0, 0.0
#                     ])
#                 ),
#                 'obstacles_state': ROSObstaclesState() 
#             },
#             False,
#             "Agent is outside the unsafe set → False"
#         ),
#         # Test 3: Unsafe set intersects the agent's safety buffer
#         (
#             {
#                 'agent_state': ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=15.0),
#                 'unsafe_set_state': ROSUnsafeSetState(
#                     convex_hull_vertices=Float64MultiArray(data=[
#                         0.0, 0.0,
#                         0.0, 20.0,
#                         20.0, 20.0,
#                         20.0, 0.0
#                     ])
#                 ),
#                 'obstacles_state': ROSObstaclesState() 
#             },
#             True,
#             "Agent safety radius intersects unsafe set → True"
#         )
#     ]
# )
# def test_unsafe_conditions_guard_comprehensive(
#     state_kwargs: dict,
#     expected_guard_evaluation: bool,
#     test_description: str
# ):
#     """
#     Tests for UnsafeConditionsGuard:
#     - Fires when the agent’s safety radius intersects the unsafe polygon
#     - Does not fire when no intersection occurs
#     """
#     guard = UnsafeConditionsGuard()
#     actual_guard_evaluation = guard(**state_kwargs)
#     assert actual_guard_evaluation == expected_guard_evaluation, test_description


# @pytest.mark.parametrize(
#     "state_kwargs, expected_exception, test_description",
#     [
#         # Test 1: No state args
#         (
#             {},
#             KeyError,
#             'test if valid exception when no args -> pytest.raise(KeyError)'
#         ),
#         # Test 2: Only agent state arg
#         (
#             {'agent_state': ROSAgentState()},
#             KeyError,
#             'test if valid exception when missing obstacles_state and unsafe_set_state -> pytest.raise(KeyError)'
#         ),
#         # Test 3: Only obstacles state arg
#         (
#             {'obstacles_state': ROSObstaclesState()},
#             KeyError,
#             'test if valid exception when missing agent_state and unsafe_set_state -> pytest.raise(KeyError)'
#         ),
#         # Test 4: Only unsafe set state
#         (
#             {'unsafe_set_state': ROSUnsafeSetState()},
#             KeyError,
#             'test if valid exception when missing agent_state and obstacles_state -> pytest.raise(KeyError)'
#         ),
#         # Test 5: Missing unsafe_set_state
#         (
#             {
#                 'agent_state': ROSAgentState(),
#                 'obstacles_state': ROSObstaclesState()
#             },
#             KeyError,
#             'test if valid exception when missing unsafe_set_state -> pytest.raise(KeyError)'
#         ),
#         # Test 6: Missing obstacles_state
#         (
#             {
#                 'agent_state': ROSAgentState(),
#                 'unsafe_set_state': ROSUnsafeSetState()
#             },
#             KeyError,
#             'test if valid exception when missing obstacles_state -> pytest.raise(KeyError)'
#         ),
#         # Test 7: Missing agent_state
#         (
#             {
#                 'obstacles_state': ROSObstaclesState(),
#                 'unsafe_set_state': ROSUnsafeSetState()
#             },
#             KeyError,
#             'test if valid exception when missing agent_state -> pytest.raise(KeyError)'
#         ),
#         # Test 8: Wrong type for agent_state
#         (
#             {
#                 'agent_state': "wrong_type",
#                 'obstacles_state': ROSObstaclesState(),
#                 'unsafe_set_state': ROSUnsafeSetState()
#             },
#             TypeError,
#             'test if valid exception when agent_state is wrong type -> pytest.raise(TypeError)'
#         ),
#         # Test 9: Wrong type for obstacles_state
#         (
#             {
#                 'agent_state': ROSAgentState(),
#                 'obstacles_state': "wrong_type",
#                 'unsafe_set_state': ROSUnsafeSetState()
#             },
#             TypeError,
#             'test if valid exception when obstacles_state is wrong type -> pytest.raise(TypeError)'
#         ),
#         # Test 10: Wrong type for unsafe_set_state
#         (
#             {
#                 'agent_state': ROSAgentState(),
#                 'obstacles_state': ROSObstaclesState(),
#                 'unsafe_set_state': "wrong_type"
#             },
#             TypeError,
#             'test if valid exception when unsafe_set_state is wrong type -> pytest.raise(TypeError)'
#         ),
#         # Test 11: Multiple wrong types
#         (
#             {
#                 'agent_state': "wrong_type",
#                 'obstacles_state': 123,
#                 'unsafe_set_state': ROSUnsafeSetState()
#             },
#             TypeError,
#             'test if valid exception when multiple states have wrong types -> pytest.raise(TypeError)'
#         ),
#         # Test 12: All wrong types
#         (
#             {
#                 'agent_state': "wrong_type",
#                 'obstacles_state': 123,
#                 'unsafe_set_state': []
#             },
#             TypeError,
#             'test if valid exception when all states have wrong types -> pytest.raise(TypeError)'
#         )
#     ]
# )
# def test_unsafe_conditions_guard_state_inputs(
#     state_kwargs: dict,
#     expected_exception,
#     test_description: str
# ):
#     guard = UnsafeConditionsGuard()
#     with pytest.raises(expected_exception):
#         guard.__call__(**state_kwargs)