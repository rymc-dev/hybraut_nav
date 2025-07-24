"""
test file for WaypointReachedGuard which is an implementation of the GuardABC abstractclass
for utilization within the COLAV Hybrid Automaton model
"""

from nodes.guards import WaypointReachedGuard, GuardABC
import pytest
from colav_interfaces.msg import (
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint,
    AgentState as ROSAgentState
)
from geometry_msgs.msg import Point
from geometry_msgs.msg import Pose

@pytest.fixture
def guard_instance():
    return WaypointReachedGuard()

class TestWaypointReachedGuard:

    def test_initialization_and_specs(self, guard_instance: GuardABC):
        """test the initialization and specifications of the class instance are valid"""
        assert guard_instance.init_input_spec_names() == []
        assert guard_instance.init_input_spec_types() == []
        assert guard_instance.state_input_spec_names() == ['agent_state', 'waypoints_state']
        assert guard_instance.state_input_spec_types() == [ROSAgentState, ROSWaypointsState] 

    def test_string_representations(self, guard_instance: GuardABC):
        """test the string representations of the guard instance"""
        assert repr(guard_instance) == 'WaypointReachedGuard(initialized=True)'
        assert str(guard_instance) == 'Guard Function: WaypointReachedGuard'


    @pytest.mark.parametrize(
        "agent_state, waypoints_state, expected_guard_evaluation",
        [
            (ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=10.0), ROSWaypointsState(current_waypoint=ROSWaypoint(position=Point(x=10.0, y=10.0, z=0.0), acceptance_radius= 20.0)), True, ),
        ],
        ids=[
            "agent in waypoint current waypoint acceptance radius → True"
        ]
    )
    def test_guard_evaluation(self, agent_state:ROSAgentState, waypoints_state:ROSWaypointsState, expected_guard_evaluation:bool, request, guard_instance):
        """tests the guard evaluations """
        guard = WaypointReachedGuard()
        state_kwargs = {
            'agent_state': agent_state,
            'waypoints_state': waypoints_state
        }
        actual_guard_evaluation = guard_instance(**state_kwargs)
        assert actual_guard_evaluation == expected_guard_evaluation, request.node.callspec.id

    # NOTE: no initialization args therefore no test for init required

    
    @pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            ({}, KeyError),            
            ({'waypoints_state': ROSWaypointsState()}, KeyError),            
            ({'agent_state': ROSAgentState()}, KeyError),
            ({'agent_state': "wrong_type", 'waypoints_state': ROSWaypointsState()}, TypeError),
            ({'agent_state': ROSAgentState(), 'waypoints_state': "wrong_type"}, TypeError),
            ({'agent_state': 123, 'waypoints_state': 456}, TypeError),
            ({'agent_state': None, 'waypoints_state': ROSWaypointsState()}, TypeError),
            ({'agent_state': ROSAgentState(), 'waypoints_state': None}, TypeError),
        ],
        ids=[
            'no state inputs given -> KeyError("agent_state value not given in **call**")',
            'agent_state missing -> KeyError("agent_state value not given in **call**")',
            'waypoints_state missing -> KeyError("waypoints_state key not given in **call**")',
            'agent_state wrong type -> TypeError("agent_state data passed in **call** invalid type")',
            'waypoints_state wrong type -> TypeError("waypoints_state data passed in **call** invalid type")',
            'both states wrong type -> TypeError("agent_state data passed in **call** invalid type")',
            'agent_state is None -> TypeError("agent_state data passed in **call** invalid type")',
            'waypoints_state is None -> TypeError("waypoints_state data passed in **call** invalid type")'
        ]
    )
    def test_invalid_state_inputs(self,state_kwargs, expected_exception, guard_instance):
        """Tests invalid state inputs when __call__ is utilized"""
        with pytest.raises(expected_exception):
            guard_instance(**state_kwargs) 


if __name__ == '__main__':
    pytest.main([__file__])