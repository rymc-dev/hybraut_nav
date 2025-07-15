from automaton.invariants import IsGoalWaypointInvariant, InvariantABC
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint
import pytest
from geometry_msgs.msg import Pose, Point


@pytest.fixture
def is_goal_waypoint_invaraint_instance():
    return IsGoalWaypointInvariant()

class TestIsGoalWaypointInvariant:

    def test_initialization_and_specs(self, is_goal_waypoint_invaraint_instance: InvariantABC):
        """test the initialization and specifications of the class instance are valid"""
        assert is_goal_waypoint_invaraint_instance.init_input_spec_names() == []
        assert is_goal_waypoint_invaraint_instance.init_input_spec_types() == []
        assert is_goal_waypoint_invaraint_instance.state_input_spec_names() == ['waypoints_state']
        assert is_goal_waypoint_invaraint_instance.state_input_spec_types() == [ROSWaypointsState] 

    def test_string_representations(self, is_goal_waypoint_invaraint_instance: InvariantABC):
        """test the string representations of the guard instance"""
        assert repr(is_goal_waypoint_invaraint_instance) == 'IsGoalWaypointInvariant(initialized=True)'
        assert str(is_goal_waypoint_invaraint_instance) == 'Invariant Function: IsGoalWaypointInvariant'

    @pytest.mark.parametrize(
        "state_kwargs, expected_invariant_evaluation",
        [
            (
                {
                    'waypoints_state': ROSWaypointsState(
                        current_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0))),
                        goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0))),
                        virtual_waypoints=[]
                    )
                }, 
                True                 
            ),            
            (
                {
                    'waypoints_state': ROSWaypointsState(
                        current_waypoint=ROSWaypoint(position=Pose(position=Point(x=0.0, y=0.0))),
                        virtual_waypoints=[ROSWaypoint(position=Pose(position=Point(x=5.0, y=5.0)))],
                        goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0)))
                    )
                },
                False
            ),
            (
                {
                    'waypoints_state': ROSWaypointsState(
                        current_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0))),
                        virtual_waypoints=[ROSWaypoint(position=Pose(position=Point(x=5.0, y=5.0)))],
                        goal_waypoint=ROSWaypoint(position=Pose(position=Point(x=10.0, y=10.0)))
                    )
                },
                False
            ),            
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
                False
            ),
        ],
        ids=[
            'Current waypoint equals goal waypoint with no virtual waypoints -> True',
            'Virtual waypoints exist -> False',
            'Virtual waypoints exist even when current equals goal -> False',
            'Multiple virtual waypoints exist -> False'
        ]
    )
    def test_invariant_evaluation(self, state_kwargs: dict, expected_invariant_evaluation: bool, request, is_goal_waypoint_invaraint_instance):
        """
        Test IsGoalWaypointInvariant with various waypoint configurations.
        
        The invariant logic:
        1. If virtual_waypoints exist (len > 0) -> return False
        2. If no virtual waywaypoints AND current == goal -> return True  
        3. If no virtual waypoints AND current != goal -> raise Exception
        """

        assert is_goal_waypoint_invaraint_instance(**state_kwargs) == expected_invariant_evaluation, request.node.callspec.id

    @pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'waypoints_state': "invalid_type"}, TypeError),
        ],
        ids=[
            "No args -> pytest.error(ValueError)",
            "Invalid State -> pytest.error(TypeError)"
        ]
    )
    def test_virtual_waypoints_guard_invalid_state_kwargs(
        self,
        state_kwargs: ROSWaypointsState,
        expected_exception: Exception,
        is_goal_waypoint_invaraint_instance
    ):
        """test with invalid state kwargs"""
        with pytest.raises(expected_exception):
            is_goal_waypoint_invaraint_instance.__call__(**state_kwargs)

if __name__ == '__main__':
    pytest.main([__file__])