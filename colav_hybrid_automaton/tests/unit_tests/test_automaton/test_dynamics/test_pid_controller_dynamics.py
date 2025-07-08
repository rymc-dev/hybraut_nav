import pytest
from colav_hybrid_automaton.automaton.dynamics import PIDControllerDynamics, DynamicsABC
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState
)

@pytest.mark.parametrize(
        "init_kwargs, state_kwargs, expected_velocity, expected_yaw_rate",
        (
            # Test Case 1: 
            {
                "control_frequency": 100,
                "target_velocity": 30.0,
                "error_tolerance": 0.3,
                "max_yaw_rate": 0.1,
                "yaw_kp": 0.3,
                "yaw_ki": 0.01,
                "yaw_kd": 0.05,
                "vel_kp": 0.05,
                "vel_ki": 0.01,
                "vel_kd": 0.05
            },
            {
                "agent_state": ROSAgentState(),
                "waypoints_state": ROSWaypointsState()
            },
            10.0,
            0.2
        ),
        ids=[
            "Test Case 1: "
        ]
)
def test_pid_controller_dynamics_comprehensive(init_kwargs, state_kwargs, expected_velocity, expected_yaw_rate):
    dynamics: DynamicsABC = PIDControllerDynamics(**init_kwargs)
    output = dynamics.__call__(**state_kwargs)

    print(output.velocity)
    print(output.yaw_rate)

    output = dynamics.__call__(**state_kwargs)

    print(output.velocity)
    print(output.yaw_rate)



# @pytest.mark.parametrize(
        
# )
# def test_pid_controller_dynamics_invalid_initialization():
#     pass

# @pytest.mark.parametrize(
        
# )
# def test_pid_controller_dynamics_invalid_state_inputs():
#     pass


if __name__ == '__main__':
    test_pid_controller_dynamics_comprehensive(
        init_kwargs={
            "control_frequency": 100,
            "target_velocity": 30.0,
            "error_tolerance": 0.3,
            "max_yaw_rate": 0.1,
            "yaw_kp": 0.3,
            "yaw_ki": 0.01,
            "yaw_kd": 0.05,
            "vel_kp": 0.05,
            "vel_ki": 0.01,
            "vel_kd": 0.05
        },
        state_kwargs={
            "agent_state": ROSAgentState(),
            "waypoints_state": ROSWaypointsState()
        },
        expected_velocity=10.0,
        expected_yaw_rate=0.2
    )