#!/usr/bin/python3
"""
A real-time ROS 2 node that evaluates and publishes the control dynamics
of an agent based on its current state and control mode.

The `DynamicsNode` operates within a hybrid control architecture, switching
between different controller implementations such as CRUISE, T2LOS (Trajectory-To-Line-of-Sight),
FALLBACK, and WAYPOINT_REACHED. Each controller is responsible for generating
appropriate dynamics based on situational inputs like agent state and waypoints.

This node subscribes to:
- Control mode updates (String)
- Agent state updates (AgentUpdate)
- Waypoint updates (Waypoints)

It publishes:
- DynamicsUpdate messages, containing evaluated dynamics and metadata

Services:
- `/dynamics_node/start_dynamics_evaluation`: Starts dynamics evaluation
- `/dynamics_node/stop_dynamics_evaluation`: Placeholder for stopping evaluation

Key Features:
- Modular design using a dictionary for control mode-to-function mapping
- Timed callback for continuous dynamics evaluation
- Built-in error handling and diagnostics via ROS 2 logging
- Easily extendable to support new control modes or logic

This class is central to ensuring real-time reactive behavior in the agent,
enabling adaptive control across dynamic scenarios.

Attributes:
    _MODES (dict): Maps control mode IDs to their string names.
    _DYNAMICS (dict): Maps control mode names to their corresponding function handlers.
    _control_mode (str): Current active control mode.
    _agent_state (AgentUpdate): Latest received state of the agent.
    _waypoint (Waypoint): Active navigation waypoint for trajectory guidance.
    _dynamics_pub (Publisher): ROS publisher for `DynamicsUpdate` messages.

Version: 0.0.1
Author: Ryan McKee
Date: April 17, 2025
"""

from rclpy.callback_groups import ReentrantCallbackGroup
from hybrid_automaton.config.qos_config import QOS_PROFILE
from hybrid_automaton.utils import (
    get_current_ros_time
)
from std_msgs.msg import String
from rclpy.lifecycle import Node, State, TransitionCallbackReturn
import rclpy

from rcl_interfaces.msg import ParameterDescriptor
import uuid
from unique_identifier_msgs.msg import UUID
from colav_interfaces.msg import AgentUpdate

from hybrid_automaton_interfaces.msg import Dynamics
from hybrid_automaton.scripts.nodes.managed_node import AutomatonManagedNode

import rclpy
from rclpy.executors import MultiThreadedExecutor

class DynamicFeedbackLifecycleNode(AutomatonManagedNode):

    def __init__(self, node_name, namespace, **kwargs) -> None:
        """
        Initialize the managed node default parameters and attributes
        """
        super().__init__(node_name, namespace=namespace, **kwargs)

    def on_configure(self, state):
        """on configuration state initializes node attributes like subscribers and publishers"""
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'")
        try: 
            self._dynamics_pub = self.create_publisher(
                msg_type=Dynamics,
                topic='/hybrid_automaton/dynamics',
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
            )
        except Exception as e:
            self.get_logger().info(str(e))
            return TransitionCallbackReturn.FAILURE

        return super().on_configure(state)
    

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """
        Transition to activate state
        This transition will start the transition evaluation callbacks starting the key functionality of this node.
        """
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")

        try: 
            self._dynamics_timer = self.create_timer(
                1/self.eval_hz,
                self._dynamics_callback,
                callback_group=self.dynamic_feedback_callback_group
            )
        except Exception as e:
            self.get_logger().error(str(e))
            return TransitionCallbackReturn.FAILURE

        return super().on_activate(state)
    
    def on_deactivate(self, state):
        """
        transition to deactivate state
        This state will stop running processes.
        """
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")
        return super().on_deactivate(state)

    def on_cleanup(self, state):
        return super().on_cleanup(state)
    
    def on_shutdown(self, state):
        """
        transition to shutdown state
        """
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")
        return super().on_shutdown()

    """callback functions"""

    def _dynamics_callback(self):
        """updating dynamics"""
        if not self.activate:
            return
        
        dynamics_update = Dynamics()
        ros_stamp = get_current_ros_time()
        dynamics_update.stamp = ros_stamp
        generated_uuid = uuid.uuid4()

        ros_uuid = UUID()
        ros_uuid.uuid = list(generated_uuid.bytes)

        dynamics_update.dynamic_uuid = ros_uuid

        def publish_error(mode:str, message: str):
            dynamics_update.success = False
            dynamics_update.error_message = message
            dynamics_update.stamp = ros_stamp
            self._dynamics_pub.publish(dynamics_update)

        try:
            try: 
                current_mode = self.mode.lower()
            except Exception as e: 
                raise ValueError('Hybrid Automaton Control Mode not received /hybrid_automaton/mode')
            
            if current_mode not in [mode for mode in self.config['modes']]:
                publish_error(current_mode, f"Current Hybrid Automaton Mode published to /hybrid_automaton/mode: '{current_mode}' is not among Hybrid Automaton Mode configuration: '{[mode for mode in self.config['modes']]}'")
                return

            dynamics_update.mode = current_mode
            self.config['dynamics'][self.config['modes'][current_mode]['dynamics']]
            dynamics_update.dynamic_parameters.controller_name = self.config['modes'][current_mode]['dynamics']
            dynamics_update.dynamic_parameters.dynamic_name = list(self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['output'].keys())
            dynamics_update.dynamic_parameters.dynamic_units = list(self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['output'].values())

            dynamic_function =  self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['function']
            if 'state_inputs' in  self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]:
                state_input_names = self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['state_inputs']
                state_inputs = [self.config['states'][state_name]['state'] for state_name in state_input_names]
                dynamics_update.dynamic_parameters.dynamic_value = dynamic_function(*state_inputs)
            else: 
                dynamics_update.dynamic_parameters.dynamic_value = dynamic_function()

            # dynamics_update.dynamics = dynamics
            dynamics_update.success = True
        except Exception as e:
            publish_error(mode='', message=str(f"Exception occured: {e}"))
            return
        
        self._dynamics_pub.publish(dynamics_update)

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DynamicFeedbackLifecycleNode("dynamics_feedback", "hybrid_automaton")
        executor = MultiThreadedExecutor()  # Create a multi-threaded executor
        executor.add_node(node)  # Add your node to the executor
        executor.spin()  # Spin the executor instead of rclpy.spin
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Exception occurred: {str(e)}')
    finally:
        if node:
            node.destroy_node()  # Ensure the node is properly destroyed after spinning
        rclpy.shutdown()

if __name__ == '__main__':
    main()
