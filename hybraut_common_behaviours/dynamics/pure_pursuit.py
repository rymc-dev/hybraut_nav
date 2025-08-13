# from hybraut_aci_interfaces import DynamicsInterface, IOSpec
# from hybraut_aci_interfaces._dynamics_interface import DynamicsSpecBuilder
# from colav_interfaces.msg import (
#     AgentState as ROSAgentState,
#     WaypointsState as ROSWaypointsState,
#     Waypoint as ROSWaypoint
# )
# import math
# from typing import Tuple
# import numpy as np

# def quaternion_to_heading(qx, qy, qz, qw) -> float:
#     """Convert quaternion to heading angle in radians."""
#     # Yaw (Z-axis rotation)
#     siny_cosp = 2.0 * (qw * qz + qx * qy)
#     cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
#     return math.atan2(siny_cosp, cosy_cosp)

# class PurePursuitController(DynamicsInterface):
#     """
#     Pure Pursuit controller for path following.
    
#     Features:
#     - Classic pure pursuit algorithm
#     - Lookahead distance adaptation
#     - Velocity control based on curvature
#     - Smooth steering transitions
#     """
    
#     _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

#     _init_input_spec = [
#         IOSpec.create_io_spec(name='base_lookahead_distance', type=float),
#         IOSpec.create_io_spec(name='lookahead_velocity_factor', type=float),
#         IOSpec.create_io_spec(name='min_lookahead_distance', type=float),
#         IOSpec.create_io_spec(name='max_lookahead_distance', type=float),
#         IOSpec.create_io_spec(name='wheelbase', type=float),
#         IOSpec.create_io_spec(name='max_velocity', type=float),
#         IOSpec.create_io_spec(name='min_velocity', type=float),
#         IOSpec.create_io_spec(name='curvature_velocity_factor', type=float),
#         IOSpec.create_io_spec(name='max_yaw_rate', type=float),
#         IOSpec.create_io_spec(name='steering_smoothing_factor', type=float),
#     ]

#     _state_input_spec = [
#         IOSpec.create_io_spec(name='agent_state', type=ROSAgentState),
#         IOSpec.create_io_spec(name='waypoints_state', type=ROSWaypointsState)
#     ]

#     def __init__(self, **init_kwargs):
#         super().__init__(**init_kwargs)
#         self._prev_steering_angle = 0.0
#         self._prev_yaw_rate = 0.0

#     def _validate_initialization(self, **init_kwargs):
#         super()._validate_initialization(**init_kwargs)
        
#         if init_kwargs['min_lookahead_distance'] >= init_kwargs['max_lookahead_distance']:
#             raise ValueError("min_lookahead_distance must be less than max_lookahead_distance")
        
#         if init_kwargs['min_velocity'] >= init_kwargs['max_velocity']:
#             raise ValueError("min_velocity must be less than max_velocity")

#     def _calculate_lookahead_distance(self, velocity: float) -> float:
#         """Calculate adaptive lookahead distance based on velocity."""
#         base_distance = self.__getattribute__('base_lookahead_distance')
#         velocity_factor = self.__getattribute__('lookahead_velocity_factor')
#         min_distance = self.__getattribute__('min_lookahead_distance')
#         max_distance = self.__getattribute__('max_lookahead_distance')
        
#         adaptive_distance = base_distance + velocity * velocity_factor
#         return max(min_distance, min(adaptive_distance, max_distance))

#     def _find_lookahead_point(self, agent_state: ROSAgentState, waypoint: ROSWaypoint, 
#                             lookahead_distance: float) -> Tuple[float, float]:
#         """Find the lookahead point for pure pursuit."""
#         # Current position
#         current_x = agent_state.pose.position.x
#         current_y = agent_state.pose.position.y
        
#         # Target position
#         target_x = waypoint.position.x
#         target_y = waypoint.position.y
        
#         # Vector from current to target
#         dx = target_x - current_x
#         dy = target_y - current_y
#         distance_to_target = math.sqrt(dx * dx + dy * dy)
        
#         # If target is within lookahead distance, use target
#         if distance_to_target <= lookahead_distance:
#             return target_x, target_y
        
#         # Otherwise, find point at lookahead distance along the line
#         unit_x = dx / distance_to_target
#         unit_y = dy / distance_to_target
        
#         lookahead_x = current_x + unit_x * lookahead_distance
#         lookahead_y = current_y + unit_y * lookahead_distance
        
#         return lookahead_x, lookahead_y

#     def _calculate_curvature(self, agent_state: ROSAgentState, 
#                            lookahead_point: Tuple[float, float]) -> float:
#         """Calculate curvature for pure pursuit steering."""
#         current_x = agent_state.pose.position.x
#         current_y = agent_state.pose.position.y
#         current_heading = quaternion_to_heading(
#             agent_state.pose.orientation.x,
#             agent_state.pose.orientation.y,
#             agent_state.pose.orientation.z,
#             agent_state.pose.orientation.w
#         )
        
#         # Transform lookahead point to vehicle frame
#         dx = lookahead_point[0] - current_x
#         dy = lookahead_point[1] - current_y
        
