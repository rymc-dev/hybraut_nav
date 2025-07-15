"""
test class for UnsafeConditionsGuard which is a implementaion of the abstract class GuardABC
for use specifcally as a guard within the colav hybrid automaton model.
"""

from colav_hybrid_automaton.automaton.guards import UnsafeConditionsGuard, GuardABC
import pytest
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState
)
from geometry_msgs.msg import Pose, Point
from std_msgs.msg import Float64MultiArray


@pytest.fixture
def guard_instance():
    return UnsafeConditionsGuard()

class TestUnsafeConditionsGuard:
    """test suite for UnsafeConditionsGuard"""

    def test_initialization_and_specs(self, guard_instance: GuardABC):
        """test the initialization and specifications of the class instance are valid"""
        assert guard_instance.init_input_spec_names() == []
        assert guard_instance.init_input_spec_types() == []
        assert guard_instance.state_input_spec_names() == ['agent_state', 'unsafe_set_state']
        assert guard_instance.state_input_spec_types() == [ROSAgentState, ROSUnsafeSetState] 

    def test_string_representations(self, guard_instance: GuardABC):
        """test the string representations of the guard instance"""
        assert repr(guard_instance) == 'UnsafeConditionsGuard(initialized=True)'
        assert str(guard_instance) == 'Guard Function: UnsafeConditionsGuard'

    @pytest.mark.parametrize(
        "state_kwargs, expected_guard_evaluation",
        [
            (
                {
                    'agent_state': ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=10.0),
                    'unsafe_set_state': ROSUnsafeSetState(),
                    'obstacles_state': ROSObstaclesState() 
                }, False
            ),
            (
                {
                    'agent_state': ROSAgentState(pose=Pose(position=Point(x=100.0, y=100.0, z=0.0)), safety_radius=5.0),
                    'unsafe_set_state': ROSUnsafeSetState(
                        convex_hull_vertices=Float64MultiArray(data=[
                            0.0, 0.0,
                            0.0, 20.0,
                            20.0, 20.0,
                            20.0, 0.0
                        ])
                    ),
                    'obstacles_state': ROSObstaclesState() 
                }, False
            ),
            (
                {
                    'agent_state': ROSAgentState(pose=Pose(position=Point(x=10.0, y=10.0, z=0.0)), safety_radius=15.0),
                    'unsafe_set_state': ROSUnsafeSetState(
                        convex_hull_vertices=Float64MultiArray(data=[
                            0.0, 0.0,
                            0.0, 20.0,
                            20.0, 20.0,
                            20.0, 0.0
                        ])
                    ),
                    'obstacles_state': ROSObstaclesState() 
                }, True
            )
        ],
        ids=[
            "No unsafe set data provided → False",
            "Agent is outside the unsafe set → False",
            "Agent safety radius intersects unsafe set → True"
        ]
    )
    def test_unsafe_conditions_guard_comprehensive(
        self,
        state_kwargs: dict,
        expected_guard_evaluation: bool,
        request
    ):
        """
        Tests for UnsafeConditionsGuard:
        - Fires when the agent’s safety radius intersects the unsafe polygon
        - Does not fire when no intersection occurs
        """
        guard = UnsafeConditionsGuard()
        actual_guard_evaluation = guard(**state_kwargs)
        assert actual_guard_evaluation == expected_guard_evaluation, request.node.callspec.id


    @pytest.mark.parametrize(
        "state_kwargs, expected_exception",
        [
            ({}, KeyError),
            ({'agent_state': ROSAgentState()}, KeyError),
            ({'obstacles_state': ROSObstaclesState()}, KeyError),
            ({'unsafe_set_state': ROSUnsafeSetState()}, KeyError),
            ({'agent_state': ROSAgentState(), 'obstacles_state': ROSObstaclesState()}, KeyError),
            ({'obstacles_state': ROSObstaclesState(), 'unsafe_set_state': ROSUnsafeSetState()}, KeyError),
            ({'agent_state': "wrong_type", 'obstacles_state': ROSObstaclesState(), 'unsafe_set_state': ROSUnsafeSetState()}, TypeError),
            ({'agent_state': ROSAgentState(), 'obstacles_state': ROSObstaclesState(), 'unsafe_set_state': "wrong_type"}, TypeError),
            ({'agent_state': "wrong_type", 'unsafe_set_state': ROSUnsafeSetState()}, TypeError),
            ({'agent_state': "wrong_type", 'unsafe_set_state': []}, TypeError)
        ],
        ids=[
            'test if valid exception when no args -> pytest.raise(KeyError)',
            'test if valid exception when missing obstacles_state and unsafe_set_state -> pytest.raise(KeyError)',
            'test if valid exception when missing agent_state and unsafe_set_state -> pytest.raise(KeyError)',
            'test if valid exception when missing agent_state and obstacles_state -> pytest.raise(KeyError)',
            'test if valid exception when missing unsafe_set_state -> pytest.raise(KeyError)',
            'test if valid exception when missing agent_state -> pytest.raise(KeyError)',
            'test if valid exception when agent_state is wrong type -> pytest.raise(TypeError)',
            'test if valid exception when unsafe_set_state is wrong type -> pytest.raise(TypeError)',
            'test if valid exception when multiple states have wrong types -> pytest.raise(TypeError)',
            'test if valid exception when all states have wrong types -> pytest.raise(TypeError)'
        ]
    )
    def test_unsafe_conditions_guard_state_inputs(
        self,
        state_kwargs: dict,
        expected_exception,
        guard_instance: GuardABC
    ):
        """test invalid state inputs"""
        with pytest.raises(expected_exception):
            guard_instance.__call__(**state_kwargs)


if __name__ == '__main__':
    pytest.main([__file__])