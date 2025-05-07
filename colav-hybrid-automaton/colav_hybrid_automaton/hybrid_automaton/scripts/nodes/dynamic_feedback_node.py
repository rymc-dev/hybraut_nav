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


from hybrid_automaton.config.qos_config import QOS_PROFILE
from hybrid_automaton.utils import (
    get_current_ros_time, 
    process_automaton_config, 
    load_yml,
    create_state_subscriptions
)
from std_msgs.msg import String
from std_srvs.srv import Trigger
from rclpy.node import Node
import rclpy
import os
import sys

from ament_index_python.packages import get_package_share_directory
from rcl_interfaces.msg import ParameterDescriptor
from functools import partial
import uuid
from unique_identifier_msgs.msg import UUID
import importlib
from colav_interfaces.msg import AgentUpdate

from hybrid_automaton_interfaces.msg import Dynamics

# Add two directories back to sys.path: necessary for local debugging when the package isn't built with colcon,
# allowing imports to work correctly without relying on the build process.
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..')))


class InitializationError(Exception):
    """Custom exception for initialization-related failures."""

    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message


default_hybrid_automaton_config = os.path.join(get_package_share_directory('colav_hybrid_automaton'), 'config', 'colav_hybrid_automaton_config.yml')

def load_module_attribute(module_path: str, attr_name: str):
    """Dynamically import a module and retrieve an attribute (e.g., class or function)."""
    try:
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to import '{attr_name}' from '{module_path}': {e}")

class DynamicFeedbackNode(Node):
    """
    DynamicsNode is an rclpy node that implemenst real-time dynamics evaluations
    for the COLAV Hybrid Automaton specific to the control mode we are in.

    This node provides services to srtart and stop the dynamics evaluation process.
    It continously evaluates dyanmics in real time based on the incoming waypoint and
    agent_state data we receive from subscribed topics and publishes the results to
    a dedicated `dynamics` topic.
    """

    def __init__(
        self,
        namespace: str = "hybrid_automaton",
        name: str = "dynamic_feedback"
    ):
        """
        Initializes the dynamics_node
        """
        super().__init__(name, namespace=namespace)
        self.declare_parameter(
            'hybrid_automaton_config_path',
            value=default_hybrid_automaton_config,
            descriptor=ParameterDescriptor(description='Path to the Hybrid Automaton configuration file')
        )
        self.config = load_yml(
            self.get_parameter('hybrid_automaton_config_path').get_parameter_value().string_value
        )
        self.config = process_automaton_config(self.config)

        self.declare_parameter(
            'transition_evaluation_hz',
            value=self.config['params']['transition_evaluation_hz'],
            descriptor=ParameterDescriptor(description='transition evaluation hz for guard evaluations')
        )

        self._dynamics_pub = self.create_publisher(
            msg_type=Dynamics,
            topic='/hybrid_automaton/dynamics',
            qos_profile=QOS_PROFILE
        )

        # Internal communication subscriptions
        self._control_mode_sub = self.create_subscription(
            msg_type=String,
            topic='/hybrid_automaton/mode',
            callback=lambda msg: self.__setattr__('_current_mode', msg.data),
            qos_profile=QOS_PROFILE
        )
        # TODO: Need to get rid of this in the future and utilize yml for creating subscriptions for this file
        # self._agent_state_sub = self.create_subscription(
        #     msg_type=AgentUpdate,
        #     topic='/state/agent',
        #     callback=lambda msg: self.__setattr__('_agent_state', msg),
        #     qos_profile=QOS_PROFILE
        # )

        # subscribe to state updates
        create_state_subscriptions(node=self) # uncomment this in future

        # create the node services
        self.create_service(
            srv_type=Trigger,
            srv_name=f'/hybrid_automaton/start_dynamics_eval',
            callback=self._start_dynamics_evaluation_callback
        )
        self.create_service(
            srv_type=Trigger,
            srv_name=f'/hybrid_automaton/stop_dynamics_eval',
            callback=self._stop_dynamics_evaluation_callback
        )


        # Internal State
        self._current_mode = None
        self._agent_state = None

    def _start_dynamics_evaluation_callback(
            self,
            request: Trigger.Request,
            response: Trigger.Response):
        """callback for starting dynamics evaluation callback"""
        try:
            self._dynamics_timer = self.create_timer(
                1/self.get_parameter('transition_evaluation_hz').value,
                self._update_dynamics_callback
            )
            response.success = True
            response.message = "dynamics evaluation successfully started!"
        except Exception as e:
            self.get_logger().error(
                f'error when attempting to start dynamics_evaluation: {str(e)}')
            response.success = False
            response.message = f"Error occured: {str(e)}"

        return response


    def _stop_dynamics_evaluation_callback(
            self,
            request: Trigger.Request,
            response: Trigger.Response):
        # TODO
        pass

    def _update_dynamics_callback(self):
        """updating dynamics"""
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
                current_mode = self._current_mode.lower()
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


import rclpy
from rclpy.executors import MultiThreadedExecutor

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DynamicFeedbackNode()
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
