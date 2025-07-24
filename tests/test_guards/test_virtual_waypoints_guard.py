from hybraut_lifecycle.guards import VirtualWaypointsGuard, GuardABC
import pytest
from colav_interfaces.msg import WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint

@pytest.fixture
def guard_instance():
    return VirtualWaypointsGuard()

class TestVirtualWaypointsGuard:
    """test suite for virutal waypoints guard"""

    def test_initialization_and_specs(self, guard_instance: GuardABC):
        """test the initialization and specifications of the class instance are valid"""
        assert guard_instance.init_input_spec_names() == []
        assert guard_instance.init_input_spec_types() == []
        assert guard_instance.state_input_spec_names() == ['waypoints_state']
        assert guard_instance.state_input_spec_types() == [ROSWaypointsState] 

    def test_string_representations(self, guard_instance: GuardABC):
        """test the string representations of the guard instance"""
        assert repr(guard_instance) == 'VirtualWaypointsGuard(initialized=True)'
        assert str(guard_instance) == 'Guard Function: VirtualWaypointsGuard'

    @pytest.mark.parametrize(
        "waypoints_state, expected_guard_evaluation",
        [
            (ROSWaypointsState(virtual_waypoints=[ROSWaypoint()]), True),
            (ROSWaypointsState(virtual_waypoints=[]), False),
            (ROSWaypointsState(), False),
        ],
        ids=[
            "One virtual waypoint → True",
            "Empty virtual_waypoints list → False",
            "No virtual_waypoints attribute set → False"
        ]
    )
    def test_guard_evaluation(
        self,
        waypoints_state: ROSWaypointsState,
        expected_guard_evaluation: bool,
        request,
        guard_instance
    ):
        """
        Comprehensive tests for VirtualWaypointsGuard:
        - fires when there is at least one virtual waypoint
        - does not fire when there are none
        """
        assert guard_instance(waypoints_state=waypoints_state) == expected_guard_evaluation, request.node.callspec.id

    # NOTE: No initialization args for this guard so no init_kwarg validation required

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
    def test_invalid_state_kwargs(
        self,
        state_kwargs: ROSWaypointsState,
        expected_exception: Exception,
        guard_instance
    ):
        """test guard call with invalid args"""
        with pytest.raises(expected_exception):
            guard_instance.__call__(**state_kwargs)

if __name__ == '__main__':
    pytest.main([__file__])