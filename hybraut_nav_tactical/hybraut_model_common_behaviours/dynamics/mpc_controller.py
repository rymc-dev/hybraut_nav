# from hybraut_aci_interfaces import DynamicsInterface, IOSpec
# from hybraut_aci_interfaces._dynamics_interface import DynamicsSpecBuilder
# from colav_interfaces.msg import (
#     AgentState as ROSAgentState,
#     WaypointsState as ROSWaypointsState,
#     Waypoint as ROSWaypoint
# )
# import math
# from collections import deque
# import numpy as np

# def quaternion_to_heading(qx, qy, qz, qw) -> float:
#     """Convert quaternion to heading angle in radians."""
#     # Yaw (Z-axis rotation)
#     siny_cosp = 2.0 * (qw * qz + qx * qy)
#     cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
#     return math.atan2(siny_cosp, cosy_cosp)

# class ModelPredictiveController(DynamicsInterface):
#     """
#     Model Predictive Controller (MPC) for trajectory following.
    
#     Features:
#     - Predictive control over finite horizon
#     - Quadratic cost function optimization
#     - Constraint handling
#     - Velocity and steering rate limits
#     """
    
#     _dynamic_output_spec = DynamicsSpecBuilder.create_automaton_control_outputs()

#     _init_input_spec = [
#         IOSpec.create_io_spec(name='prediction_horizon', type=int),
#         IOSpec.create_io_spec(name='control_horizon', type=int),
#         IOSpec.create_io_spec(name='dt_prediction', type=float),
#         IOSpec.create_io_spec(name='position_weight', type=float),
#         IOSpec.create_io_spec(name='heading_weight', type=float),
#         IOSpec.create_io_spec(name='velocity_weight', type=float),
#         IOSpec.create_io_spec(name='control_weight', type=float),
#         IOSpec.create_io_spec(name='control_rate_weight', type=float),
#         IOSpec.create_io_spec(name='max_velocity', type=float),
#         IOSpec.create_io_spec(name='max_yaw_rate', type=float),
#         IOSpec.create_io_spec(name='target_velocity', type=float),
#         IOSpec.create_io_spec(name='wheelbase', type=float),
#     ]

#     _state_input_spec = [
#         IOSpec.create_io_spec(name='agent_state', type=ROSAgentState),
#         IOSpec.create_io_spec(name='waypoints_state', type=ROSWaypointsState)
#     ]

#     def __init__(self, **init_kwargs):
#         super().__init__(**init_kwargs)
#         self._prev_controls = np.zeros(2)  # [velocity, yaw_rate]
#         self._control_sequence = deque(maxlen=self.__getattribute__('control_horizon'))

#     def _validate_initialization(self, **init_kwargs):
#         super()._validate_initialization(**init_kwargs)
        
#         if init_kwargs['control_horizon'] > init_kwargs['prediction_horizon']:
#             raise ValueError("control_horizon must be <= prediction_horizon")

#     def _predict_state(self, current_state: np.ndarray, control: np.ndarray, 
#                       dt: float) -> np.ndarray:
#         """Predict next state using bicycle model."""
#         x, y, theta, v = current_state
#         velocity_cmd, yaw_rate = control
        
#         # Simple first-order velocity dynamics
#         v_next = v + (velocity_cmd - v) * dt / 0.5  # time constant = 0.5s
        
#         # Update position and heading
#         x_next = x + v * math.cos(theta) * dt
#         y_next = y + v * math.sin(theta) * dt
#         theta_next = theta + yaw_rate * dt
        
#         return np.array([x_next, y_next, theta_next, v_next])

#     def _calculate_cost(self, predicted_states: np.ndarray, controls: np.ndarray,
#                        target_state: np.ndarray) -> float:
#         """Calculate quadratic cost function."""
#         horizon = predicted_states.shape[0]
#         total_cost = 0.0
        
#         # Weights
#         pos_weight = self.__getattribute__('position_weight')
#         heading_weight = self.__getattribute__('heading_weight')
#         vel_weight = self.__getattribute__('velocity_weight')
#         control_weight = self.__getattribute__('control_weight')
#         control_rate_weight = self.__getattribute__('control_rate_weight')
        
#         # State tracking costs
#         for i in range(horizon):
#             state_error = predicted_states[i] - target_state
            
#             # Position cost
#             pos_cost = pos_weight * (state_error[0]**2 + state_error[1]**2)
            
