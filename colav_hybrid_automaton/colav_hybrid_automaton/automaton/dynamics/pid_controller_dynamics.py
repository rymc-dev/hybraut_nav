from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsABC
from typing import NamedTuple
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from colav_hybrid_automaton.automaton._internal.utils import quaternion_to_heading
import math
from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsSpec, DynamicsField
from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsSpecBuilder
from colav_hybrid_automaton.automaton._internal.types import InputSpec

class PIDControllerDynamics(DynamicsABC):
    """
    PIDYawVelocityController
    A PID controller for velocity and yaw rate based on heading and position error
    relative to the target waypoint.
    """
    
    _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

    _init_input_spec = [
        InputSpec(name='control_frequency', type=int),
        InputSpec(name='target_velocity', type=float),
        InputSpec(name='error_tolerance', type=float),
        InputSpec(name='max_yaw_rate', type=float),
        InputSpec(name='yaw_kp', type=float),
        InputSpec(name='yaw_ki', type=float),
        InputSpec(name='yaw_kd', type=float),
        InputSpec(name='vel_kp', type=float),
        InputSpec(name='vel_ki', type=float),
        InputSpec(name='vel_kd', type=float),
    ]

    _state_input_spec = [
        InputSpec(name='agent_state', type=ROSAgentState),
        InputSpec(name='waypoints_state', type=ROSWaypointsState)
    ]

    def __init__(self, **init_kwargs):
        super().__init__(**init_kwargs)

        # Internal dynamic states: PID state (integrals & previous errors)
        self._heading_error_integral = 0.0
        self._prev_heading_error = 0.0

        self._velocity_error_integral = 0.0
        self._prev_velocity_error = 0.0

        self._avg_dt = 1.0 / int(init_kwargs['control_frequency'])

        # in the dynamics I want to automatically have buffers for state inputs for improving the PID controllers

        # TODO: Should have an internal state for storing agent_states to help the PID controller. please add this for the future.



    def _validate_initialization(self, **init_kwargs):
        super()._validate_initialization(**init_kwargs)

        for param_name, value in init_kwargs.items():
            if value < 0.0:
                raise ValueError(f"init param '{param_name}' must be non-negative, got {value}")
    
    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)

        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')

        wp:ROSWaypoint = waypoints_state.current_waypoint

        # Compute desired heading
        dx = wp.position.x - agent_state.pose.position.x
        dy = wp.position.y - agent_state.pose.position.y
        desired_heading = math.atan2(dy, dx)

        # Get current heading
        current_heading = quaternion_to_heading(
            qx=agent_state.pose.orientation.x,
            qy=agent_state.pose.orientation.y,
            qz=agent_state.pose.orientation.z,
            qw=agent_state.pose.orientation.w,
        )

        # Yaw PID
        heading_error = math.atan2(
            math.sin(desired_heading - current_heading),
            math.cos(desired_heading - current_heading)
        )

        self._heading_error_integral += heading_error * self._dt
        heading_error_derivative = (heading_error - self._prev_heading_error) / self._dt
        self._prev_heading_error = heading_error

        raw_yaw_rate = (
            self.__getattribute__('yaw_kp') * heading_error +
            self.__getattribute__('yaw_ki') * self._heading_error_integral +
            self.__getattribute__('yaw_kd') * heading_error_derivative
        )
        target_yaw_rate = max(-self.__getattribute__('max_yaw_rate'), min(raw_yaw_rate, self.__getattribute__('max_yaw_rate')))

        # Velocity PID
        current_velocity = agent_state.velocity
        velocity_error = self.__getattribute__('target_velocity') - current_velocity
        self._velocity_error_integral += velocity_error * self._dt
        velocity_error_derivative = (velocity_error - self._prev_velocity_error) / self._dt
        self._prev_velocity_error = velocity_error

        velocity_command = (
            self.__getattribute__('vel_kp') * velocity_error +
            self.__getattribute__('vel_ki') * self._velocity_error_integral +
            self.__getattribute__('vel_kd') * velocity_error_derivative
        )

        # Final target velocity = current + PID adjustment
        final_velocity = current_velocity + velocity_command

        return self.create_output(
            velocity = final_velocity,
            yaw_rate = target_yaw_rate
        )
    

if __name__ == '__main__':
    init_kwargs = {
        'control_frequency': 100,
        'target_velocity': 25.0,
        'error_tolerance': 0.3,
        'max_yaw_rate': 0.1,
        'yaw_kp': 0.3, 
        'yaw_ki': 0.01,
        'yaw_kd': 0.05,
        'vel_kp': 0.5,
        'vel_ki': 0.05,
        'vel_kd': 0.05
    }
    dynamics: DynamicsABC = PIDControllerDynamics(**init_kwargs)

    state_kwargs = {
        'agent_state': ROSAgentState(),
        'waypoints_state': ROSWaypointsState()
    }
    dynamic_output = dynamics.__call__(**state_kwargs)
    print (dynamic_output)