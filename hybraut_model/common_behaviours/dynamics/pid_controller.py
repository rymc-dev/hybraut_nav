from automaton_models.hybraut_model.aci_interfaces.dynamics_interface import DynamicsInterface
from automaton_models.hybraut_model.aci_interfaces.dynamics_interface import DynamicsSpecBuilder
from automaton.spec import IOSpec
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
import math
import time
from collections import deque
from typing import NamedTuple, Dict, Any


def quaternion_to_heading(qx, qy, qz, qw) -> float:
    """Convert quaternion to heading angle in radians."""
    # Yaw (Z-axis rotation)
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)

class PIDControllerDynamics(DynamicsInterface):
    """
    Enhanced PID controller for velocity and yaw rate control using state buffer.
    
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
        IOSpec.create_io_spec(name='control_frequency', type=int),
        IOSpec.create_io_spec(name='target_velocity', type=float),
        IOSpec.create_io_spec(name='error_tolerance', type=float),
        IOSpec.create_io_spec(name='max_velocity', type=float),
        IOSpec.create_io_spec(name='max_yaw_rate', type=float),
        IOSpec.create_io_spec(name='yaw_kp', type=float),
        IOSpec.create_io_spec(name='yaw_ki', type=float),
        IOSpec.create_io_spec(name='yaw_kd', type=float),
        IOSpec.create_io_spec(name='vel_kp', type=float),
        IOSpec.create_io_spec(name='vel_ki', type=float),
        IOSpec.create_io_spec(name='vel_kd', type=float),
        IOSpec.create_io_spec(name='integral_max', type=float),  # Anti-windup
        IOSpec.create_io_spec(name='derivative_filter_alpha', type=float),  # Derivative smoothing
    ]

    _state_input_spec = [
        IOSpec.create_io_spec(name='agent_state', type=ROSAgentState),
        IOSpec.create_io_spec(name='waypoints_state', type=ROSWaypointsState)
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

        # Control output history for smoothing
        self._velocity_output_history = deque(maxlen=3)
        self._yaw_rate_output_history = deque(maxlen=3)

        # Distance-based velocity scaling
        self._min_approach_distance = 2.0  # meters
        self._approach_velocity_scale = 0.3

        # Additional state tracking for buffer analysis
        self._velocity_trend_buffer = deque(maxlen=5)
        self._heading_error_trend_buffer = deque(maxlen=5)

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
            # Use the built-in exponential moving average method
            self._avg_dt_calc(actual_dt)
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

    def _analyze_velocity_trend(self) -> float:
        """Analyze velocity trend from buffered agent states."""
        agent_state_buffer = self._state_buffer['agent_state']
        
        if len(agent_state_buffer) < 2:
            return 0.0
        
        # Calculate velocity trend from recent states
        velocities = [state.velocity for state in agent_state_buffer]
        self._velocity_trend_buffer.extend(velocities)
        
        # Simple linear trend calculation
        if len(self._velocity_trend_buffer) >= 3:
            recent_velocities = list(self._velocity_trend_buffer)[-3:]
            trend = (recent_velocities[-1] - recent_velocities[0]) / len(recent_velocities)
            return trend
        
        return 0.0

    def _analyze_heading_stability(self, current_heading_error: float) -> float:
        """Analyze heading error stability from buffered states."""
        self._heading_error_trend_buffer.append(current_heading_error)
        
        if len(self._heading_error_trend_buffer) < 3:
            return 0.0
        
        # Calculate heading error variance as stability measure
        errors = list(self._heading_error_trend_buffer)
        mean_error = sum(errors) / len(errors)
        variance = sum((e - mean_error) ** 2 for e in errors) / len(errors)
        
        # Return stability factor (lower variance = more stable)
        return max(0.0, 1.0 - variance)

    def _evaluate(self, **state_kwargs):
        """Core PID evaluation logic using state buffer."""
        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')

        # Get current waypoint
        wp: ROSWaypoint = waypoints_state.current_waypoint

        # Calculate adaptive time step
        dt = self._calculate_adaptive_dt()

        # Calculate distance to waypoint
        distance_to_waypoint = self._calculate_distance_to_waypoint(agent_state, wp)

        # Analyze trends from state buffer
        velocity_trend = self._analyze_velocity_trend()

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

        # Analyze heading stability
        heading_stability = self._analyze_heading_stability(heading_error)

        # PID calculation for yaw with stability adjustment
        # Proportional term
        yaw_kp = self.__getattribute__('yaw_kp')
        yaw_p_term = yaw_kp * heading_error

        # Integral term with anti-windup
        self._heading_error_integral += heading_error * dt
        integral_max = self.__getattribute__('integral_max')
        self._heading_error_integral = self._anti_windup_clamp(
            self._heading_error_integral, integral_max
        )
        yaw_ki = self.__getattribute__('yaw_ki')
        yaw_i_term = yaw_ki * self._heading_error_integral

        # Filtered derivative term
        alpha = self.__getattribute__('derivative_filter_alpha')
        self._filtered_heading_derivative = self._filtered_derivative(
            heading_error, self._prev_heading_error, 
            self._filtered_heading_derivative, dt, alpha
        )
        yaw_kd = self.__getattribute__('yaw_kd')
        yaw_d_term = yaw_kd * self._filtered_heading_derivative

        # Combine PID terms with stability adjustment
        raw_yaw_rate = yaw_p_term + yaw_i_term + yaw_d_term
        
        # Reduce yaw rate if heading is unstable
        if heading_stability < 0.5:
            raw_yaw_rate *= (0.5 + heading_stability)

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

        # PID calculation for velocity with trend compensation
        # Proportional term
        vel_kp = self.__getattribute__('vel_kp')
        vel_p_term = vel_kp * velocity_error

        # Integral term with anti-windup
        self._velocity_error_integral += velocity_error * dt
        self._velocity_error_integral = self._anti_windup_clamp(
            self._velocity_error_integral, integral_max
        )
        vel_ki = self.__getattribute__('vel_ki')
        vel_i_term = vel_ki * self._velocity_error_integral

        # Filtered derivative term
        self._filtered_velocity_derivative = self._filtered_derivative(
            velocity_error, self._prev_velocity_error,
            self._filtered_velocity_derivative, dt, alpha
        )
        vel_kd = self.__getattribute__('vel_kd')
        vel_d_term = vel_kd * self._filtered_velocity_derivative

        # Combine PID terms for velocity command
        velocity_command = vel_p_term + vel_i_term + vel_d_term

        # Apply trend compensation
        trend_compensation = -0.1 * velocity_trend  # Counteract velocity trend
        velocity_command += trend_compensation

        # Calculate final velocity
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
        
        self._velocity_output_history.clear()
        self._yaw_rate_output_history.clear()
        self._velocity_trend_buffer.clear()
        self._heading_error_trend_buffer.clear()
        
        self._last_time = None

    def get_pid_diagnostics(self) -> Dict[str, Any]:
        """Get current PID state for debugging."""
        return {
            'heading_error_integral': self._heading_error_integral,
            'velocity_error_integral': self._velocity_error_integral,
            'avg_dt': self._avg_dt,
            'agent_state_buffer_size': len(self._state_buffer.get('agent_state', [])),
            'waypoints_state_buffer_size': len(self._state_buffer.get('waypoints_state', [])),
            'velocity_trend_buffer_size': len(self._velocity_trend_buffer),
            'heading_error_trend_buffer_size': len(self._heading_error_trend_buffer),
            'state_buffer_keys': list(self._state_buffer.keys()),
        }

    def get_buffer_analysis(self) -> Dict[str, Any]:
        """Get analysis of buffered state data."""
        agent_states = self._state_buffer.get('agent_state', deque())
        
        if len(agent_states) < 2:
            return {'status': 'insufficient_data'}
        
        # Analyze velocity statistics
        velocities = [state.velocity for state in agent_states]
        avg_velocity = sum(velocities) / len(velocities)
        velocity_variance = sum((v - avg_velocity) ** 2 for v in velocities) / len(velocities)
        
        # Analyze position changes
        positions = [(state.pose.position.x, state.pose.position.y) for state in agent_states]
        if len(positions) >= 2:
            total_distance = sum(
                math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                for p1, p2 in zip(positions[:-1], positions[1:])
            )
            avg_distance_per_step = total_distance / (len(positions) - 1)
        else:
            avg_distance_per_step = 0.0
        
        return {
            'status': 'analyzed',
            'buffer_size': len(agent_states),
            'avg_velocity': avg_velocity,
            'velocity_variance': velocity_variance,
            'avg_distance_per_step': avg_distance_per_step,
            'velocity_trend': self._analyze_velocity_trend(),
        }


# Example usage with improved parameters
if __name__ == '__main__':
    init_kwargs = {
        'control_frequency': 100,
        'target_velocity': 25.0,
        'error_tolerance': 0.3,
        'max_velocity': 30.0,
        'max_yaw_rate': 1.0,
        
        # HEADING CONTROLLER - Significantly reduced gains
        'yaw_kp': 0.8,          # Reduced from 2.0 - less aggressive response
        'yaw_ki': 0.01,         # Reduced from 0.1 - much less integral buildup
        'yaw_kd': 0.4,          # Increased from 0.2 - more damping to reduce oscillations
        
        # VELOCITY CONTROLLER - Keep existing (working well)
        'vel_kp': 1.0,
        'vel_ki': 0.2,
        'vel_kd': 0.1,
        
        # INTEGRAL LIMITS - Tighter control
        'integral_max': 2.0,    # Reduced from 10.0 - prevent excessive windup
        'derivative_filter_alpha': 0.15,  # Slightly increased - better noise filtering
    }
    
    dynamics = PIDControllerDynamics(**init_kwargs)

    from geometry_msgs.msg import Point, Pose, Quaternion
    from colav_interfaces.msg import Waypoint

    # Create multiple waypoints for more interesting behavior
    waypoints = [
        Waypoint(position=Point(x=30.0, y=100.0, z=0.0)),
        Waypoint(position=Point(x=50.0, y=120.0, z=0.0)),
        Waypoint(position=Point(x=70.0, y=90.0, z=0.0)),
        Waypoint(position=Point(x=80.0, y=70.0, z=0.0)),
    ]

    # Simulate vehicle state with realistic dynamics - MOVED BEFORE FUNCTION
    vehicle_x, vehicle_y = 0.0, 0.0
    vehicle_velocity = 0.0
    vehicle_heading = 0.0
    
    def create_quaternion_from_yaw(yaw):
        """Create quaternion from yaw angle"""
        return Quaternion(
            x=0.0,
            y=0.0,
            z=math.sin(yaw / 2.0),
            w=math.cos(yaw / 2.0)
        )

    def simulate_vehicle_dynamics(vel_cmd, yaw_rate_cmd, dt):
        """Simple vehicle dynamics simulation"""
        global vehicle_x, vehicle_y, vehicle_velocity, vehicle_heading
        
        # Simple first-order dynamics for velocity
        vel_time_constant = 0.5  # seconds
        vehicle_velocity += (vel_cmd - vehicle_velocity) * dt / vel_time_constant
        
        # Simple first-order dynamics for heading
        heading_time_constant = 0.3  # seconds
        vehicle_heading += yaw_rate_cmd * dt
        
        # Update position
        vehicle_x += vehicle_velocity * math.cos(vehicle_heading) * dt
        vehicle_y += vehicle_velocity * math.sin(vehicle_heading) * dt
        
        # Add some noise to make it more realistic
        import random
        noise_scale = 0.1
        vehicle_velocity += random.uniform(-noise_scale, noise_scale)
        vehicle_heading += random.uniform(-0.05, 0.05)
    
    # Test with multiple scenarios
    print("=== Testing PID Controller with Dynamic Simulation ===")
    
    current_waypoint_idx = 0
    dt = 0.01
    
    for i in range(10000):
        # Create current agent state
        agent_state = ROSAgentState()
        agent_state.pose = Pose(
            position=Point(x=vehicle_x, y=vehicle_y, z=0.0),
            orientation=create_quaternion_from_yaw(vehicle_heading)
        )
        agent_state.velocity = vehicle_velocity
        
        # Check if we need to switch waypoints
        current_wp = waypoints[current_waypoint_idx]
        distance_to_wp = math.sqrt(
            (current_wp.position.x - vehicle_x)**2 + 
            (current_wp.position.y - vehicle_y)**2
        )
        
        if distance_to_wp < 5.0 and current_waypoint_idx < len(waypoints) - 1:
            current_waypoint_idx += 1
            dynamics.reset_pid_state()  # Reset PID when switching waypoints
            print(f"  --> Switching to waypoint {current_waypoint_idx}")
        
        # Create state dictionary
        state_kwargs = {
            'agent_state': agent_state,
            'waypoints_state': ROSWaypointsState(current_waypoint=waypoints[current_waypoint_idx])
        }
        
        # Get PID output
        dynamic_output = dynamics(**state_kwargs)
        
        # Simulate vehicle response to commands
        simulate_vehicle_dynamics(dynamic_output.velocity, dynamic_output.yaw_rate, dt)
        
        # Print every 50 iterations
        if i % 50 == 0:
            print(f"Step {i:3d}: pos=({vehicle_x:6.2f},{vehicle_y:6.2f}), "
                  f"vel={vehicle_velocity:5.2f}, heading={vehicle_heading:5.2f}, "
                  f"vel_cmd={dynamic_output.velocity:5.2f}, yaw_cmd={dynamic_output.yaw_rate:5.2f}, "
                  f"dist_to_wp={distance_to_wp:5.2f}")
        
        # Simulate some time passing
        time.sleep(0.001)  # Faster simulation
    
    # Show final diagnostics
    print("\n=== Final Diagnostics ===")
    print("PID Diagnostics:", dynamics.get_pid_diagnostics())
    print("Buffer Analysis:", dynamics.get_buffer_analysis())
    
    # Test with different scenarios
    print("\n=== Testing Edge Cases ===")
    
    # Test 1: Large initial error
    print("\n--- Test 1: Large Initial Error ---")
    dynamics.reset_pid_state()
    far_agent = ROSAgentState()
    far_agent.pose = Pose(
        position=Point(x=-50.0, y=-50.0, z=0.0),
        orientation=create_quaternion_from_yaw(math.pi)  # Facing opposite direction
    )
    far_agent.velocity = 5.0
    
    far_state_kwargs = {
        'agent_state': far_agent,
        'waypoints_state': ROSWaypointsState(current_waypoint=waypoints[0])
    }
    
    output = dynamics(**far_state_kwargs)
    print(f"Large error test: velocity={output.velocity:.3f}, yaw_rate={output.yaw_rate:.3f}")
    
    # Test 2: Very close to waypoint
    print("\n--- Test 2: Close to Waypoint ---")
    close_agent = ROSAgentState()
    close_agent.pose = Pose(
        position=Point(x=29.9, y=100.1, z=0.0),
        orientation=create_quaternion_from_yaw(0.1)
    )
    close_agent.velocity = 20.0
    
    close_state_kwargs = {
        'agent_state': close_agent,
        'waypoints_state': ROSWaypointsState(current_waypoint=waypoints[0])
    }
    
    output = dynamics(**close_state_kwargs)
    print(f"Close to waypoint test: velocity={output.velocity:.3f}, yaw_rate={output.yaw_rate:.3f}")
    
    # Test 3: High speed approach
    print("\n--- Test 3: High Speed Approach ---")
    fast_agent = ROSAgentState()
    fast_agent.pose = Pose(
        position=Point(x=25.0, y=95.0, z=0.0),
        orientation=create_quaternion_from_yaw(0.5)
    )
    fast_agent.velocity = 35.0  # Above max velocity
    
    fast_state_kwargs = {
        'agent_state': fast_agent,
        'waypoints_state': ROSWaypointsState(current_waypoint=waypoints[0])
    }
    
    output = dynamics(**fast_state_kwargs)
    print(f"High speed test: velocity={output.velocity:.3f}, yaw_rate={output.yaw_rate:.3f}")
    
    print("\n=== Test Complete ===")
    print(f"Final vehicle position: ({vehicle_x:.2f}, {vehicle_y:.2f})")
    print(f"Final waypoint: ({waypoints[current_waypoint_idx].position.x:.2f}, {waypoints[current_waypoint_idx].position.y:.2f})")
    print(f"Final distance to waypoint: {distance_to_wp:.2f}m")