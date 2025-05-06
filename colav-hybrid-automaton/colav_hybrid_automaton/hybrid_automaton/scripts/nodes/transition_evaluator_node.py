#!/usr/bin/python3
"""
This module defines the `GuardsNode` class, a real-time ROS 2 node that manages
and evaluates guards for the COLAV Hybrid Automaton. It operates within the
hybrid evaluation framework, providing services to start and stop guard evaluations
and continuously monitors incoming state data to evaluate conditions that trigger
transitions between different modes of operation.

The `GuardsNode` interacts with various components, such as agent state, obstacles,
waypoints, and unsafe sets, to determine when to transition between control modes,
such as CRUISE, T2LOS, FB, and WAYPOINT_REACHED. It publishes the results of these
evaluations to a dedicated topic for downstream processes to react to.

Key Features:
- Subscribes to topics for agent state, obstacles, waypoints, and unsafe set updates.
- Provides services to start and stop the evaluation process.
- Evaluates mode transitions in real-time based on incoming data and control logic.
- Publishes evaluation results to a specified topic for external systems to consume.

This class is crucial for ensuring that the system can adapt to dynamic conditions
and make real-time decisions regarding its behavior and transitions.

Version: 0.0.1
Author: Ryan McKee
Date: April 17, 2025
"""


# === Standard Library Imports ===
import os
import sys
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            '..')))

from collections import deque
from hybrid_automaton.config import QOS_PROFILE
# from hybrid_automaton.scripts.guards import (
#     is_los_clear_to_waypoint,
#     is_heading_within_tolerance,
#     is_unsafe_conditions,
#     is_waypoint_reached,
#     is_heading_not_within_tolerance,
#     is_virtual_waypoints
# )
from hybrid_automaton.utils import (
    get_current_ros_time, 
    load_yml,
    process_automaton_config,
    create_state_subscriptions
)

from colav_interfaces.msg import (
    AgentUpdate,
    ObstaclesUpdate,
    UnsafeSet,
)
from hybrid_automaton_interfaces.msg import (
    Transition,
    TransitionPending,
    TransitionTimer,
    Waypoints
)
from functools import partial
from ament_index_python.packages import get_package_share_directory
from std_srvs.srv import Trigger
from std_msgs.msg import String
from builtin_interfaces.msg import Duration
from rclpy.node import Node
import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rcl_interfaces.msg import ParameterValue
import uuid
from unique_identifier_msgs.msg import UUID


import importlib
import yaml
from rclpy.action import ActionServer

default_hybrid_automaton_config = os.path.join(get_package_share_directory('colav_hybrid_automaton'), 'config', 'colav_hybrid_automaton_config.yml')

def load_module_attribute(module_path: str, attr_name: str):
    """Dynamically import a module and retrieve an attribute (e.g., class or function)."""
    try:
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to import '{attr_name}' from '{module_path}': {e}")

class InitializationError(Exception):
    """Custom exception for initialization-related failures."""

    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message


