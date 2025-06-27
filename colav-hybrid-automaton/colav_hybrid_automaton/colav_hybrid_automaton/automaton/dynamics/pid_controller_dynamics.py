from .dynamics import Dynamics
from typing import NamedTuple
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from colav_hybrid_automaton.automaton._internal.utils import quaternion_to_heading
import math

class PIDControllerDynamics(Dynamics):
    """
    PIDYawVelocityController
    A PID controller for velocity and yaw rate based on heading and position error
    relative to the target waypoint.
    """
    
    class PIDDynamicsOutput(NamedTuple):
        velocity: float
        yaw_rate: float

    def __init__(self, **init_kwargs):
        super().__init__(self.PIDDynamicsOutput, **init_kwargs)

        # static PID controller configuration
        self.target_velocity = init_kwargs.get('target_velocity')
        self.dt = init_kwargs.get('dt')
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

        # TODO: Should have an internal state for storing agent_states to help the PID controller. please add this for the future.

    def _validate_initialization(self, **init_kwargs):
        super()._validate_initialization(**init_kwargs)

        # target velocity arg
        try: 
            if not isinstance(init_kwargs['target_velocity'], float):
                raise TypeError()
            if init_kwargs['target_velocity'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
        # dt: this will by used for validation of agent states in buffer rather than for dynamics calculation
        try: 
            if not isinstance(init_kwargs['dt'], float):
                raise TypeError()
            if init_kwargs['dt'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
        # error_tolerance
        try: 
            if not isinstance(init_kwargs['error_tolerance'], float):
                raise TypeError()
            if init_kwargs['error_tolerance'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
        # max_yaw_rate
        try: 
            if not isinstance(init_kwargs['max_yaw_rate'], float):
                raise TypeError()
            if init_kwargs['max_yaw_rate'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
        """ == PID Gains === """
        try: 
            if not isinstance(init_kwargs['yaw_kp'], float):
                raise TypeError()
            if init_kwargs['yaw_kp'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        try: 
            if not isinstance(init_kwargs['yaw_ki'], float):
                raise TypeError()
            if init_kwargs['yaw_ki'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
        try: 
            if not isinstance(init_kwargs['yaw_kd'], float):
                raise TypeError()
            if init_kwargs['yaw_kd'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
        try: 
            if not isinstance(init_kwargs['vel_kp'], float):
                raise TypeError()
            if init_kwargs['vel_kp'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
        try: 
            if not isinstance(init_kwargs['vel_ki'], float):
                raise TypeError()
            if init_kwargs['vel_ki'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()

        try: 
            if not isinstance(init_kwargs['yaw_kd'], float):
                raise TypeError()
            if init_kwargs['yaw_kd'] < 0.0:
                raise ValueError()
        except KeyError as e:
            raise KeyError()
        
    def __call__(self, **state_kwargs) -> PIDDynamicsOutput:
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
    
    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)
    
        # target velocity arg
        try:
            try: 
                if not isinstance(state_kwargs['agent_state'], ROSAgentState):
                    raise TypeError()
            except KeyError as e:
                raise KeyError()
            
            try: 
                if not isinstance(state_kwargs['waypoints_state'], ROSWaypointsState):
                    raise TypeError()
            except KeyError as e:
                raise KeyError()
        except Exception as e:
            raise e
