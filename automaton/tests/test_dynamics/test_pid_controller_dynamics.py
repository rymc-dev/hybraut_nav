"""
Test class for PIDControllerDynamics an implementation of the Abstract Dynamics ABC for COLAV hybrid automaton control modes cruise and t2los control modes.

In this class we utilize PIDControllerDynamics to test 
the underlying functionalities for this abstract class to enusre it is working 
as expected through the lifecycle of build and runtime
"""


import pytest
import math
from automaton.dynamics import PIDControllerDynamics, DynamicsABC
from colav_interfaces.msg import AgentState as ROSAgentState, WaypointsState as ROSWaypointsState, Waypoint as ROSWaypoint
from geometry_msgs.msg import Point
import numpy as np

@pytest.fixture
def default_init_kwargs():
    return  {
        'control_frequency': 100,
        'target_velocity': 25.0,
        'error_tolerance': 0.3,
        'max_velocity': 30.0,
        'max_yaw_rate': 1.0,
        'yaw_kp': 2.0,
        'yaw_ki': 0.05,  # Reduced
        'yaw_kd': 0.1,   # Reduced
        'vel_kp': 2.0,   # Increased for faster response
        'vel_ki': 0.01,  # Much lower to avoid oscillation
        'vel_kd': 0.0,   # Remove derivative term initially
        'integral_max': 5.0,  # Lower limit
        'derivative_filter_alpha': 0.1,
    }

@pytest.fixture
def far_waypoint():
    wp = ROSWaypoint()
    wp.position = Point(x=100.0, y=0.0, z=0.0)
    return wp

@pytest.fixture
def dynamics(default_init_kwargs):
    return PIDControllerDynamics(**default_init_kwargs)

@pytest.fixture
def state_kwargs(far_waypoint):
    agent = ROSAgentState()
    agent.velocity = 0.0
    waypoints = ROSWaypointsState()
    waypoints.current_waypoint = far_waypoint
    return {'agent_state': agent, 'waypoints_state': waypoints}

