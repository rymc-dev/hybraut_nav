#!/usr/bin/python3
"""
"""

import sys
import os

# Add path two directories back
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from rclpy.executors import MultiThreadedExecutor
import rclpy
from rclpy.node import Node
import os
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate
from colav_interfaces.msg import GuardsStatus
from colav_hybrid_eval.utils import get_current_ros_time
from config.qos_config import QOS_PROFILE
from colav_hybrid_eval.scripts.guards import (
    guard_CRUISE_to_FB,
    guard_CRUISE_to_T2LOS_1,
    guard_CRUISE_to_T2LOS_2,
    guard_CRUISE_to_WAYPOINT_REACHED,
    guard_T2LOS_to_CRUISE,
    guard_T2LOS_to_FB,
    guard_T2LOS_to_WAYPOINT_REACHED,
    guard_WAYPOINT_REACHED_to_CRUISE
)
from builtin_interfaces.msg import Duration
from rclpy.executors import MultiThreadedExecutor
from colav_interfaces.msg import Waypoint, UnsafeSet, Waypoints
from std_msgs.msg import String
from typing import List
from std_srvs.srv import Trigger

class InitializationError(Exception):
    """Custom exception for initialization-related failures."""
    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message

class HAGuardsNode(Node):
    _MODES = {  # dict showing the name of the control modes.
        1: "CRUISE",
        2: "T2LOS",
        3: "FB",
        4: "WAYPOINT_REACHED"
    }

    def __init__(
        self,
        namespace:str = "hybrid_automaton",
        name:str = "guards_node"
    ):
        super().__init__(name, namespace=namespace)

        # Initialize the ThreadPoolExecutor
        self.executor = MultiThreadedExecutor()

        self._current_agent_state = None
        self._current_obstacles_state = None
        self._current_waypoint = None
        self._current_waypoints = None
        self._current_unsafe_set = None
        self._current_control_mode = None

        self._NODE_SUBS = None
        self._NODE_PUBS = None
        self._NODE_TIMERS = None

        # Initialisation functions
        self._NODE_SRVS = self._init_node_srvs()
        self.get_logger().info(f"{namespace}/{name} node initialised!")

    def _init_node_srvs(self, node_name: str = 'guards_node'):
        try:
            return {
                "start_guards_evaluation": self.create_service(
                    srv_type=Trigger,
                    srv_name=f"{node_name}/start_guard_evaluation",
                    callback=self._start_guards_evaluation_callback
                ),
                "stop_guards_evaluation": self.create_service(
                    srv_type=Trigger,
                    srv_name=f"{node_name}/stop_guards_evaluation",
                    callback=self._stop_guards_evaluation_callback
                )
            }
        except Exception as e: 
            self.get_logger().error(f"{self.__class__}::_init_node_pubs: Exception occured: {str(e)}")

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

            # Initialize node subscribers
            self._node_subs = self._init_node_subs()
            self.get_logger().debug(f'Node subscribers initialized: {self._node_subs}')

            # Initialize node publishers
            self._node_pubs = self._init_node_pubs()
            self.get_logger().debug(f'Node publishers initialized: {self._node_pubs}')

            # Initialize timers
            self._node_timers = self._init_node_timers()
            self.get_logger().debug(f'Node timers initialized: {self._node_timers}')

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
            self.get_logger().error(f'Unexpected error in _start_guards_evaluation_callback: {str(e)}')

        return response

    def _stop_guards_evaluation_callback(self, request: Trigger.Request, _) -> Trigger.Response:
        """
        callback to stop guards guards evaluation:
        - destroys the Subscrbers, Publisher, and timers
        - returns a Trigger.Response indicating success or error details
        """
        response = Trigger.Response()
        try:
            if self._NODE_SUBS is not None:
                for key in self._NODE_SUBS:
                    self.destroy_subscription(self._NODE_SUBS[key])
            if self._NODE_PUBS is not None:
                for key in self._NODE_PUBS:
                    self.destroy_publisher(self._NODE_PUBS[key])
            if self._NODE_TIMERS is not None:
                for key in self._NODE_TIMERS:
                    self.destroy_timer(self._NODE_TIMERS[key])

            response.success = True
            response.message = 'Successfully shut down subs, pubs and srvs related to guards_evaluation'
        except Exception as e: 
            response.success = False
            response.message = str(e)

        return response

    def _init_node_pubs(self):
        """initialize the node publisher"""
        try:
            return {
                "guards_status": self.create_publisher(
                    msg_type=GuardsStatus,
                    topic="/hybrid_automaton/guards_status",
                    qos_profile=QOS_PROFILE
                )
            }
        except Exception as e: 
            raise InitializationError(f"Publishers",  f"Failed to create one or more subscriptions: {e}")

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
            raise InitializationError('timers', f"Failed to create one or more subscriptions: {e}")
        
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
                guards_status.error_message = "Transition evaluation states required not updated"
                guards_status.timestamp = current_time
                self._NODE_PUBS["guards_status"].publish(guards_status)
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
                guards_status.guard_names = ["cruise_to_t2los_1", "cruise_to_t2los_2", "cruise_to_fb", "cruise_to_waypoint_reached"]
                if not self._validate_state_updates(mode_cruise):
                    guards_status.error = True
                    guards_status.error_message = "Control mode set, but state updates not received for guard evaluation"
                    guards_status.timestamp = current_time
                    self._NODE_PUBS["guards_status"].publish(guards_status)
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
                guards_status.guard_names = ["t2los_to_cruise", "t2los_to_fb", "t2los_to_waypoint_reached"]
                if not self._validate_state_updates(mode_t2los):
                    guards_status.error = True
                    guards_status.error_message = "Control mode set, but state updates not received for guard evaluation"
                    guards_status.timestamp = current_time
                    self._NODE_PUBS["guards_status"].publish(guards_status)
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
                    self._NODE_PUBS["guards_status"].publish(guards_status)
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
                    self._NODE_PUBS["guards_status"].publish(guards_status)
                    return

                # TODO: validate timestamps if necessary
                guards_status.waypoint_reached_to_cruise = guard_WAYPOINT_REACHED_to_CRUISE(
                    waypoints=self._current_waypoints
                )

            else:
                self.get_logger().info("Unknown control mode encountered")
                self._NODE_PUBS["guards_status"].publish(
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
        self._NODE_PUBS["guards_status"].publish(guards_status)

    def _state_update_check(self):
        pass

    def _init_node_subs(self):
        """initialisation the nodes subscriptions for the guard_evaluation component."""
        try:
            return {
                "mode": self.create_subscription(
                    topic="/hybrid_automaton/mode",
                    msg_type=String,
                    callback=self._control_mode_update,
                    qos_profile=QOS_PROFILE
                ),
                "waypoints": self.create_subscription(
                    topic="/hybrid_automaton/waypoints",
                    msg_type= Waypoints,
                    callback=self._waypoints_update,
                    qos_profile=QOS_PROFILE
                ), 
                "agent_update": self.create_subscription(
                    topic = "/agent_update",
                    msg_type = AgentUpdate,
                    callback=self._agent_update_callback,
                    qos_profile=QOS_PROFILE
                ),
                "obstacles_update": self.create_subscription(
                    topic = "/obstacles_update",
                    msg_type = ObstaclesUpdate,
                    callback = self._obstacles_update,
                    qos_profile=QOS_PROFILE
                ),
                "unsafe_set": self.create_subscription(
                    topic="/unsafe_set",
                    msg_type=UnsafeSet,
                    callback=self._unsafe_set_callback,
                    qos_profile=QOS_PROFILE
                )
            }
        except Exception as e:
            raise InitializationError("Subscribers", f"Failed to create one or more subscriptions: {e}")
    
    def _waypoints_update(self, waypoints: Waypoints):
        self._current_waypoints = waypoints
        if len(waypoints.waypoints):
            self._current_waypoint = self._current_waypoints.waypoints[0]
        else:
            self._current_waypoint = None   

    def _control_mode_update(self, control_mode: String):
        self._current_control_mode = control_mode.data

    def _agent_update_callback(self, agent_update: AgentUpdate):
        self._current_agent_state = agent_update

    def _obstacles_update(self, obstacle_update: ObstaclesUpdate):
        self._current_obstacles_state = obstacle_update

    def _unsafe_set_callback(self, unsafe_set_update: UnsafeSet):
        self._current_unsafe_set = unsafe_set_update

def main(args=None):
    rclpy.init(args=args)
    node = HAGuardsNode()
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
