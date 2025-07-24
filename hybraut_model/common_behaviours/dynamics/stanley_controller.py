from automaton_models.hybraut_model.aci_interfaces.dynamics_interface import DynamicsInterface
from automaton_models.hybraut_model.aci_interfaces.dynamics_interface import DynamicsSpecBuilder
from automaton.spec import IOSpec
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
import math

def quaternion_to_heading(qx, qy, qz, qw) -> float:
    """Convert quaternion to heading angle in radians."""
    # Yaw (Z-axis rotation)
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)

class StanleyController(DynamicsInterface):
    """
    Stanley controller for path following.
    
    Features:
    - Cross-track error correction
    - Heading error correction
    - Velocity-dependent gain scaling
    - Smooth control outputs
    """
    
    _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

    _init_input_spec = [
        IOSpec.create_io_spec(name='cross_track_gain', type=float),
        IOSpec.create_io_spec(name='heading_gain', type=float),
        IOSpec.create_io_spec(name='velocity_gain', type=float),
        IOSpec.create_io_spec(name='max_cross_track_error', type=float),
        IOSpec.create_io_spec(name='target_velocity', type=float),
        IOSpec.create_io_spec(name='max_velocity', type=float),
        IOSpec.create_io_spec(name='max_yaw_rate', type=float),
        IOSpec.create_io_spec(name='wheelbase', type=float),
        IOSpec.create_io_spec(name='output_smoothing_factor', type=float),
    ]

    _state_input_spec = [
        IOSpec.create_io_spec(name='agent_state', type=ROSAgentState),
        IOSpec.create_io_spec(name='waypoints_state', type=ROSWaypointsState)
    ]

    def __init__(self, **init_kwargs):
        super().__init__(**init_kwargs)
        self._prev_steering_angle = 0.0

    def _calculate_cross_track_error(self, agent_state: ROSAgentState, 
                                   waypoint: ROSWaypoint) -> float:
        """Calculate cross-track error (perpendicular distance to path)."""
        # Current position
        current_x = agent_state.pose.position.x
        current_y = agent_state.pose.position.y
        
        # Target position (simplified as point target)
        target_x = waypoint.position.x
        target_y = waypoint.position.y
        
        # Current heading
        current_heading = quaternion_to_heading(
            agent_state.pose.orientation.x,
            agent_state.pose.orientation.y,
            agent_state.pose.orientation.z,
            agent_state.pose.orientation.w
        )
        
        # Calculate path direction (assuming straight line to target)
        dx = target_x - current_x
        dy = target_y - current_y
        path_heading = math.atan2(dy, dx)
        
        # Calculate cross-track error
        distance_to_target = math.sqrt(dx * dx + dy * dy)
        heading_error = path_heading - current_heading
        
        # Cross-track error (positive = left of path)
        cross_track_error = distance_to_target * math.sin(heading_error)
        
        return cross_track_error

    def _calculate_heading_error(self, agent_state: ROSAgentState, 
                               waypoint: ROSWaypoint) -> float:
        """Calculate heading error relative to desired path."""
        current_x = agent_state.pose.position.x
        current_y = agent_state.pose.position.y
        target_x = waypoint.position.x
        target_y = waypoint.position.y
        
        # Desired heading
        desired_heading = math.atan2(target_y - current_y, target_x - current_x)
        
        # Current heading
        current_heading = quaternion_to_heading(
            agent_state.pose.orientation.x,
            agent_state.pose.orientation.y,
            agent_state.pose.orientation.z,
            agent_state.pose.orientation.w
        )
        
        # Heading error with angle wrapping
        heading_error = math.atan2(
            math.sin(desired_heading - current_heading),
            math.cos(desired_heading - current_heading)
        )
        
        return heading_error

    def _evaluate(self, **state_kwargs):
        """Stanley controller evaluation logic."""
        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        
        current_velocity = agent_state.velocity
        
        # Calculate errors
        cross_track_error = self._calculate_cross_track_error(
            agent_state, waypoints_state.current_waypoint
        )
        heading_error = self._calculate_heading_error(
            agent_state, waypoints_state.current_waypoint
        )
        
        # Limit cross-track error
        max_cross_track_error = self.__getattribute__('max_cross_track_error')
        cross_track_error = max(-max_cross_track_error, 
                               min(cross_track_error, max_cross_track_error))
        
        # Stanley control law
        cross_track_gain = self.__getattribute__('cross_track_gain')
        heading_gain = self.__getattribute__('heading_gain')
        velocity_gain = self.__getattribute__('velocity_gain')
        
        # Cross-track term (velocity-dependent)
        if current_velocity > 0.1:
            cross_track_term = math.atan(cross_track_gain * cross_track_error / 
                                       (velocity_gain + current_velocity))
        else:
            cross_track_term = math.atan(cross_track_gain * cross_track_error / velocity_gain)
        
        # Heading term
        heading_term = heading_gain * heading_error
        
        # Combined steering angle
        steering_angle = heading_term + cross_track_term
        
        # Smooth steering output
        smoothing_factor = self.__getattribute__('output_smoothing_factor')
        steering_angle = (smoothing_factor * steering_angle + 
                         (1 - smoothing_factor) * self._prev_steering_angle)
        self._prev_steering_angle = steering_angle
        
        # Convert to yaw rate
        wheelbase = self.__getattribute__('wheelbase')
        if current_velocity > 0.1:
            yaw_rate = current_velocity * math.tan(steering_angle) / wheelbase
        else:
            yaw_rate = 0.0
        
        # Apply yaw rate limits
        max_yaw_rate = self.__getattribute__('max_yaw_rate')
        yaw_rate = max(-max_yaw_rate, min(yaw_rate, max_yaw_rate))
        
        # Velocity control
        target_velocity = self.__getattribute__('target_velocity')
        max_velocity = self.__getattribute__('max_velocity')
        
        # Reduce velocity for large steering angles
        steering_velocity_reduction = abs(steering_angle) * 0.5
        final_velocity = target_velocity * (1.0 - steering_velocity_reduction)
        final_velocity = max(0.0, min(final_velocity, max_velocity))
        
        return self.create_output(
            velocity=final_velocity,
            yaw_rate=yaw_rate
        )