class TransitionEvaluatorNode(Node):
    """
    GuardsNode is an rclpy node that implements real-time Guard evaluations
    for the COLAV Hybrid Automaton.

    This node provides services to start and stop the guard evaluation process.
    It continuously evaluates guards in real time based on incoming state data
    from subscribed topics and publishes the results to a dedicated
    'guard_evaluations' topic.
    """

    def __init__(self, namespace: str = "hybrid_automaton", name: str = "guards_node"):
        """
        Initializes the guards_node
        """
        
        super().__init__(name, namespace=namespace)

        self.declare_parameter(
            'hybrid_automaton_config_path',
            value=default_hybrid_automaton_config,
            descriptor=ParameterDescriptor(description='Path to the Hybrid Automaton configuration file')
        )

        # Load automaton configuration
        self.config = load_yml(
            self.get_parameter('hybrid_automaton_config_path').get_parameter_value().string_value
        )
        self.config = process_automaton_config(self.config)

        # Declare the parameter correctly

        from rcl_interfaces.msg import Parameter
        # declare parameter for transition evaluation hz
        self.declare_parameter(
            'transition_evaluation_hz',
            value=self.config['params']['transition_evaluation_hz'],
            descriptor=ParameterDescriptor(description='transition evaluation hz for guard evaluations')
        )

        # Publishers
        self.transition_pending_pub = self.create_publisher(
            topic="/hybrid_automaton/transition_pending",
            msg_type=TransitionPending,
            qos_profile=QOS_PROFILE
        )

        self.transition_eval_pub = self.create_publisher(
            topic="/hybrid_automaton/transitions",
            msg_type=Transition,
            qos_profile=QOS_PROFILE
        )

        # Subscriptions
        self.create_subscription(
            topic="/hybrid_automaton/mode",
            msg_type=String,
            callback=self._mode_callback,
            qos_profile=QOS_PROFILE
        )

        self.create_subscription(
            topic="/hybrid_automaton/transition_pending",
            msg_type=TransitionPending,
            callback=lambda msg: self.__setattr__('transition_pending', msg),
            qos_profile=QOS_PROFILE
        )

        self.create_subscription(
            topic='/hybrid_automaton/transition_timer',
            msg_type=TransitionTimer,
            callback=lambda msg: self.__setattr__('transition_time', msg), # need to implement this
            qos_profile=QOS_PROFILE
        )   

        # TODO: NEED TO MAKE STATES APART OF THERE PYTHON DICTS SO THAT I CAN ACCESS THE VALUES LOCALLY AND PUBLISH THE DATA
        create_state_subscriptions(node=self)

        # Services
        self.create_service(
            srv_type=Trigger,
            srv_name="/hybrid_automaton/start_guards_eval",
            callback=self._start_guards_evaluation_callback
        )
        self.create_service(
            srv_type=Trigger,
            srv_name="/hybrid_automaton/stop_guards_eval",
            callback=self._stop_guards_evaluation_callback
        )

        # Internal state
        self.transition_pending = False
        self._current_mode = None
        self._guards_status = None
        self._resets_status = None

        # Log initialization
        self.get_logger().info(f"{namespace}/{name} node initialized.")
        self.get_logger().debug("Publishers, subscribers, and services are ready.")

    """callbacks"""
    def _mode_callback(self, msg: String):
        self._current_mode = msg.data
        self.get_logger().debug(f"Received control mode: {self._current_mode}")

    def _transition_pending_callback(self, msg: TransitionPending):
        self.transition_pending = msg
        self.get_logger().debug("Transition pending status received.")

    # def _buffer_callback(self, msg, key: str):
    #     """a generased buffer callback"""
    # def _state_callback(self, msg, buffer_name: str):
    #     """a generaised state callback for state buffers"""
    #     buffer: deque = self.__getattribute__(buffer_name)
    #     buffer.append(msg)
    #     self.get_logger().debug(f"Updated state buffer for {buffer_name}")

    def _start_guards_evaluation_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response
    ) -> Trigger.Response:
        """
        Callback to start guard evaluation:
        - Initializes subscribers, publishers, and timers
        - Returns a Trigger.Response indicating success or error details
        """
        response = Trigger.Response()
        try:
            # Log the initialization start
            self.get_logger().info('Initializing guards evaluation components...')
            transition_evaluation_hz=self.get_parameter('transition_evaluation_hz').value
            self.eval_timer = self.create_timer(
                1.0/transition_evaluation_hz,
                callback=self._eval_transitions
            )
            self.get_logger().debug(
                f"transition_eval_timer started, evaluating at '{transition_evaluation_hz}hz'."
            )

            # Update response on success
            response.success = True
            response.message = 'Guards evaluation started successfully'
            self.get_logger().info('Guard evaluation started successfully')

        except InitializationError as init_err:
            # Handle known initialization errors separately
            response.success = False
            response.message = f'Initialization failed: {init_err}'
            self.get_logger().error(response.message)

        except Exception as e:
            # Catch-all for unexpected exceptions with full traceback
            response.success = False
            response.message = f'Unexpected error during guards evaluation startup: {str(e)}'
            self.get_logger().error(
                f'Unexpected error in _start_guards_evaluation_callback: {str(e)}')

        return response

    def _stop_guards_evaluation_callback(
        self,
        request: Trigger.Request,
        _,
    ) -> Trigger.Response:
        """
        callback to stop guards guards evaluation:
        - destroys the Subscrbers, Publisher, and timers
        - returns a Trigger.Response indicating success or error details
        """
        response = Trigger.Response()
        try:
            for collection in (
                    self._node_subs,
                    self._node_pubs,
                    self._node_timers):
                for handle in collection.values():
                    destroy = getattr(
                        self, f"destroy_{handle.__class__.__name__.lower()}", None)
                    if callable(destroy):
                        destroy(handle)
            response.success = True
            response.message = 'Guards evaluation stopped successfully'
            self.get_logger().info(response.message)
        except Exception as e:
            self.get_logger().exception('Error in stop callback')
            response.success = False
            response.message = str(e)
        return response

    def _waypoints_update_callback(self, waypoints: Waypoints):
        """
        Callback function for waypoints subscription.

        Updates the internal `_current_waypoints` and sets `_current_waypoint`
        to the first waypoint if available; otherwise sets it to None.
        """
        self._current_waypoints = waypoints

        waypoints_list = getattr(waypoints, 'waypoints', [])
        if waypoints_list:
            self._current_waypoint = waypoints_list[0]
        else:
            self._current_waypoint = None

    def _validate_state_updates(self, mode: str) -> bool:
        """Ensure all necessary state variables are available for the given mode."""
        required_states = [
            
            self.agent_state_buffer,
            self.obstacles_state_buffer,
            self.unsafe_set_state_buffer,
            self._current_waypoints,
            self._current_waypoint,
        ]
        if any(state is None for state in required_states):
            return False
        return True

    def _eval_transitions(self):
        """Evaluate transitions based on the control mode.""" 
        # 1. Get metadata for transition
        
        ros_stamp = get_current_ros_time()
        generated_uuid = uuid.uuid4()

        ros_uuid = UUID()
        ros_uuid.uuid = list(generated_uuid.bytes)

        transition_eval = Transition(stamp=ros_stamp, transition_uuid=ros_uuid)
        transition_pending = TransitionPending(stamp=ros_stamp, transition_uuid=ros_uuid)
        
        def publish_error(mode:str, message: str):
            transition_eval.success = False
            transition_eval.error_message = message
            transition_eval.stamp = ros_stamp
            self.transition_eval_pub.publish(transition_eval)

        try:
            try: 
                current_mode = self._current_mode.lower()
            except Exception as e: 
                raise ValueError('Hybrid Automaton Control Mode not received /hybrid_automaton/mode')

            # validate state data for this transition evaluation
            if current_mode is None:
                publish_error("NULL", "Hybrid Automaton Mode has not been published to /hybrid_automaton/mode.")
                return

            if current_mode not in [mode for mode in self.config['modes']]:
                publish_error(current_mode, f"Current Hybrid Automaton Mode published to /hybrid_automaton/mode: '{current_mode}' is not among Hybrid Automaton Mode configuration: '{[mode for mode in self.config['modes']]}'")
                return
            
            # Make transition evaluations 
            transition_eval.mode = current_mode

            transitions = self.config['modes'][transition_eval.mode]['transitions']
            transition_names = list(transitions.keys()) if len(transitions) > 0 else []


            transition_eval.transition_names = transition_names    
            values = []
            for transition in transition_names:
                guard_func = self.config['guards'][(self.config['transitions'][transition]['guard'])]['function']
                state_inputs = [self.config['states'][state]['state'] for state in (self.config['guards'][(self.config['transitions'][transition]['guard'])]['state_inputs'])]
                value:bool = guard_func(*state_inputs)
                values.append(value)

            transition_eval.transition_values = values
            transition_eval.success = True

            # if any transitions for current mode evlauted as true
            if True in values: 
                transition_pending.transition_pending = True

        except Exception as e:
            publish_error(mode=self._current_mode, message=str(e))
            return
        
        self.transition_eval_pub.publish(transition_eval)
        self.transition_pending_pub.publish(transition_pending)

from rclpy.executors import MultiThreadedExecutor

def main(args=None):
    rclpy.init(args=args)
    node = TransitionEvaluatorNode()
    try:
        # executor = MultiThreadedExecutor()
        # executor.add_node(node)
        # executor.spin()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
