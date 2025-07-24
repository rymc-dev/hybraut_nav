"""
Test class for LOSClearToWaypoint Guard which is an implemenation of the abstract class 
GuardABC utilized within the COLAV Hybrid Automaton model.
"""

from  colav_hybrid_automaton.automaton.guards import LOSClearToWaypointGuard, GuardABC
import math
import pytest
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState,
    Waypoint as ROSWaypoint
)
from geometry_msgs.msg import Pose, Point
from std_msgs.msg import Float64MultiArray


@pytest.fixture
def guard_instance():
    return LOSClearToWaypointGuard(los_distance_threshold = 100.0)

class TestLOSClearToWaypointGuard:
    """test suite for LOSClearToWaypointGuard class"""

    def test_initialization_and_specs(self, guard_instance: GuardABC):
        """test the initialization and specifications of the class instance are valid"""
        assert guard_instance.init_input_spec_names() == ['los_distance_threshold']
        assert guard_instance.init_input_spec_types() == [float]
        assert guard_instance.state_input_spec_names() == ['agent_state', 'obstacles_state', 'unsafe_set_state', 'waypoints_state']
        assert guard_instance.state_input_spec_types() == [ROSAgentState, ROSObstaclesState, ROSUnsafeSetState , ROSWaypointsState] 

    def test_string_representations(self, guard_instance: GuardABC):
        """test the string representations of the guard instance"""
        assert repr(guard_instance) == 'LOSClearToWaypointGuard(initialized=True)'
        assert str(guard_instance) == 'Guard Function: LOSClearToWaypointGuard'

    @pytest.mark.parametrize(
        "los_distance_threshold, agent_state, obstacles_state, unsafe_set_state, waypoints_state, expected_guard_evaluation",
        [
            (
                20.0,
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
                ROSObstaclesState(),
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[])),  # Empty unsafe set
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius=5.0)),
                False
            ),
            (
                20.0,  # Distance threshold is 20.0
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
                ROSObstaclesState(),
                # Create unsafe polygon that intersects LOS at distance ~25 (outside threshold of 20)
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    23.0, -2.0,  # Bottom-left of obstacle
                    27.0, -2.0,  # Bottom-right of obstacle  
                    27.0, 2.0,   # Top-right of obstacle
                    23.0, 2.0    # Top-left of obstacle
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=5.0)),
                False
            ),
            (
                30.0,  # Distance threshold is 30.0
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
                ROSObstaclesState(),
                # Create unsafe polygon that intersects LOS at distance ~15 (within threshold of 30)
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    13.0, -2.0,  # Bottom-left of obstacle
                    17.0, -2.0,  # Bottom-right of obstacle
                    17.0, 2.0,   # Top-right of obstacle
                    13.0, 2.0    # Top-left of obstacle
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=5.0)),
                True
            ),
            (
                25.0,  # Distance threshold is 25.0
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=10.0),
                ROSObstaclesState(),
                # Create unsafe polygon that intersects LOS at distance exactly 25 (at threshold boundary)
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    24.0, -1.0,  # Bottom-left of obstacle
                    26.0, -1.0,  # Bottom-right of obstacle
                    26.0, 1.0,   # Top-right of obstacle
                    24.0, 1.0    # Top-left of obstacle
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=5.0)),
                True
            ),
            (
                1.0,  # Very small distance threshold
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=2.0),
                ROSObstaclesState(),
                # Unsafe polygon very close to agent (within 1.0 threshold)
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    0.5, -0.5,   # Bottom-left of obstacle
                    1.5, -0.5,   # Bottom-right of obstacle
                    1.5, 0.5,    # Top-right of obstacle
                    0.5, 0.5     # Top-left of obstacle
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=0.0, z=0.0), acceptance_radius=1.0)),
                True
            ),
            (
                15.0,
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=5.0),
                ROSObstaclesState(),
                # Unsafe polygon intersecting diagonal LOS at distance ~7.07 (within threshold of 15)
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    4.0, 4.0,    # Bottom-left of obstacle
                    6.0, 4.0,    # Bottom-right of obstacle
                    6.0, 6.0,    # Top-right of obstacle
                    4.0, 6.0     # Top-left of obstacle
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=20.0, y=20.0, z=0.0), acceptance_radius=3.0)),
                True
            ),
            (
                40.0,
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=8.0),
                ROSObstaclesState(),
                # L-shaped unsafe polygon that intersects LOS multiple times, closest at ~10 units
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    8.0, -3.0,   # Bottom-left of vertical part
                    12.0, -3.0,  # Bottom-right of vertical part
                    12.0, 1.0,   # Corner point
                    25.0, 1.0,   # Bottom-right of horizontal part
                    25.0, 3.0,   # Top-right of horizontal part
                    8.0, 3.0     # Top-left (back to start)
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=4.0)),
                True
            ),
            (
                10.0,
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=5.0),
                ROSObstaclesState(),
                # Unsafe polygon near waypoint at distance ~45 from agent (outside threshold of 10)
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    43.0, -2.0,  # Bottom-left near waypoint
                    47.0, -2.0,  # Bottom-right near waypoint
                    47.0, 2.0,   # Top-right near waypoint
                    43.0, 2.0    # Top-left near waypoint
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=2.0)),
                False
            ),
            (
                5.0,
                ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=3.0),
                ROSObstaclesState(),
                # Unsafe polygon nearby but shouldn't affect zero-length LOS
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    8.0, 8.0,    # Bottom-left
                    12.0, 8.0,   # Bottom-right
                    12.0, 12.0,  # Top-right
                    8.0, 12.0    # Top-left
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius=1.0)),
                False,
                
            ),
            (
                1000.0,  # Very large threshold
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=15.0),
                ROSObstaclesState(),
                # Unsafe polygon far from agent but within large threshold
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    198.0, -5.0,  # Bottom-left at distance ~200
                    202.0, -5.0,  # Bottom-right at distance ~200
                    202.0, 5.0,   # Top-right at distance ~200
                    198.0, 5.0    # Top-left at distance ~200
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=500.0, y=0.0, z=0.0), acceptance_radius=10.0)),
                True,
                
            ),
            (
                20.0,
                ROSAgentState(pose=Pose(position=Point(x=-10.0, y=-10.0, z=0.0)), safety_radius=5.0),
                ROSObstaclesState(),
                # Unsafe polygon in negative coordinate space, intersecting LOS at distance ~7.07
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    -6.0, -6.0,  # Bottom-left
                    -4.0, -6.0,  # Bottom-right
                    -4.0, -4.0,  # Top-right
                    -6.0, -4.0   # Top-left
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius=3.0)),
                True,
                
            ),
            (
                25.0,
                ROSAgentState(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=4.0),
                ROSObstaclesState(),
                # Very thin unsafe polygon that just touches the LOS line at distance 20
                ROSUnsafeSetState(convex_hull_vertices=Float64MultiArray(data=[
                    20.0, 0.0,   # Point touching LOS
                    20.1, -0.1,  # Bottom-right (very small)
                    20.1, 0.1,   # Top-right (very small)
                    20.0, 0.0    # Back to touching point
                ])),
                ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=50.0, y=0.0, z=0.0), acceptance_radius=2.0)),
                True,
                
            )
        ],
        ids=[
            "test: no unsafe set or obstacles with agent on waypoints state -> expected guard evaluation: False",
            "test: unsafe set on los to current waypoint but interception just outside distance threshold -> expected guard evaluation: False",
            "test: unsafe set on los to current waypoint but interception just within the distance threshold -> expected guard evaluation: True",
            "test: unsafe set intersects LOS exactly at distance threshold boundary -> expected guard evaluation: True",
            "test: very small distance threshold with nearby unsafe set -> expected guard evaluation: True",
            "test: diagonal LOS path with unsafe set intersection within threshold -> expected guard evaluation: True",
            "test: complex polygon with multiple LOS intersections, closest within threshold -> expected guard evaluation: True",
            "test: unsafe set near waypoint but outside distance threshold from agent -> expected guard evaluation: False",
            "test: agent and waypoint at same position with nearby unsafe set -> expected guard evaluation: False",
            "test: very large distance threshold catches distant intersection -> expected guard evaluation: True",
            "test: negative coordinates with unsafe set intersection within threshold -> expected guard evaluation: True",
            "test: unsafe set barely touches LOS line within threshold -> expected guard evaluation: True",
        ]
    )
    def test_los_clear_to_waypoint_comprehensive(
        self,
        los_distance_threshold: float,
        agent_state: ROSAgentState,
        obstacles_state: ROSObstaclesState,
        unsafe_set_state: ROSUnsafeSetState,
        waypoints_state: ROSWaypointsState,
        expected_guard_evaluation: bool,
        request
    ):
        """Comprehensive test for LOSClearToWaypointGuard with boundary conditions.
        
        Args:
            los_distance_threshold (float): The distance threshold for LOS analysis.
            agent_state (ROSAgentState): The agent's current state.
            obstacles_state (ROSObstaclesState): State of obstacles in the environment.
            unsafe_set_state (ROSUnsafeSetState): State of the unsafe set.
            waypoints_state (ROSWaypointsState): State of waypoints.
            expected_guard_evaluation (bool): Expected result of guard evaluation.
            test_description (str): Description of the test case.
        """
        init_kwargs = {
            'los_distance_threshold': los_distance_threshold
        }
        
        guard = LOSClearToWaypointGuard(**init_kwargs)
        
        assert guard.__repr__() == "LOSClearToWaypointGuard(initialized=True)"
        assert guard.__str__() == "Guard Function: LOSClearToWaypointGuard"
        
        guard_info = guard.get_guard_info()
        assert guard_info["class_name"] == 'LOSClearToWaypointGuard'
        assert guard_info["module"] == 'colav_hybrid_automaton.automaton.guards.los_clear_to_waypoint_guard'
        assert guard_info['is_initialized'] == True
        
        state_kwargs = {
            'agent_state': agent_state,
            'obstacles_state': obstacles_state,
            'unsafe_set_state': unsafe_set_state,
            'waypoints_state': waypoints_state
        }
        
        actual_guard_evaluation = guard.__call__(**state_kwargs)
        assert actual_guard_evaluation == expected_guard_evaluation, request.node.callspec.id

    @pytest.mark.parametrize(
        "init_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'los_distance_threshold': "invalid_type"}, TypeError),
            ({'los_distance_threshold': -0.01}, ValueError),
        ],
        ids=[
            "No args -> pytest.error(KeyError)",
            "Invalid distance threshold type -> pytest.error(TypeError)",
            "Negative los_distance_threshold → pytest.error(ValueError)"
        ]
    )
    def test_invalid_initialization(
        self,
        init_kwargs: ROSWaypointsState,
        expected_exception: Exception
    ):
        """tests invalid initialization args for __init__ being called"""
        with pytest.raises(expected_exception):
            LOSClearToWaypointGuard(**init_kwargs)

    @pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({
                'waypoints_state': ROSWaypointsState(),
                'unsafe_set_state': ROSUnsafeSetState(),
                'obstacles_state': ROSObstaclesState()
            }, KeyError),
            ({
                'agent_state': "wrong_type",
                'waypoints_state': ROSWaypointsState(),
                'unsafe_set_state': ROSUnsafeSetState(),
                'obstacles_state': ROSObstaclesState()
            }, TypeError),
            ({
                'agent_state': ROSAgentState(),
                'unsafe_set_state': ROSUnsafeSetState(),
                'obstacles_state': ROSObstaclesState()
            }, KeyError),
            ({
                'agent_state': ROSAgentState(),
                'waypoints_state': "wrong_type",
                'unsafe_set_state': ROSUnsafeSetState(),
                'obstacles_state': ROSObstaclesState()
            }, TypeError),
            ({
                'agent_state': ROSAgentState(),
                'waypoints_state': ROSWaypointsState(),
                'obstacles_state': ROSObstaclesState()
            }, KeyError),
            ({
                'agent_state': ROSAgentState(),
                'waypoints_state': ROSWaypointsState(),
                'unsafe_set_state': "wrong_type",
                'obstacles_state': ROSObstaclesState()
            }, TypeError),
            ({
                'agent_state': ROSAgentState(),
                'waypoints_state': ROSWaypointsState(),
                'unsafe_set_state': ROSUnsafeSetState()
            }, KeyError),
            ({
                'agent_state': ROSAgentState(),
                'waypoints_state': ROSWaypointsState(),
                'unsafe_set_state': ROSUnsafeSetState(),
                'obstacles_state': "wrong_type"
            }, TypeError),
        ],
        ids=[
            "no_args_keyerror",
            "missing_agent_state_keyerror",
            "wrong_agent_state_type_typeerror",
            "missing_waypoints_state_keyerror",
            "wrong_waypoints_state_type_typeerror",
            "missing_unsafe_set_state_keyerror",
            "wrong_unsafe_set_state_type_typeerror",
            "missing_obstacles_state_keyerror",
            "wrong_obstacles_state_type_typeerror"
        ]
    )
    def test_invalid_state_inputs(
        self,
        state_kwargs: dict,
        expected_exception: Exception,
        guard_instance: "GuardABC"  # Use quotes if GuardABC is a forward reference
    ):
        """Parameterized test for variations of invalid state inputs."""
        with pytest.raises(expected_exception):
            guard_instance(**state_kwargs)


if __name__ == '__main__':
    pytest.main([__file__])