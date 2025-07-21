from automaton_models.hybrid.aci_interfaces.dynamics_interface import DynamicsABC
from nodes._internal.utils import quaternion_to_heading
from automaton_models.hybrid.aci_interfaces.dynamics_interface import DynamicsSpecBuilder
from nodes._internal.types import InputSpec

from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
import math
import time
from collections import deque
from typing import NamedTuple

class PIDControllerDynamics(DynamicsABC):
    """
    Enhanced PID controller for velocity and yaw rate control.
    
    Features:
    - Improved velocity control logic
    - Integral windup protection
    - Derivative kick prevention
    - Adaptive dt calculation
    - State buffering for smoother control
    - Proper output saturation
    """
    
    _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

    _init_input_spec = [
        InputSpec(name='control_frequency', type=int),
        InputSpec(name='target_velocity', type=float),
        InputSpec(name='error_tolerance', type=float),
        InputSpec(name='max_velocity', type=float),
        InputSpec(name='max_yaw_rate', type=float),
        InputSpec(name='yaw_kp', type=float),
        InputSpec(name='yaw_ki', type=float),
        InputSpec(name='yaw_kd', type=float),
        InputSpec(name='vel_kp', type=float),
        InputSpec(name='vel_ki', type=float),
        InputSpec(name='vel_kd', type=float),
        InputSpec(name='integral_max', type=float),  # Anti-windup
        InputSpec(name='derivative_filter_alpha', type=float),  # Derivative smoothing
    ]

    _state_input_spec = [
        InputSpec(name='agent_state', type=ROSAgentState),
        InputSpec(name='waypoints_state', type=ROSWaypointsState)
    ]

    def __init__(self, **init_kwargs):
        super().__init__(**init_kwargs)

        # Enhanced PID state tracking
        self._heading_error_integral = 0.0
        self._prev_heading_error = 0.0
        self._filtered_heading_derivative = 0.0

        self._velocity_error_integral = 0.0
        self._prev_velocity_error = 0.0
        self._filtered_velocity_derivative = 0.0

        # Time tracking for adaptive dt
        self._last_time = None
        self._dt = 1.0 / int(init_kwargs['control_frequency'])
        self._avg_dt = self._dt

        # State history buffers for improved derivative calculation
        self._velocity_history = deque(maxlen=5)
        self._heading_error_history = deque(maxlen=5)
        
        # Control output history for smoothing
        self._velocity_output_history = deque(maxlen=3)
        self._yaw_rate_output_history = deque(maxlen=3)

        # Distance-based velocity scaling
        self._min_approach_distance = 2.0  # meters
        self._approach_velocity_scale = 0.3

    def _validate_initialization(self, **init_kwargs):
        super()._validate_initialization(**init_kwargs)

        # Validate all parameters are non-negative
        for param_name, value in init_kwargs.items():
            if param_name in ['yaw_ki', 'yaw_kd', 'vel_ki', 'vel_kd', 'integral_max', 'derivative_filter_alpha']:
                if value < 0.0:
                    raise ValueError(f"init param '{param_name}' must be non-negative, got {value}")
            elif param_name in ['control_frequency', 'max_velocity', 'max_yaw_rate', 'yaw_kp', 'vel_kp']:
                if value <= 0.0:
                    raise ValueError(f"init param '{param_name}' must be positive, got {value}")
        
        # Validate derivative filter alpha is between 0 and 1
        if not (0.0 <= init_kwargs.get('derivative_filter_alpha', 0.1) <= 1.0):
            raise ValueError("derivative_filter_alpha must be between 0.0 and 1.0")

    def _calculate_adaptive_dt(self):
        """Calculate adaptive time step based on actual call frequency."""
        current_time = time.time()
        if self._last_time is not None:
            actual_dt = current_time - self._last_time
            # Use exponential moving average for smoothing
            self._avg_dt = 0.1 * actual_dt + 0.9 * self._avg_dt
            # Clamp to reasonable bounds
            self._avg_dt = max(0.001, min(0.1, self._avg_dt))
        else:
            self._avg_dt = self._dt
        
        self._last_time = current_time
        return self._avg_dt

    def _calculate_distance_to_waypoint(self, agent_state: ROSAgentState, waypoint: ROSWaypoint) -> float:
        """Calculate Euclidean distance to waypoint."""
        dx = waypoint.position.x - agent_state.pose.position.x
        dy = waypoint.position.y - agent_state.pose.position.y
        return math.sqrt(dx * dx + dy * dy)

    def _scale_velocity_for_approach(self, base_velocity: float, distance: float) -> float:
        """Scale velocity down when approaching waypoint."""
        if distance < self._min_approach_distance:
            scale_factor = max(self._approach_velocity_scale, distance / self._min_approach_distance)
            return base_velocity * scale_factor
        return base_velocity

    def _anti_windup_clamp(self, integral: float, max_integral: float) -> float:
        """Prevent integral windup by clamping integral term."""
        return max(-max_integral, min(integral, max_integral))

    def _filtered_derivative(self, current_error: float, prev_error: float, 
                           prev_filtered_derivative: float, dt: float, alpha: float) -> float:
        """Calculate filtered derivative to reduce noise."""
        raw_derivative = (current_error - prev_error) / dt if dt > 0 else 0.0
        return alpha * raw_derivative + (1 - alpha) * prev_filtered_derivative

    def _smooth_output(self, new_value: float, history: deque) -> float:
        """Apply simple moving average to smooth control outputs."""
        history.append(new_value)
        return sum(history) / len(history)

    def __call__(self, **state_kwargs):
        super().__call__(**state_kwargs)

        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')

        # Get current waypoint
        wp: ROSWaypoint = waypoints_state.current_waypoint

        # Calculate adaptive time step
        dt = self._calculate_adaptive_dt()

        # Calculate distance to waypoint
        distance_to_waypoint = self._calculate_distance_to_waypoint(agent_state, wp)

        # ===== YAW CONTROL =====
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

        # Calculate heading error with proper angle wrapping
        heading_error = math.atan2(
            math.sin(desired_heading - current_heading),
            math.cos(desired_heading - current_heading)
        )

        # Update heading error history
        self._heading_error_history.append(heading_error)

        # PID calculation for yaw
        # Proportional term
        yaw_p_term = self.__getattribute__('yaw_kp') * heading_error

        # Integral term with anti-windup
        self._heading_error_integral += heading_error * dt
        integral_max = self.__getattribute__('integral_max')
        self._heading_error_integral = self._anti_windup_clamp(
            self._heading_error_integral, integral_max
        )
        yaw_i_term = self.__getattribute__('yaw_ki') * self._heading_error_integral

        # Filtered derivative term
        alpha = self.__getattribute__('derivative_filter_alpha')
        self._filtered_heading_derivative = self._filtered_derivative(
            heading_error, self._prev_heading_error, 
            self._filtered_heading_derivative, dt, alpha
        )
        yaw_d_term = self.__getattribute__('yaw_kd') * self._filtered_heading_derivative

        # Combine PID terms
        raw_yaw_rate = yaw_p_term + yaw_i_term + yaw_d_term

        # Apply saturation
        max_yaw_rate = self.__getattribute__('max_yaw_rate')
        target_yaw_rate = max(-max_yaw_rate, min(raw_yaw_rate, max_yaw_rate))

        # Smooth output
        target_yaw_rate = self._smooth_output(target_yaw_rate, self._yaw_rate_output_history)

        # Update previous error
        self._prev_heading_error = heading_error

        # ===== VELOCITY CONTROL =====
        current_velocity = agent_state.velocity
        
        # Scale target velocity based on distance to waypoint
        base_target_velocity = self.__getattribute__('target_velocity')
        scaled_target_velocity = self._scale_velocity_for_approach(
            base_target_velocity, distance_to_waypoint
        )

        # Calculate velocity error
        velocity_error = scaled_target_velocity - current_velocity

        # Update velocity history
        self._velocity_history.append(current_velocity)

        # PID calculation for velocity
        # Proportional term
        vel_p_term = self.__getattribute__('vel_kp') * velocity_error

        # Integral term with anti-windup
        self._velocity_error_integral += velocity_error * dt
        self._velocity_error_integral = self._anti_windup_clamp(
            self._velocity_error_integral, integral_max
        )
        vel_i_term = self.__getattribute__('vel_ki') * self._velocity_error_integral

        # Filtered derivative term (derivative of error, not velocity)
        self._filtered_velocity_derivative = self._filtered_derivative(
            velocity_error, self._prev_velocity_error,
            self._filtered_velocity_derivative, dt, alpha
        )
        vel_d_term = self.__getattribute__('vel_kd') * self._filtered_velocity_derivative

        # Combine PID terms for velocity command
        velocity_command = vel_p_term + vel_i_term + vel_d_term

        # CORRECTED: Output target velocity directly, not increment
        final_velocity = scaled_target_velocity + velocity_command

        # Apply velocity saturation
        max_velocity = self.__getattribute__('max_velocity')
        final_velocity = max(0.0, min(final_velocity, max_velocity))

        # Smooth velocity output
        final_velocity = self._smooth_output(final_velocity, self._velocity_output_history)

        # Update previous error
        self._prev_velocity_error = velocity_error

        # Check if we've reached the waypoint
        error_tolerance = self.__getattribute__('error_tolerance')
        if distance_to_waypoint < error_tolerance:
            # Gradually reduce velocity as we approach the waypoint
            final_velocity *= 0.5

        return self.create_output(
            velocity=final_velocity,
            yaw_rate=target_yaw_rate
        )

    def reset_pid_state(self):
        """Reset PID internal state - useful when switching waypoints."""
        self._heading_error_integral = 0.0
        self._prev_heading_error = 0.0
        self._filtered_heading_derivative = 0.0
        
        self._velocity_error_integral = 0.0
        self._prev_velocity_error = 0.0
        self._filtered_velocity_derivative = 0.0
        
        self._velocity_history.clear()
        self._heading_error_history.clear()
        self._velocity_output_history.clear()
        self._yaw_rate_output_history.clear()
        
        self._last_time = None

    def get_pid_diagnostics(self) -> dict:
        """Get current PID state for debugging."""
        return {
            'heading_error_integral': self._heading_error_integral,
            'velocity_error_integral': self._velocity_error_integral,
            'avg_dt': self._avg_dt,
            'velocity_history_length': len(self._velocity_history),
            'heading_error_history_length': len(self._heading_error_history),
        }


