#!/usr/bin/python3
"""
"""

import sys
import os

# Add path two directories back
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import rclpy
from rclpy.node import Node
import os
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate
from colav_interfaces.msg import GuardsStatus
from utils import get_current_ros_time
from config.qos_config import QOS_PROFILE
from scripts.guards import (
    guard_CRUISE_to_FB,
    guard_CRUISE_to_T2LOS_1,
    guard_CRUISE_to_T2LOS_2,
    guard_CRUISE_to_WAYPOINT_REACHED,
    guard_T2LOS_to_CRUISE,
    guard_T2LOS_to_FB,
    guard_T2LOS_to_WAYPOINT_REACHED,
    guard_WAYPOINT_REACHED_to_CRUISE
)
from rclpy.executors import MultiThreadedExecutor
from colav_interfaces.msg import Waypoint, UnsafeSet, Waypoints
from std_msgs.msg import String
from typing import List

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

        self._current_agent_state = AgentUpdate()
        self._current_obstacles_state = ObstaclesUpdate()
        self._current_waypoint = Waypoint()
        self._current_waypoints = List[Waypoint]
        self._current_unsafe_set = UnsafeSet()

        # Initialisation functions
        self._current_control_mode = None
        self._NODE_SUBS = self._init_node_subs()
        self._NODE_PUBS = self._init_node_pubs()
        self._NODE_TIMER = self._init_node_timers()

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
            self.get_logger().error(f"{self.__class__}::_init_node_pubs: Exception occured: {str(e)}")

    def _init_node_timers(self):
        """initialize the node timers"""
        try:   
            return {
                "transition_eval_timer": self.create_timer(
                    timer_period_sec=float(1),
                    callback=self._evaluate_transitions
                )
            }
        except Exception as e:
            self.get_logger().error(f"{self.__class__}::_init_node_timers: Exception occured: {str(e)}")
            raise e
        
    def _evaluate_transitions(self):
        """evalute the transitions passed in based on the control mode"""
        guards_status = GuardsStatus()
        try:
            if self._current_control_mode == None:
                guards_status.control_mode = "NA"
                guards_status.error = True
                guards_status.status.error_message = "transition evaluation states required not updated"
                guards_status.timestamp = get_current_ros_time()
                self._NODE_PUBS["guards_status"].publish(guards_status)
                return
            else: 
                # if _current_control_mode is given
                if self._current_control_mode == self._MODES[1]:
                    # CRUISE Transitions
                    guards_status.control_mode = self._MODES[1]

                    # T2LOS1
                    guards_status.cruise_to_t2los1 = guard_CRUISE_to_T2LOS_1(
                        agent_state = self._current_agent_state,
                        obstacles_state = self._current_obstacles_state,
                        unsafe_set = self._current_unsafe_set,
                        waypoint = self._current_waypoint,
                        dsf = 80
                    )
                    # T2LOS2 
                    guards_status.cruise_to_t2los1 = guard_CRUISE_to_T2LOS_2(
                        agent_state= self._current_agent_state,
                        current_waypoint= self._current_waypoint,
                        heading_error_tolerance=0.1
                    )

                    # FALLBACK
                    guards_status.cruise_to_fb = guard_CRUISE_to_FB(
                        agent_state=self._current_agent_state,
                        obstacles_state=self._current_obstacles_state,
                        unsafe_set=self._current_unsafe_set
                    )
                    # WAYPOINT_REACHED
                    guards_status.cruise_to_waypoint_reached = guard_CRUISE_to_WAYPOINT_REACHED(
                        agent_state=self._current_agent_state,
                        current_waypoint=self._current_waypoint
                    )
                elif self._current_control_mode == self._MODES[2]:
                    # T2LOS Transitions
                    guards_status.control_mode = self._MODES[2]

                    # CRUISE
                    guards_status.t2los_to_cruise = guard_T2LOS_to_CRUISE(
                        agent_state=self._current_agent_state,
                        current_waypoint=self._current_waypoint,
                        heading_error_tolerance=0.1
                    )

                    # Fallback
                    guards_status.t2los_to_fb = guard_T2LOS_to_FB(
                        agent_state=self._current_agent_state,
                        obstacles_state=self._current_obstacles_state,
                        unsafe_set=self._current_unsafe_set
                    )

                    # WAYPOINT_REACHED
                    guards_status.t2los_to_waypoint_reached = guard_T2LOS_to_WAYPOINT_REACHED(

                    )

                elif self._current_control_mode == self._MODES[3]:
                    # fallback
                    guards_status.control_mode = self._MODES[3]

                elif self._current_control_mode == self._MODES[4]:
                    # CRUISE
                    guards_status.control_mode = self._MODES[4]

                    guards_status.waypoint_reached_to_cruise = guard_WAYPOINT_REACHED_to_CRUISE(
                        waypoints=self._current_waypoints
                    )
                else:
                    self.get_logger().info('exception occured')
                    self._NODE_PUBS["guards_status"].publish(GuardsStatus(
                        control_mode="NA",
                        timestamp=get_current_ros_time()
                    ))

        except Exception as e: 
            self.get_logger().info(str(e))
            guards_status.error = True
            guards_status.error_message = str(e)
        
        guards_status.timestamp=get_current_ros_time()
        self._NODE_PUBS["guards_status"].publish(guards_status)

    def _init_node_subs(self):
        try:
            return {
                "control_mode": self.create_subscription(
                    topic="/hybrid_automaton/current_mode",
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
                )
            }
        except Exception as e:
            self.get_logger().error(str(e))
            raise e
    
    def _waypoints_update(self, waypoints: Waypoints):
        self._current_waypoints = waypoints
        self._current_waypoint = self._current_waypoints.waypoints[0]

    def _control_mode_update(self, control_mode: String):
        self._current_control_mode = control_mode.data

    def _agent_update_callback(self, agent_update: AgentUpdate):
        self._current_agent_state = agent_update

    def _obstacles_update(self, obstacle_update: ObstaclesUpdate):
        self._current_obstacles_state = obstacle_update


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = HAGuardsNode()
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
