# !/usr/bin/env python3
""" 
Tactical Node for HybrautNav Navigation Stack is the second layer 
responsible for tactical decision-making in navigation tasks.
"""

import rclpy
from rclpy.lifecycle import State, TransitionCallbackReturn, Node

from rclpy.lifecycle import Node

from colav_automaton import ColavAutomaton
from hybrid_automaton import Automaton
from hybrid_automaton_runner import AutomatonRunner
import asyncio
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult, ParameterType
import threading

import numpy as np

class TacticalNode(Node):
    
    
    def __init__(self, node_name:str='tactical_node', namespace:str='hybraut_nav',**kwargs) -> None:
        super().__init__(node_name, namespace=namespace, **kwargs)
        # parameters
        

        
        # initialize the subscriber/publishers
        
        self._automaton: Automaton = None
        self._runner: AutomatonRunner = None
        self._runner_thread: threading.Thread = None
        
        self._x = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        self._aux_x = {
            'waypoints': [np.array([100.0, 100.0])],
            'unsafe_region': []
        }
        
        
        self._unconfigured_params_state = False
        self._inactive_params_state = False
        
        self._toggle_unconfigured_params_state()

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'")
        
        try: 
            self._automaton = ColavAutomaton(
                heading_tolerance=self.get_parameter('heading_tolerance').value,
                k_theta=self.get_parameter('k_theta').value,
                k_v=self.get_parameter('k_v').value,
                constant_velocity=self.get_parameter('constant_velocity').value,
                acceptance_radius=self.get_parameter('acceptance_radius').value,
                los_distance_threshold=self.get_parameter('los_distance_threshold').value,
                longitudinal_offset_distance=self.get_parameter('longitudinal_offset_distance').value,
                lateral_offset_distance=self.get_parameter('lateral_offset_distance').value
            ) 
            self._toggle_unconfigured_params_state()
            self._toggle_inactive_params_state()
        except Exception as e: 
            raise Exception(f"{str(e)}")
        
        
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")
        
        try: 
            self._runner: AutomatonRunner = AutomatonRunner(
                hybrid_automaton=self._automaton,
                sampling_rate=0.01
            )
            dt = self.get_parameter('dt').value
            injector_update_rate = self.get_parameter('sensor_update_rate').value
            self._runner_thread = threading.Thread(
                target=lambda: self._runner_thread_fn(dt, injector_update_rate),
                daemon=True
            )
            self._runner_thread.start()
            self._toggle_inactive_params_state()
        except Exception as e:
            raise SystemError(f"{str(e)}")
    
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info("Stopping runner thread...")

        try:
            # Tell the runner to stop gracefully
            if self._runner:
                self._runner.stop()

            # Wait for thread to complete naturally (don't force stop the loop)
            if self._runner_thread and self._runner_thread.is_alive():
                self._runner_thread.join(timeout=5.0)  # Increased timeout for safety
                
                if self._runner_thread.is_alive():
                    self.get_logger().warning("Runner thread did not exit cleanly")

            # Now safe to get results
            if self._runner:
                results = self._runner.get_results()

                import matplotlib.pyplot as plt
                from hybrid_automaton_evaluation.figure_generator import (
                    continuous_states_over_time_fig, 
                    automaton_states_over_time
                )
                fig1 = continuous_states_over_time_fig(results['continuous_states'])
                fig2 = automaton_states_over_time(results['automaton_states'])
                plt.show()

        except Exception as e:
            self.get_logger().error(f"Error during deactivation: {str(e)}")
            raise SystemError(str(e))
        finally:
            # Clean up references
            self._runner = None
            self._runner_thread = None
            if hasattr(self, "_loop"):
                delattr(self, "_loop")

        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")
        
        try: 
            ... 
        except Exception as e:
            return TransitionCallbackReturn.FAILURE
        
        return TransitionCallbackReturn.SUCCESS
    
    
    """ asyncio runner"""
    def _runner_thread_fn(self, dt: float, injector_update_rate: float):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._runner.run(
                x0=self._x,
                aux_x0=self._aux_x,
                real_time_mode=True,
                integrate=True,
                dt=dt,
                collect_continuous=True,
                collect_automaton=True,
                collect_control=False,
                collect_transitions=True,
                injector_update_rate=injector_update_rate
            ))
        finally:
            self._loop.close()

    
    """ === parameters toggles === """
    
    def _toggle_unconfigured_params_state(self):
        """toggles ROS2 parameters available in unconfigured state"""
        try: 
            if not self._unconfigured_params_state:
                self.declare_parameter(
                    'heading_tolerance',
                    0.2,
                    ParameterDescriptor(
                        name='heading_tolerance',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='heading tolerance. '
                                'cfg for guards for colav_automaton '
                                f'(default: {0.2})'
                    )
                )
                self.declare_parameter(
                    'k_theta',
                    1.0,
                    ParameterDescriptor(
                        name='k_theta',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='k_thate. '
                                'k_theta, control gains for theta controllers.'
                                f'(default: {1.0})'
                    )
                )
                self.declare_parameter(
                    'k_v',
                    1.0,
                    ParameterDescriptor(
                        name='k_v',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='k_v. '
                                'control gains for velocity controllers. '
                                f'(default: {1.0})'
                    )
                )
                self.declare_parameter(
                    'constant_velocity',
                    2.0,
                    ParameterDescriptor(
                        name='constant_velocity',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='constant_velocity. '
                                'constant_velocity for colav_automaton'
                                f'(default: {2.0})'
                    )
                )
                self.declare_parameter(
                    'acceptance_radius',
                    20.0,
                    ParameterDescriptor(
                        name='acceptance_radius',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='acceptance_radius'
                                'acceptance radius for waypoint reached guards in colav_automaton.'
                                f'(default: {20.0})'
                    )
                )
                self.declare_parameter(
                    'los_distance_threshold',
                    200.0,
                    ParameterDescriptor(
                        name='los_distance_threshold',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='los_distance_threshold. '
                                'los_distance_threshold for colav_automaton guards.'
                                f'(default: {200.0})'
                    )
                )
                self.declare_parameter(
                    'longitudinal_offset_distance',
                    100.0,
                    ParameterDescriptor(
                        name='longitudinal_offset_distance',
                        type=ParameterType.PARAMETER_DOUBLE,
                        description='longitudinal_offset_distance. '
                                'longitudinal_offset_distance for resets for colav_automaton '
                                f'(default: {100.0})'
                    )
                )
                self.declare_parameter(
                    'lateral_offset_distance',
                    100.0,
                    ParameterDescriptor(
                        name='declare_parameter',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='lateral_offset_distance. '
                                'lateral_offset_distance for resets for colav_automaton '
                                f'(default: {0.2})'
                    )
                )
            else: 
                self.undeclare_parameter('heading_tolerance')
                self.undeclare_parameter('k_theta')
                self.undeclare_parameter('k_v')
                self.undeclare_parameter('constant_velocity')
                self.undeclare_parameter('acceptance_radius')
                self.undeclare_parameter('los_distance_threshold')
                self.undeclare_parameter('longitudinal_offset_distance')
                self.undeclare_parameter('lateral_offset_distance')
        except Exception as e: 
            raise SystemError(str(e))
        
        self._unconfigured_params_state = not(self._unconfigured_params_state)
        
    def _toggle_inactive_params_state(self):
        """toggles ROS2 parameters available in inactive state"""
        try: 
            if not self._inactive_params_state:
                self.declare_parameter(
                    'dt',
                    0.01,
                    ParameterDescriptor(
                        name='dt',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='dt. '
                                'delta time for evaluation steps. '
                                f'(default: {0.01})'
                    )
                )          
                self.declare_parameter(
                    'sensor_update_rate',
                    0.01,
                    ParameterDescriptor(
                        name='sensor_update_rate',
                        type=ParameterType.PARAMETER_DOUBLE, 
                        description='sensor_update_rate. '
                                'sensor_update_rate for evaluation steps. '
                                f'(default: {0.01})'
                    )
                )      
            else: 
                self.undeclare_parameter('dt')
                self.undeclare_parameter('sensor_update_rate')
        except Exception as e: 
            raise SystemError(str(e))
        
        self._inactive_params_state = not(self._inactive_params_state)
    
    """ === injection functions === """
    
    def _control_fu_publisher():
        """injection function for controller updates"""
        ...
        
    def _aux_x_injection():
        ...
        
    def x_cb():
        """"""
        ...
        
    def x_aux_unsafe_set_cb():
        ... 
        
    
        
    
        
if __name__ == '__main__':
    rclpy.init()
    
    node = TacticalNode()
    
    rclpy.spin(node)
    
    
    rclpy.shutdown()