# Example usage with improved parameters
if __name__ == '__main__':
    init_kwargs = {
        'control_frequency': 100,
        'target_velocity': 25.0,
        'error_tolerance': 0.3,
        'max_velocity': 30.0,  # Add velocity limit
        'max_yaw_rate': 1.0,   # Increased for better maneuverability
        'yaw_kp': 2.0,         # Increased for better heading tracking
        'yaw_ki': 0.1,         # Moderate integral gain
        'yaw_kd': 0.2,         # Moderate derivative gain
        'vel_kp': 1.0,         # Moderate proportional gain
        'vel_ki': 0.2,         # Moderate integral gain
        'vel_kd': 0.1,         # Small derivative gain
        'integral_max': 10.0,  # Anti-windup limit
        'derivative_filter_alpha': 0.1,  # Derivative smoothing
    }
    
    dynamics: DynamicsABC = PIDControllerDynamics(**init_kwargs)

    from geometry_msgs.msg import Point
    from colav_interfaces.msg import Waypoint

    # Create test state
    wp = Waypoint(position=Point(x=30.0, y=100.0, z=0.0))

    # Create the state dictionary
    state_kwargs = {
        'agent_state': ROSAgentState(),
        'waypoints_state': ROSWaypointsState(current_waypoint=wp)
    }
    
    # Test multiple calls
    for i in range(5):
        dynamic_output = dynamics.__call__(**state_kwargs)
        print(f"Call {i+1}: velocity={dynamic_output.velocity:.3f}, yaw_rate={dynamic_output.yaw_rate:.3f}")
        
        # Simulate some time passing
        import time
        time.sleep(0.01)
    
    # Show diagnostics
    print("\nPID Diagnostics:", dynamics.get_pid_diagnostics())