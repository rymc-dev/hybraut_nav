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
from hybrid_automaton.config import QOS_PROFILE
from hybrid_automaton.scripts.guards import (
    guard_CRUISE_to_FB,
    guard_CRUISE_to_T2LOS_1,
    guard_CRUISE_to_T2LOS_2,
    guard_CRUISE_to_WAYPOINT_REACHED,
    guard_T2LOS_to_CRUISE,
    guard_T2LOS_to_FB,
    guard_T2LOS_to_WAYPOINT_REACHED,
    guard_WAYPOINT_REACHED_to_CRUISE
)
from hybrid_automaton.utils import get_current_ros_time
from colav_interfaces.msg import (
    AgentUpdate,
    GuardsStatus,
    ObstaclesUpdate,
    UnsafeSet,
    Waypoints
)
from std_srvs.srv import Trigger
from std_msgs.msg import String
from builtin_interfaces.msg import Duration
from rclpy.node import Node
import rclpy
import os
import sys

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


class GuardsNode(Node):
    """
    GuardsNode is an rclpy node that implements real-time Guard evaluations
    for the COLAV Hybrid Automaton.

    This node provides services to start and stop the guard evaluation process.
    It continuously evaluates guards in real time based on incoming state data
    from subscribed topics and publishes the results to a dedicated
    'guard_evaluations' topic.
    """

    # Dict shows the different control modes
    _MODES = {
        1: "CRUISE",
        2: "T2LOS",
        3: "FB",
        4: "WAYPOINT_REACHED"
    }

    def __init__(
        self,
        namespace: str = "hybrid_automaton",
        name: str = "guards_node"
    ):
        """
        Initializes the guards_node
        """
        super().__init__(name, namespace=namespace)

        self._current_agent_state = None
        self._current_obstacles_state = None
        self._current_waypoint = None
        self._current_waypoints = None
        self._current_unsafe_set = None
        self._current_control_mode = None

        self._NODE_SRVS = self._init_node_srvs()
        self.get_logger().info(f"{namespace}/{name} node initialised!")

    def _init_node_srvs(self, node_name: str = 'guards_node'):
        """
        Initializes node services
        - Initializes the start_guard_evaluations stop_guards_evaluation
        - Raises InitializationError if exception thrown during service creation
        """
        try:
            return {
                "start_guards_evaluation": self.create_service(
                    srv_type=Trigger,
                    srv_name=f"/hybrid_automaton/start_guards_eval",
                    callback=self._start_guards_evaluation_callback
                ),
                "stop_guards_evaluation": self.create_service(
                    srv_type=Trigger,
                    srv_name=f"/hybrid_automaton/stop_guards_eval",
                    callback=self._stop_guards_evaluation_callback
                )
            }
        except Exception:
            raise InitializationError(
                'Node Services',
                "Excpetion occured initializing start/stop guard_evaluations services for this node")

    def _start_guards_evaluation_callback(
        self,
        request: Trigger.Request,
        _
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

            self._current_control_mode = self._MODES[1]
            # Initialize node subscribers
            self._node_subs = self._init_node_subs()
            self.get_logger().debug(
                f'Node subscribers initialized: {self._node_subs}')

            # Initialize node publishers
            self._node_pubs = self._init_node_pubs()
            self.get_logger().debug(
                f'Node publishers initialized: {self._node_pubs}')

            # Initialize timers
            self._node_timers = self._init_node_timers()
            self.get_logger().debug(
                f'Node timers initialized: {self._node_timers}')

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

    def _init_node_pubs(self):
        """initialize the node publisher"""
        try:
            return {
                "guards_status": self.create_publisher(
                    msg_type=GuardsStatus,
                    topic="/hybrid_automaton/guards",
                    qos_profile=QOS_PROFILE
                )
            }
        except Exception as e:
            raise InitializationError(
                "Publishers",
                f"Failed to create one or more subscriptions: {e}")

    def _init_node_subs(self):
        """initialisation the nodes subscriptions for the guard_evaluation component."""
        try:
            return {
                "mode": self.create_subscription(
                    topic="/hybrid_automaton/mode",
                    msg_type=String,
                    callback=lambda msg: self.__setattr__(
                        '_current_control_mode',
                        msg.data),
                    qos_profile=QOS_PROFILE),
                "waypoints": self.create_subscription(
                    topic="/hybrid_automaton/waypoints",
                    msg_type=Waypoints,
                    callback=self._waypoints_update_callback,
                    qos_profile=QOS_PROFILE),
                "agent_update": self.create_subscription(
                    topic="/agent_update",
                    msg_type=AgentUpdate,
                    callback=lambda msg: self.__setattr__(
                        '_current_agent_state',
                        msg),
                    qos_profile=QOS_PROFILE),
                "obstacles_update": self.create_subscription(
                    topic="/obstacles_update",
                    msg_type=ObstaclesUpdate,
                    callback=lambda msg: self.__setattr__(
                        '_current_obstacles_state',
                        msg),
                    qos_profile=QOS_PROFILE),
                "unsafe_set": self.create_subscription(
                    topic="/unsafe_set",
                    msg_type=UnsafeSet,
                    callback=lambda msg: self.__setattr__(
                        '_current_unsafe_set',
                        msg),
                    qos_profile=QOS_PROFILE)}
        except Exception as e:
            raise InitializationError(
                "Subscribers",
                f"Failed to create one or more subscriptions: {e}")

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

    def _init_node_timers(self):
        """initialize the node timers"""
        try:
            return {
                "transition_eval_timer": self.create_timer(
                    timer_period_sec=float(0.1),
                    callback=self._evaluate_transitions
                )
            }
        except Exception as e:
            raise InitializationError(
                'timers', f"Failed to create one or more subscriptions: {e}")

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

    def _evaluate_transitions(self):
        """Evaluate transitions based on the control mode."""
        guards_status = GuardsStatus()
        try:
            current_time = get_current_ros_time()

            if self._current_control_mode is None:
                guards_status.control_mode = "NA"
                guards_status.error = True
                guards_status.error_message = "Transition evalustd_srvs/srv/Triggeration states required not updated"
                guards_status.timestamp = current_time
                self._node_pubs["guards_status"].publish(guards_status)
                return

            # Map control modes to shorthand for readability
            mode_cruise = self._MODES[1]
            mode_t2los = self._MODES[2]
            mode_fallback = self._MODES[3]
            mode_waypoint_reached = self._MODES[4]

            # Evaluate based on current control mode
            if self._current_control_mode == mode_cruise:
                # CRUISE
                guards_status.control_mode = mode_cruise
                guards_status.guard_names = [
                    "cruise_to_t2los_1",
                    "cruise_to_t2los_2",
                    "cruise_to_fb",
                    "cruise_to_waypoint_reached"]
                if not self._validate_state_updates(mode_cruise):
                    guards_status.error = True
                    guards_status.error_message = "Control mode set, but state updates not received for guard evaluation"
                    guards_status.timestamp = current_time
                    self._node_pubs["guards_status"].publish(guards_status)
                    return

                # TODO: validate timestamps
                # mock duration for tolerance for now
                # Evaluate CRUISE transitions

                guards_status.cruise_to_t2los_1 = guard_CRUISE_to_T2LOS_1(
                    agent_state=self._current_agent_state,
                    obstacles_state=self._current_obstacles_state,
                    unsafe_set=self._current_unsafe_set,
                    waypoint=self._current_waypoint,
                    dsf=80,
                    tolerance=Duration(sec=3000)
                )
                guards_status.cruise_to_t2los_2 = guard_CRUISE_to_T2LOS_2(
                    agent_state=self._current_agent_state,
                    current_waypoint=self._current_waypoint,
                    heading_error_tolerance=0.1,
                    tolerance=Duration(sec=3000)
                )
                guards_status.cruise_to_fb = guard_CRUISE_to_FB(
                    agent_state=self._current_agent_state,
                    obstacles_state=self._current_obstacles_state,
                    unsafe_set=self._current_unsafe_set,
                    tolerance=Duration(sec=3000)
                )
                guards_status.cruise_to_waypoint_reached = guard_CRUISE_to_WAYPOINT_REACHED(
                    agent_state=self._current_agent_state,
                    current_waypoint=self._current_waypoint,
                    tolerance=Duration(sec=3000)
                )

            elif self._current_control_mode == mode_t2los:
                # T2LOS
                guards_status.control_mode = mode_t2los
                guards_status.guard_names = [
                    "t2los_to_cruise", "t2los_to_fb", "t2los_to_waypoint_reached"]
                if not self._validate_state_updates(mode_t2los):
                    guards_status.error = True
                    guards_status.error_message = "Control mode set, but state updates not received for guard evaluation"
                    guards_status.timestamp = current_time
                    self._node_pubs["guards_status"].publish(guards_status)
                    return

                # TODO: validate timestamps

                guards_status.t2los_to_cruise = guard_T2LOS_to_CRUISE(
                    agent_state=self._current_agent_state,
                    current_waypoint=self._current_waypoint,
                    heading_error_tolerance=0.1,
                    tolerance=Duration(sec=3000)
                )
                guards_status.t2los_to_fb = guard_T2LOS_to_FB(
                    agent_state=self._current_agent_state,
                    obstacles_state=self._current_obstacles_state,
                    unsafe_set=self._current_unsafe_set,
                    tolerance=Duration(sec=3000)
                )
                guards_status.t2los_to_waypoint_reached = guard_T2LOS_to_WAYPOINT_REACHED(
                    agent_state=self._current_agent_state,
                    current_waypoint=self._current_waypoint,
                    tolerance=Duration(sec=3000)
                )

            elif self._current_control_mode == mode_fallback:
                guards_status.control_mode = mode_fallback

                if not self._validate_state_updates(mode_fallback):
                    guards_status.error = True
                    guards_status.error_message = "Control mode set, but state updates not received for guard evaluation"
                    guards_status.timestamp = current_time
                    self._node_pubs["guards_status"].publish(guards_status)
                    return

                # TODO: Validate timestamps for FALLBACK mode if needed
                # Add FALLBACK-specific evaluations here

            elif self._current_control_mode == mode_waypoint_reached:
                # WAYPOINT_REACHED
                guards_status.control_mode = mode_waypoint_reached
                guards_status.guard_names = ["waypoint_reached_to_cruise"]

                if not self._validate_state_updates(mode_waypoint_reached):
                    guards_status.error = True
                    guards_status.error_message = "Control mode set, but state updates not received for guard evaluation"
                    guards_status.timestamp = current_time
                    self._node_pubs["guards_status"].publish(guards_status)
                    return

                # TODO: validate timestamps if necessary
                guards_status.waypoint_reached_to_cruise = guard_WAYPOINT_REACHED_to_CRUISE(
                    waypoints=self._current_waypoints)

            else:
                self.get_logger().info("Unknown control mode encountered")
                self._node_pubs["guards_status"].publish(
                    GuardsStatus(
                        control_mode="NA",
                        timestamp=current_time,
                    )
                )
                return

        except Exception as e:
            guards_status.error = True
            guards_status.error_message = str(e)

        guards_status.timestamp = get_current_ros_time()
        self._node_pubs["guards_status"].publish(guards_status)


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
