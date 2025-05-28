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

import threading
import uuid

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.lifecycle import State, TransitionCallbackReturn
from unique_identifier_msgs.msg import UUID

from hybrid_automaton.config import QOS_PROFILE
from hybrid_automaton.utils import (
    get_current_ros_time,
)
from hybrid_automaton_interfaces.msg import (
    Transition,
    TransitionPending,
)
from hybrid_automaton.scripts.nodes.managed_node import AutomatonManagedNode

class TransitionEvaluatorLifecycleNode(AutomatonManagedNode):

    def __init__(self, node_name, namespace, **kwargs) -> None:
        """
        Initialize the managed node default parameters and attributes
        """
        super().__init__(node_name, namespace=namespace,**kwargs)

        self.transition_event = threading.Event()
        self._guards_status = None
        self._resets_status = None
        self._current_transition_uuid = None

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """on configuration state initializes node attributes like subscribers and publishers"""
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'")

        try: 
            self.transition_pending_pub = self.create_publisher(
                topic="/hybrid_automaton/transition_pending",
                msg_type=TransitionPending,
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
            )
            self.transition_eval_pub = self.create_publisher(
                topic="/hybrid_automaton/transitions",
                msg_type=Transition,
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
            )
            def transition_pending_callback(msg: TransitionPending):
                if msg.transition_pending:
                    self.transition_event.set()   # Signal that a transition is pending
                else:
                    self.transition_event.clear()  # Signal that the transition is complete
            self.transition_pending_sub =  self.create_subscription(
                topic="/hybrid_automaton/transition_pending",
                msg_type=TransitionPending,
                callback=transition_pending_callback,
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
            )
            self.eval_timer = self.create_timer(
                1.0/self.eval_hz,
                callback=self._transition_eval_callback,
                callback_group=self.feedback_callback_group
            )
        except Exception as e:
            self.get_logger().error(
                f"Transition to 'configure' failed for node '{self.get_name()}' while in state '{state.label}'. "
                f"Exception: {str(e)}. Aborting transition."
            )
            return TransitionCallbackReturn.FAILURE

        return super().on_configure(state)

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """
        Transition to activate state
        This transition will start the transition evaluation callbacks starting the key functionality of this node.
        """
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")
        return super().on_activate(state)

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        """
        transition to deactivate state
        This state will stop running processes.
        """
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")

        try:
            self.transition_event.clear()
            self._guards_status = None
            self._resets_status = None
            self._current_transition_uuid = None
        except Exception as e: 
            self.get_logger().error(
                f"Transition to 'deactivate' failed for node '{self.get_name()}' while in state '{state.label}'. "
                f"Exception: {str(e)}. Aborting transition."
            )
            return TransitionCallbackReturn.FAILURE
    
        return super().on_deactivate(state)

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        """
        transition to shutdown state
        This state will close all processing related to the transition evaluator making 
        node shutdown safe.
        """
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")
        super().on_shutdown(state)
    
    def on_cleanup(self, state):
        """return to unconfigured state for when configuration is done to hybrid automaton config"""
        return super().on_cleanup(state)

    # ==== callback functions ====

    def _transition_eval_callback(self):
        """Evaluate transitions based on the current control mode in the Hybrid Automaton."""
        if not self.activate: # this signifies we are in the activated state for this mode.
            return
        
        if self.transition_event.is_set():
            self.get_logger().info('transition event in progress, skipping evaluation')
            ros_stamp = get_current_ros_time()
            transition_eval = Transition(success=True, error_message='No error, currently transitioning.')
            transition_pending = TransitionPending(transition_pending = True, stamp=ros_stamp, transition_uuid=self._current_transition_uuid)
            self.transition_pending_pub.publish(transition_pending)
            return
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
                    current_mode = self.mode.lower()
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
    executor = MultiThreadedExecutor(num_threads=4)
    node = TransitionEvaluatorLifecycleNode('transition_evaluator', 'hybrid_automaton')

    try:
        executor.add_node(node)
        executor.spin()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        rclpy.logging.get_logger('transition_evaluator').error(f'Unhandled exception: {e}')
    finally:
        print('closing node')
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