#             # Heading cost (wrapped)
#             heading_error = math.atan2(
#                 math.sin(state_error[2]),
#                 math.cos(state_error[2])
#             )
#             heading_cost = heading_weight * heading_error**2
            
#             # Velocity cost
#             vel_cost = vel_weight * state_error[3]**2
            
#             total_cost += pos_cost + heading_cost + vel_cost
        
#         # Control effort costs
#         for i in range(len(controls)):
#             control_cost = control_weight * np.sum(controls[i]**2)
#             total_cost += control_cost
            
#             # Control rate cost
#             if i > 0:
#                 control_rate_cost = control_rate_weight * np.sum(
#                     (controls[i] - controls[i-1])**2
#                 )
#                 total_cost += control_rate_cost
        
#         return total_cost

#     def _optimize_controls(self, current_state: np.ndarray, 
#                           target_state: np.ndarray) -> np.ndarray:
#         """Simple grid search optimization (replace with proper optimizer in practice)."""
#         best_cost = float('inf')
#         best_controls = None
        
#         horizon = self.__getattribute__('control_horizon')
#         dt = self.__getattribute__('dt_prediction')
#         max_velocity = self.__getattribute__('max_velocity')
#         max_yaw_rate = self.__getattribute__('max_yaw_rate')
        
#         # Grid search parameters (coarse for demo)
#         velocity_samples = np.linspace(0.0, max_velocity, 5)
#         yaw_rate_samples = np.linspace(-max_yaw_rate, max_yaw_rate, 7)
        
#         for vel in velocity_samples:
#             for yaw_rate in yaw_rate_samples:
#                 # Simple constant control sequence
#                 controls = np.array([[vel, yaw_rate]] * horizon)
                
#                 # Predict trajectory
#                 predicted_states = []
#                 state = current_state.copy()
                
#                 for i in range(horizon):
#                     state = self._predict_state(state, controls[i], dt)
#                     predicted_states.append(state.copy())
                
#                 predicted_states = np.array(predicted_states)
                
#                 # Calculate cost
#                 cost = self._calculate_cost(predicted_states, controls, target_state)
                
#                 if cost < best_cost:
#                     best_cost = cost
#                     best_controls = controls
        
#         return best_controls[0] if best_controls is not None else np.zeros(2)

#     def _evaluate(self, **state_kwargs):
#         """MPC evaluation logic."""
#         agent_state: ROSAgentState = state_kwargs.get('agent_state')
#         waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        
#         # Current state [x, y, theta, v]
#         current_state = np.array([
#             agent_state.pose.position.x,
#             agent_state.pose.position.y,
#             quaternion_to_heading(
#                 agent_state.pose.orientation.x,
#                 agent_state.pose.orientation.y,
#                 agent_state.pose.orientation.z,
#                 agent_state.pose.orientation.w
#             ),
#             agent_state.velocity
#         ])
        
#         # Target state
#         target_velocity = self.__getattribute__('target_velocity')
#         target_heading = math.atan2(
#             waypoints_state.current_waypoint.position.y - current_state[1],
#             waypoints_state.current_waypoint.position.x - current_state[0]
#         )
        
#         target_state = np.array([
#             waypoints_state.current_waypoint.position.x,
#             waypoints_state.current_waypoint.position.y,
#             target_heading,
#             target_velocity
#         ])
        
#         # Optimize control sequence
#         optimal_control = self._optimize_controls(current_state, target_state)
        
#         # Apply first control in sequence
#         velocity_cmd = optimal_control[0]
#         yaw_rate_cmd = optimal_control[1]
        
#         # Store for next iteration
#         self._prev_controls = optimal_control
        
#         return self.create_output(
#             velocity=velocity_cmd,
#             yaw_rate=yaw_rate_cmd
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
#         'prediction_horizon': 10,
#         'control_horizon': 5,
#         'dt_prediction': 0.2,
#         'position_weight': 1.0,
#         'heading_weight': 0.5,
#         'velocity_weight': 0.1,
#         'control_weight': 0.01,
#         'control_rate_weight': 0.01,
#         'max_velocity': 3.0,
#         'max_yaw_rate': 0.5,
#         'target_velocity': 2.0,
#         'wheelbase': 2.0
#     }

#     # Instantiate controller
#     controller = ModelPredictiveController(**init_params)

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

# if __name__ == "__main__":
#     main()