class TestPIDControllerDynamics():
    """test suite for PIDControllerDynamics"""

    def test_initialization_and_specs(self, dynamics):
        """test the dynamic class instance initializes correctly with proper specs"""
        assert dynamics.init_input_spec_names() == [
            'control_frequency',
            'target_velocity',
            'error_tolerance',
            'max_velocity',
            'max_yaw_rate',
            'yaw_kp',
            'yaw_ki',
            'yaw_kd',
            'vel_kp',
            'vel_ki',
            'vel_kd',
            'integral_max',
            'derivative_filter_alpha'
        ]
        assert dynamics.init_input_spec_types() == [
            int,
            float, 
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float,
            float
        ]

        assert dynamics.state_input_spec_names() == ['agent_state', 'waypoints_state']
        assert dynamics.state_input_spec_types() == [ROSAgentState, ROSWaypointsState]

        assert dynamics.dynamic_output_spec_name() == "AutomatonControlOutputs"
        assert dynamics.dynamic_output_spec_description() == "outputs for automaton spec"
        assert dynamics.dynamic_output_spec_names() == ['velocity', 'yaw_rate']
        assert dynamics.dynamic_output_spec_types()== [float, float]
        assert dynamics.dynamic_output_spec_units() == ['m/s', 'rad/s']

    def test_string_representations(self, dynamics):
        """Test string representation methods"""
        assert repr(dynamics) == 'PIDControllerDynamics(output_type=AutomatonControlOutputs, initialized=True)'
        assert str(dynamics) == 'Dynamics Function: PIDControllerDynamics (Output: AutomatonControlOutputs)'

    def test_comprehensive_velocity_and_yaw(self, dynamics, state_kwargs):
        """Test PID controller behavior with realistic expectations for control systems."""
        velocities = []
        yaw_rates = []
    
        # Run the controller for stabilization + evaluation
        total_iterations = 100  # Reduced from 1000 - too many iterations with sleep
        stabilization_iterations = 20  # Increased stabilization period
    
        for i in range(total_iterations):
            out = dynamics.__call__(**state_kwargs)
            velocities.append(out.velocity)
            yaw_rates.append(out.yaw_rate)
            
            # Update state for next iteration
            state_kwargs['agent_state'].velocity = out.velocity
            
            # Remove or reduce sleep - makes tests slow and doesn't add value
            # time.sleep(0.01)  # Consider removing this entirely
    
        # Basic sanity checks
        assert len(velocities) == total_iterations
        assert len(yaw_rates) == total_iterations
        
        # Velocity should start positive (assuming forward motion)
        assert velocities[0] > 0.0
    
        # Only evaluate stability after initial stabilization period
        stable_velocities = velocities[stabilization_iterations:]
        stable_yaw_rates = yaw_rates[stabilization_iterations:]
    
        # PID controllers oscillate - check for reasonable bounds instead of monotonic increase
        velocity_range = max(stable_velocities) - min(stable_velocities)
        velocity_mean = np.mean(stable_velocities)
        
        # Velocity should be bounded and not wildly oscillating
        # Allow for some oscillation but not excessive
        max_reasonable_oscillation = velocity_mean * 0.3  # 30% of mean velocity
        assert velocity_range <= max_reasonable_oscillation, f"Velocity oscillation too large: {velocity_range} > {max_reasonable_oscillation}"
    
        # Should not exceed max_velocity (check all velocities)
        assert all(v <= dynamics.max_velocity for v in velocities), "Velocity exceeded maximum"
        
        # Velocity should be positive (assuming forward motion)
        assert all(v > 0 for v in velocities), "Velocity should remain positive"
    
        # For straight-ahead motion, yaw_rate should be small (relaxed tolerance)
        max_yaw_rate = max(abs(y) for y in stable_yaw_rates)
        assert max_yaw_rate < 0.1, f"Yaw rate too large for straight motion: {max_yaw_rate}"
    
        # Convergence check - system should be settling toward target
        target_velocity = dynamics.target_velocity
        
        # Split stabilized data into early and late portions
        mid_point = len(stable_velocities) // 2
        early_stable = stable_velocities[:mid_point]
        late_stable = stable_velocities[mid_point:]
        
        if len(early_stable) > 0 and len(late_stable) > 0:
            early_avg_error = np.mean([abs(v - target_velocity) for v in early_stable])
            late_avg_error = np.mean([abs(v - target_velocity) for v in late_stable])
            
            # System should be converging or at least not diverging significantly
            # Allow for some tolerance since PID can have steady-state error
            assert late_avg_error <= early_avg_error * 1.1, "System appears to be diverging from target"
        
        # Optional: Check that final velocities are reasonably close to target
        final_velocities = velocities[-5:]  # Last 5 readings
        final_avg_error = np.mean([abs(v - target_velocity) for v in final_velocities])
        
        # Allow for reasonable steady-state error (e.g., 10% of target)
        max_acceptable_error = target_velocity * 0.1
        assert final_avg_error <= max_acceptable_error, f"Final error too large: {final_avg_error} > {max_acceptable_error}"
        
        # Additional stability check - variance should be reasonable
        stable_velocity_std = np.std(stable_velocities)
        max_acceptable_std = velocity_mean * 0.15  # 15% of mean
        assert stable_velocity_std <= max_acceptable_std, f"Velocity too unstable: std={stable_velocity_std} > {max_acceptable_std}"


    def test_pid_controller_basic_functionality(self, dynamics, state_kwargs):
        """Simplified test focusing on basic PID controller functionality."""
        
        # Run for fewer iterations to focus on core behavior
        outputs = []
        for i in range(50):
            out = dynamics.__call__(**state_kwargs)
            outputs.append(out)
            state_kwargs['agent_state'].velocity = out.velocity
        
        velocities = [out.velocity for out in outputs]
        yaw_rates = [out.yaw_rate for out in outputs]
        
        # Basic functionality checks
        assert all(isinstance(v, (int, float)) for v in velocities), "Velocities should be numeric"
        assert all(isinstance(y, (int, float)) for y in yaw_rates), "Yaw rates should be numeric"
        
        # Bounds checking
        assert all(0 <= v <= dynamics.max_velocity for v in velocities), "Velocity out of bounds"
        
        # Controller should produce reasonable outputs
        assert not all(v == velocities[0] for v in velocities), "Controller appears inactive"
        
        # For straight motion, yaw rates should be small
        assert all(abs(y) < 0.5 for y in yaw_rates), "Excessive yaw rate for straight motion"


    def test_pid_controller_convergence_trend(self, dynamics, state_kwargs):
        """Test that PID controller shows convergence trend over time."""
        
        target_velocity = dynamics.target_velocity
        errors = []
        
        # Run controller and track error over time
        for i in range(100):
            out = dynamics.__call__(**state_kwargs)
            error = abs(out.velocity - target_velocity)
            errors.append(error)
            state_kwargs['agent_state'].velocity = out.velocity
        
        # Check that error trend is generally decreasing
        # Use moving average to smooth out oscillations
        window_size = 10
        if len(errors) >= window_size * 2:
            early_avg = np.mean(errors[:window_size])
            late_avg = np.mean(errors[-window_size:])
            
            # Allow for some tolerance - PID might not achieve perfect convergence
            assert late_avg <= early_avg * 1.2, "No convergence trend detected"

    @pytest.mark.parametrize(
        "init_kwargs, exception",
        [
            ({}, KeyError),
            ({'target_velocity':10.0}, KeyError),
            ({'target_yaw_rate':0.1}, KeyError),
            ({'control_frequency':0, 'target_velocity':10.0, 'target_yaw_rate':0.1}, KeyError),
            ({'control_frequency':100, 'target_velocity':10.0, 'target_yaw_rate':0.1, 'max_velocity':-1.0}, KeyError),
            ({'control_frequency':100, 'target_velocity':10.0, 'target_yaw_rate':0.1, 'max_velocity':30.0, 'max_yaw_rate':1.0,
            'yaw_kp':1.0, 'yaw_ki':0.1, 'yaw_kd':0.1, 'vel_kp':0.5, 'vel_ki':0.05, 'vel_kd':0.01,
            'integral_max':5.0, 'derivative_filter_alpha':1.5}, KeyError),
        ],
        ids=[

        ]
    )
    def test_invalid_initialization(self, init_kwargs, exception):
        """
        Parameterized test for invalid initializations of the dynamic class.
        
        Each case checks if the class raises the expected exception type
        when initialized with incomplete or incorrect types in kwargs.
        """
        with pytest.raises(exception):
            PIDControllerDynamics(**init_kwargs)

    @pytest.mark.parametrize(
        "state_kwargs_input, exception",
        [
            ({}, KeyError),
            ({'agent_state': ROSAgentState()}, KeyError),
            ({'waypoints_state': ROSWaypointsState()}, KeyError),
            ({'agent_state': 'invalid', 'waypoints_state': ROSWaypointsState()}, TypeError),
            ({'agent_state': ROSAgentState(), 'waypoints_state': 'invalid'}, TypeError),
        ],
        ids=[

        ]
    )
    def test_invalid_state_inputs(self, dynamics, state_kwargs_input, exception, far_waypoint):
        """
        Parameterized test for invalid runtime state inputs to the dynamic class.
        
        Each test provides an invalid or incomplete state input dictionary,
        and checks whether the `__call__` method raises the appropriate exception.
        """
        with pytest.raises(exception):
            # ensure current_waypoint exists if waypoints_state is correct type
            if isinstance(state_kwargs_input.get('waypoints_state'), ROSWaypointsState):
                state_kwargs_input['waypoints_state'].current_waypoint = far_waypoint
            dynamics.__call__(**state_kwargs_input)


    def test_reset_and_diagnostics(self, dynamics, state_kwargs):
        # call once to populate state
        dynamics.__call__(**state_kwargs)
        diag_before = dynamics.get_pid_diagnostics().copy()
        assert diag_before['velocity_history_length'] > 0

        # reset
        dynamics.reset_pid_state()
        diag_after = dynamics.get_pid_diagnostics()
        assert diag_after['velocity_history_length'] == 0
        assert diag_after['heading_error_history_length'] == 0
        # avg_dt reset to initial dt
        assert math.isclose(diag_after['avg_dt'], 1.0/dynamics.control_frequency, rel_tol=1e-3)

if __name__ == '__main__':
    pytest.main([__file__])