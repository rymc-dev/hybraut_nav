from .dynamics import DynamicsABC
from typing import NamedTuple
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from colav_hybrid_automaton.automaton._internal.utils import quaternion_to_heading
import math
from colav_hybrid_automaton.automaton.dynamics.dynamics import DynamicsSpec, DynamicsField
from colav_hybrid_automaton.automaton._internal.types import InputSpec

class PIDControllerDynamics(DynamicsABC):
    """
    PIDYawVelocityController
    A PID controller for velocity and yaw rate based on heading and position error
    relative to the target waypoint.
    """
    
    _dynamic_output_spec: DynamicsSpec = (
        DynamicsSpec("AutomatonCMD", description="Automaton outputs for hydrofoil")
        .add_field("velocity", float, unit="m/s", description="Velocity in meters per second")
        .add_field("yaw_rate", float, unit="rad/s", description="Yaw rate in radians per second")
    ).create_dataclass()

    _init_input_spec = [
        InputSpec(name='target_velocity', type=float),
        InputSpec(name='error_tolerance', type=float),
        InputSpec(name='max_yaw_rate', type=float),
        InputSpec(name='yaw_kp', type=float),
        InputSpec(name='yaw_ki', type=float),
        InputSpec(name='yaw_kd', type=float),
        InputSpec(name='vel_kp', type=float),
        InputSpec(name='vel_ki', type=float),
        InputSpec(name='vel_kd', type=float),
        InputSpec(name='target_velocity', type=float),
        InputSpec(name='target_velocity', type=float),
        InputSpec(name='target_velocity', type=float),
    ]

    _state_input_spec = [
        InputSpec(name='agent_state', type=ROSAgentState),
        InputSpec(name='waypoints_state', type=ROSWaypointsState)
    ]

    def __init__(self, **init_kwargs):
        super().__init__(**init_kwargs)

        # static PID controller configuration
        self.target_velocity = init_kwargs.get('target_velocity')
        # self.dt = init_kwargs.get('dt')
        self.error_tolerance = init_kwargs.get('error_tolerance')
        self.max_yaw_rate = init_kwargs.get('max_yaw_rate')

        # PID gains
        self.yaw_kp = init_kwargs.get('yaw_kp')
        self.yaw_ki = init_kwargs.get('yaw_ki')
        self.yaw_kd = init_kwargs.get('yaw_kd')

        self.vel_kp = init_kwargs.get('vel_kp')
        self.vel_ki = init_kwargs.get('vel_ki')
        self.vel_kd = init_kwargs.get('vel_kd')

        # Internal dynamic states: PID state (integrals & previous errors)
        self._heading_error_integral = 0.0
        self._prev_heading_error = 0.0

        self._velocity_error_integral = 0.0
        self._prev_velocity_error = 0.0

        # in the dynamics I want to automatically have buffers for state inputs for improving the PID controllers

        # TODO: Should have an internal state for storing agent_states to help the PID controller. please add this for the future.

    def _validate_initialization(self, **init_kwargs):
        super()._validate_initialization(**init_kwargs)

        # target velocity arg
        if init_kwargs['target_velocity'] < 0.0:
            raise ValueError()

        if init_kwargs['error_tolerance'] < 0.0:
            raise ValueError()

        if init_kwargs['max_yaw_rate'] < 0.0:
            raise ValueError()
        
        """ == PID Gains === """
        if init_kwargs['yaw_kp'] < 0.0:
            raise ValueError()

        if init_kwargs['yaw_ki'] < 0.0:
            raise ValueError()
        
        if init_kwargs['yaw_kd'] < 0.0:
            raise ValueError()
    
        if init_kwargs['vel_kp'] < 0.0:
            raise ValueError()
        
        if init_kwargs['vel_ki'] < 0.0:
            raise ValueError()

        if init_kwargs['yaw_kd'] < 0.0:
            raise ValueError()
    
    def __call__(self, **state_kwargs) -> _dynamic_output_spec:
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

        self.heading_error_integral += heading_error * self.dt
        heading_error_derivative = (heading_error - self.prev_heading_error) / self.dt
        self.prev_heading_error = heading_error

        raw_yaw_rate = (
            self.yaw_kp * heading_error +
            self.yaw_ki * self.heading_error_integral +
            self.yaw_kd * heading_error_derivative
        )
        target_yaw_rate = max(-self.max_yaw_rate, min(raw_yaw_rate, self.max_yaw_rate))

        # Velocity PID
        current_velocity = agent_state.velocity
        velocity_error = self.target_velocity - current_velocity
        self.velocity_error_integral += velocity_error * self.dt
        velocity_error_derivative = (velocity_error - self.prev_velocity_error) / self.dt
        self.prev_velocity_error = velocity_error

        velocity_command = (
            self.vel_kp * velocity_error +
            self.vel_ki * self.velocity_error_integral +
            self.vel_kd * velocity_error_derivative
        )

        # Final target velocity = current + PID adjustment
        final_velocity = current_velocity + velocity_command

        return PIDControllerDynamics(velocity = final_velocity, yaw_rate=target_yaw_rate)