#         # Rotate to vehicle frame
#         cos_theta = math.cos(-current_heading)
#         sin_theta = math.sin(-current_heading)
        
#         local_x = dx * cos_theta - dy * sin_theta
#         local_y = dx * sin_theta + dy * cos_theta
        
#         # Calculate curvature
#         lookahead_distance = math.sqrt(local_x * local_x + local_y * local_y)
#         if lookahead_distance < 0.1:  # Avoid division by zero
#             return 0.0
        
#         curvature = 2.0 * local_y / (lookahead_distance * lookahead_distance)
#         return curvature

#     def _evaluate(self, **state_kwargs):
#         """Pure pursuit evaluation logic."""
#         agent_state: ROSAgentState = state_kwargs.get('agent_state')
#         waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        
#         current_velocity = agent_state.velocity
#         lookahead_distance = self._calculate_lookahead_distance(current_velocity)
        
#         # Find lookahead point
#         lookahead_point = self._find_lookahead_point(
#             agent_state, waypoints_state.current_waypoint, lookahead_distance
#         )
        
#         # Calculate curvature
#         curvature = self._calculate_curvature(agent_state, lookahead_point)
        
#         # Calculate steering angle using bicycle model
#         wheelbase = self.__getattribute__('wheelbase')
#         steering_angle = math.atan(wheelbase * curvature)
        
#         # Smooth steering transitions
#         smoothing_factor = self.__getattribute__('steering_smoothing_factor')
#         steering_angle = (smoothing_factor * steering_angle + 
#                          (1 - smoothing_factor) * self._prev_steering_angle)
#         self._prev_steering_angle = steering_angle
        
#         # Convert to yaw rate
#         if current_velocity > 0.1:
#             yaw_rate = current_velocity * math.tan(steering_angle) / wheelbase
#         else:
#             yaw_rate = 0.0
        
#         # Apply yaw rate limits
#         max_yaw_rate = self.__getattribute__('max_yaw_rate')
#         yaw_rate = max(-max_yaw_rate, min(yaw_rate, max_yaw_rate))
        
#         # Smooth yaw rate
#         yaw_rate = (smoothing_factor * yaw_rate + 
#                    (1 - smoothing_factor) * self._prev_yaw_rate)
#         self._prev_yaw_rate = yaw_rate
        
#         # Velocity control based on curvature
#         curvature_factor = self.__getattribute__('curvature_velocity_factor')
#         max_velocity = self.__getattribute__('max_velocity')
#         min_velocity = self.__getattribute__('min_velocity')
        
#         # Reduce velocity for sharp turns
#         curvature_velocity_reduction = abs(curvature) * curvature_factor
#         target_velocity = max_velocity * (1.0 - curvature_velocity_reduction)
#         target_velocity = max(min_velocity, min(target_velocity, max_velocity))
        
#         return self.create_output(
#             velocity=target_velocity,
#             yaw_rate=yaw_rate
#         )
    
# from types import SimpleNamespace

# class MockPose:
#     def __init__(self, x, y, yaw):
#         self.position = SimpleNamespace(x=x, y=y)
#         # Assuming quaternion (0, 0, sin(yaw/2), cos(yaw/2)) for 2D planar yaw
#         self.orientation = SimpleNamespace(
#             x=0.0,
#             y=0.0,
#             z=np.sin(yaw / 2),
#             w=np.cos(yaw / 2)
#         )

# class MockAgentState:
#     def __init__(self, x, y, yaw, velocity):
#         self.pose = MockPose(x, y, yaw)
#         self.velocity = velocity

# class MockWaypoint:
#     def __init__(self, x, y):
#         self.position = SimpleNamespace(x=x, y=y)

# class MockWaypointsState:
#     def __init__(self, waypoint):
#         self.current_waypoint = waypoint

# def main():
#     # Define initialization parameters
#     init_params = {
#         'base_lookahead_distance': 2.0,
#         'lookahead_velocity_factor': 0.5,
#         'min_lookahead_distance': 1.0,
#         'max_lookahead_distance': 10.0,
#         'wheelbase': 2.0,
#         'max_velocity': 3.0,
#         'min_velocity': 0.0,
#         'curvature_velocity_factor': 1.0,
#         'max_yaw_rate': 0.5,
#         'steering_smoothing_factor': 0.2
#     }

#     # Instantiate controller
#     controller = PurePursuitController(**init_params)

#     # Mock current agent state
#     agent_state = MockAgentState(x=0.0, y=0.0, yaw=0.0, velocity=1.0)

#     # Mock current waypoint state
#     waypoint = MockWaypoint(x=10.0, y=5.0)
#     waypoints_state = MockWaypointsState(waypoint)

#     # Evaluate control command
#     output = controller._evaluate(agent_state=agent_state, waypoints_state=waypoints_state)

#     print("=== MPC Output ===")
#     # print(f"Velocity command: {output['velocity']:.2f}")
#     print(f"Yaw rate command: {output}")

# if __name__ == '__main__':
#     main()