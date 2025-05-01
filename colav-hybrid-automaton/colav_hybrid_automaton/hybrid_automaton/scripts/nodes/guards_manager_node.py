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


from hybrid_automaton.config import QOS_PROFILE
# from hybrid_automaton.scripts.guards import (
#     is_los_clear_to_waypoint,
#     is_heading_within_tolerance,
#     is_unsafe_conditions,
#     is_waypoint_reached,
#     is_heading_not_within_tolerance,
#     is_virtual_waypoints
# )
from hybrid_automaton.utils import get_current_ros_time
from colav_interfaces.msg import (
    AgentUpdate,
    GuardsStatus,
    ObstaclesUpdate,
    UnsafeSet,
    Waypoints,
    TransitionPending
)
from functools import partial
from ament_index_python.packages import get_package_share_directory
from std_srvs.srv import Trigger
from std_msgs.msg import String
from builtin_interfaces.msg import Duration
from rclpy.node import Node
import rclpy

import importlib
import yaml


hybrid_automaton_config_path = os.path.join(get_package_share_directory('colav_hybrid_automaton'), 'config', 'hybrid_automaton_config.yml')

def load_module_attribute(module_path: str, attr_name: str):
    """Dynamically import a module and retrieve an attribute (e.g., class or function)."""
    try:
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to import '{attr_name}' from '{module_path}': {e}")