from types import SimpleNamespace
import numpy as np

class MockPose:
    def __init__(self, x, y, yaw):
        self.position = SimpleNamespace(x=x, y=y)
        # Assuming quaternion (0, 0, sin(yaw/2), cos(yaw/2)) for 2D planar yaw
        self.orientation = SimpleNamespace(
            x=0.0,
            y=0.0,
            z=np.sin(yaw / 2),
            w=np.cos(yaw / 2)
        )

class MockAgentState:
    def __init__(self, x, y, yaw, velocity):
        self.pose = MockPose(x, y, yaw)
        self.velocity = velocity

class MockWaypoint:
    def __init__(self, x, y):
        self.position = SimpleNamespace(x=x, y=y)

class MockWaypointsState:
    def __init__(self, waypoint):
        self.current_waypoint = waypoint

def main():
    # Define initialization parameters
    init_params = {
        'cross_track_gain': 1.5,
        'heading_gain': 1.0,
        'velocity_gain': 0.8,
        'max_cross_track_error': 2.0,
        'target_velocity': 2.0,
        'max_velocity': 3.0,
        'max_yaw_rate': 0.5,
        'wheelbase': 2.0,
        'output_smoothing_factor': 0.2
    }

    # Instantiate controller
    controller = StanleyController(**init_params)

    # Mock current agent state
    agent_state = MockAgentState(x=0.0, y=0.0, yaw=0.0, velocity=1.0)

    # Mock current waypoint state
    waypoint = MockWaypoint(x=10.0, y=5.0)
    waypoints_state = MockWaypointsState(waypoint)

    # Evaluate control command
    output = controller._evaluate(agent_state=agent_state, waypoints_state=waypoints_state)

    print("=== MPC Output ===")
    # print(f"Velocity command: {output['velocity']:.2f}")
    print(f"Yaw rate command: {output}")

if __name__ == '__main__':
    main()