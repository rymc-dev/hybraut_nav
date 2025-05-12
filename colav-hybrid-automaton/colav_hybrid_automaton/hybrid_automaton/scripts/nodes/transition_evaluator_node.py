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
from hybrid_automaton.utils import (
    get_current_ros_time, 
    load_yml,
    process_automaton_config,
    create_state_subscriptions
)
import threading
from hybrid_automaton_interfaces.msg import (
    Transition,
    TransitionPending,
    TransitionTimer
)
from colav_interfaces.msg import Waypoints
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


class TransitionEvaluatorNode(Node):
    """
    GuardsNode is an rclpy node that implements real-time Guard evaluations
    for the COLAV Hybrid Automaton.

    This node provides services to start and stop the guard evaluation process.
    It continuously evaluates guards in real time based on incoming state data
    from subscribed topics and publishes the results to a dedicated
    'guard_evaluations' topic.
    """

    def __init__(self, namespace: str = "hybrid_automaton", name: str = "transition_evaluator"):
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
            callback=self._transition_pending_callback,
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
            srv_name="/hybrid_automaton/start_transition_eval",
            callback=self._start_guards_evaluation_callback
        )
        self.create_service(
            srv_type=Trigger,
            srv_name="/hybrid_automaton/stop_transition_eval",
            callback=self._stop_guards_evaluation_callback
        )

        # Internal state
        self.transition_event = threading.Event()
        self._current_mode = None
        self._guards_status = None
        self._resets_status = None
        self._current_transition_uuid = None

    """callbacks"""
    def _mode_callback(self, msg: String):
        self._current_mode = msg.data
        self.get_logger().debug(f"Received control mode: {self._current_mode}")

    def _transition_pending_callback(self, msg: TransitionPending):
        self.get_logger().debug("Transition pending status received.")

        if msg.transition_pending:
            self.transition_event.set()   # Signal that a transition is pending
        else:
            self.transition_event.clear()  # Signal that the transition is complete

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
            self.get_logger().error('Error in stop callback')
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

    def _eval_transitions(self):
        """Evaluate transitions based on the current control mode in the Hybrid Automaton."""
        
        if self.transition_event.is_set():
            self.get_logger().info('transition event in progress, skipping evaluation')
            ros_stamp = get_current_ros_time()
            transition_pending = TransitionPending(transition_pending = True, stamp=ros_stamp, transition_uuid=self._current_transition_uuid)
            self.transition_pending_pub.publish(transition_pending)
        else:
            ros_stamp = get_current_ros_time()
            transition_id = uuid.uuid4()
            ros_uuid = UUID()
            ros_uuid.uuid = list(transition_id.bytes)
            self._current_transition_uuid = ros_uuid
            transition_eval = Transition(stamp=ros_stamp, transition_uuid=ros_uuid)
            transition_pending = TransitionPending(stamp=ros_stamp, transition_uuid=ros_uuid)

            def publish_error(message: str):
                transition_eval.success = False
                transition_eval.error_message = message
                transition_eval.stamp = ros_stamp
                self.transition_eval_pub.publish(transition_eval)

            try:
                try:
                    current_mode = self._current_mode.lower()
                    transition_eval.mode = current_mode
                except Exception:
                    raise RuntimeError("Hybrid Automaton Control Mode not received on /hybrid_automaton/mode")

                available_modes = self.config['modes']
                if current_mode not in available_modes:
                    raise ValueError(
                        current_mode,
                        f"Published mode '{current_mode}' is not configured. Available modes: {list(available_modes)}"
                    )

                transitions = available_modes[current_mode].get('transitions', {})
                transition_names = list(transitions.keys())

                transition_eval.success = True
                transition_eval.transition_names = []
                transition_eval.transition_values = []
                transition_eval.transition_priority = []
                error_messages = []

                for name in transition_names:
                    try:
                        transition_config = self.config['transitions'][name]
                        guard_key = transition_config['guard']
                        guard_config = self.config['guards'][guard_key]
                        guard_func = guard_config['function']
                        state_inputs = [self.config['states'][s]['state'] for s in guard_config['state_inputs']]

                        result = bool(guard_func(*state_inputs))
                        transition_eval.transition_names.append(name)
                        transition_eval.transition_values.append(result)
                        transition_eval.transition_priority.append(transitions[name]['priority'])

                    except Exception as e:
                        self.get_logger().error(f"Transition '{name}' guard evaluation failed: {e}")
                        error_messages.append(f"{name}: {e}")
                        transition_eval.success = False

                if error_messages:
                    transition_eval.error_message = "Errors during evaluation: " + "; ".join(error_messages)

                if any(transition_eval.transition_values):
                    transition_pending.transition_pending = True
                    self.transition_event.set()

            except Exception as e:
                publish_error(str(e))
                return
            
            self.transition_eval_pub.publish(transition_eval)
            self.transition_pending_pub.publish(transition_pending)

def main(args=None):
    rclpy.init(args=args)
    node = TransitionEvaluatorNode()
    try:
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