def initialize_automaton_config(hybrid_automaton_config_path: str, self_ref: object):
    with open(hybrid_automaton_config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize state variables and load message types
    for idx, state in enumerate(config['states']):
        state_name = state['name']
        state_type = state['type']

        # Set dynamic state variable
        setattr(self_ref, f"current_{state_name}_state", None)

        # Import and replace state type with actual class
        module_path, class_name = state_type.rsplit('.', 1)
        msg_class = load_module_attribute(module_path, class_name)
        config['states'][idx]['type'] = msg_class

    # Import guards and resets once
    guard_mod = importlib.import_module("hybrid_automaton.scripts.guards")
    reset_mod = importlib.import_module("hybrid_automaton.scripts.resets")

    # Assign actual guard/reset functions
    for transition in config['transitions']['list']:
        guard_name = transition.get('guard')
        reset_name = transition.get('reset')

        transition['guard'] = getattr(guard_mod, guard_name) if isinstance(guard_name, str) else None
        transition['reset'] = getattr(reset_mod, reset_name) if isinstance(reset_name, str) else None

    return config

class InitializationError(Exception):
    """Custom exception for initialization-related failures."""

    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message


class GuardsNode(Node):
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

        # Load automaton configuration
        self.config = initialize_automaton_config(hybrid_automaton_config_path, self)

        # Publishers
        self.transition_pending_pub = self.create_publisher(
            topic="/hybrid_automaton/transition_pending",
            msg_type=TransitionPending,
            qos_profile=QOS_PROFILE
        )

        self.guards_eval_pub = self.create_publisher(
            topic="/hybrid_automaton/guards",
            msg_type=GuardsStatus,
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

        for state in self.config['states']:
            self.create_subscription(
                topic=state['topic'],
                msg_type=state['type'],
                callback=partial(self._state_callback, state_name=state['name']),
                qos_profile=QOS_PROFILE
            )

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
        self._current_control_mode = msg.data
        self.get_logger().debug("Received control mode: %s", msg.data)

    def _transition_pending_callback(self, msg: TransitionPending):
        self.transition_pending = msg
        self.get_logger().debug("Transition pending status received.")

    def _state_callback(self, msg, state_name: str):
        setattr(self, f"current_{state_name}_state", msg)
        self.get_logger().debug("Updated state for %s", state_name)

    def _start_guards_evaluation_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
        transition_eval_hz: float = 0.1
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

            self.eval_timer = self.create_timer(
                timer_period_sec=1.0/transition_eval_hz,
                callback=self._eval_transitions
            )
            self.get_logger().debug(
                f"transition_eval_timer started, evaluating at '{transition_eval_hz}hz'."
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
            self._current_agent_state,
            self._current_obstacles_state,
            self._current_unsafe_set,
            self._current_waypoints,
            self._current_waypoint,
        ]
        if any(state is None for state in required_states):
            return False
        return True

    def _eval_transitions(self):
        """Evaluate transitions based on the control mode."""
        guards_status = GuardsStatus()
        current_time = get_current_ros_time()

        def publish_error(mode:str, message: str):
            guards_status.error = True
            guards_status.error_message = message
            guards_status.timestamp = current_time
            self.guards_eval_pub.publish(guards_status)

        try:
            mode = self._current_control_mode

            if mode is None:
                publish_error("NULL", "Hybrid Automaton Mode has not been published to /hybrid_automaton/mode.")
                return

            if mode not in [mode['name'] for mode in self.config['modes']]:
                publish_error(mode, f"Current Hybrid Automaton Mode published to /hybrid_automaton/mode: '{mode}' is not among Hybrid Automaton Mode configuration: '{[mode['name'] for mode in self.config['modes']]}'")
                return
            
            # Validate_state_updates should raise an exception
            if self._validate_state_updates(mode):
                publish_error(mode, f"")
                return

            guards_status.control_mode = mode



        #     # Common tolerance used across all guards
        #     common_tolerance = Duration(sec=3000)

        #     if mode_name == "CRUISE":
        #         guards_status.guard_names = [
        #             "cruise_to_t2los_1",
        #             "cruise_to_t2los_2",
        #             "cruise_to_fb",
        #             "cruise_to_waypoint_reached"
        #         ]
        #         guards_status.cruise_to_t2los_1 = guard_CRUISE_to_T2LOS_1(
        #             agent_state=self._current_agent_state,
        #             obstacles_state=self._current_obstacles_state,
        #             unsafe_set=self._current_unsafe_set,
        #             waypoint=self._current_waypoint,
        #             dsf=80,
        #             tolerance=common_tolerance
        #         )
        #         guards_status.cruise_to_t2los_2 = guard_CRUISE_to_T2LOS_2(
        #             agent_state=self._current_agent_state,
        #             current_waypoint=self._current_waypoint,
        #             heading_error_tolerance=0.1,
        #             tolerance=common_tolerance
        #         )
        #         guards_status.cruise_to_fb = guard_CRUISE_to_FB(
        #             agent_state=self._current_agent_state,
        #             obstacles_state=self._current_obstacles_state,
        #             unsafe_set=self._current_unsafe_set,
        #             tolerance=common_tolerance
        #         )
        #         guards_status.cruise_to_waypoint_reached = guard_CRUISE_to_WAYPOINT_REACHED(
        #             agent_state=self._current_agent_state,
        #             current_waypoint=self._current_waypoint,
        #             tolerance=common_tolerance
        #         )

        #     elif mode_name == "T2LOS":
        #         guards_status.guard_names = [
        #             "t2los_to_cruise",
        #             "t2los_to_fb",
        #             "t2los_to_waypoint_reached"
        #         ]
        #         guards_status.t2los_to_cruise = guard_T2LOS_to_CRUISE(
        #             agent_state=self._current_agent_state,
        #             current_waypoint=self._current_waypoint,
        #             heading_error_tolerance=0.1,
        #             tolerance=common_tolerance
        #         )
        #         guards_status.t2los_to_fb = guard_T2LOS_to_FB(
        #             agent_state=self._current_agent_state,
        #             obstacles_state=self._current_obstacles_state,
        #             unsafe_set=self._current_unsafe_set,
        #             tolerance=common_tolerance
        #         )
        #         guards_status.t2los_to_waypoint_reached = guard_T2LOS_to_WAYPOINT_REACHED(
        #             agent_state=self._current_agent_state,
        #             current_waypoint=self._current_waypoint,
        #             tolerance=common_tolerance
        #         )

        #     elif mode_name == "FALLBACK":
        #         # Placeholder for future logic
        #         pass

        #     elif mode_name == "WAYPOINT_REACHED":
        #         guards_status.guard_names = ["waypoint_reached_to_cruise"]
        #         guards_status.waypoint_reached_to_cruise = guard_WAYPOINT_REACHED_to_CRUISE(
        #             waypoints=self._current_waypoints
        #         )

        except Exception as e:
            publish_error(str(e))
            return

        guards_status.timestamp = get_current_ros_time()
        self.guards_eval_pub.publish(guards_status)

def main(args=None):
    rclpy.init(args=args)
    node = GuardsNode()
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
