#!/usr/bin/python3
"""
This module defines the reset `ResetNode` class, a real time ROS 2 node that manages
and performs system state variable resets on request for the COLAV Hybrid Automaton.
Operating within the hybrid evaluation framework, providing services to make
resets if required. it continously updates the values within it .... TODO: Finish this

....

Key Features: 
   ....
   ....

This class is crucial for ensuring that the system can perform resets on transitions 
it is a necessity this is running for the colav_hybrid_automaton.

Version: 0.0.1
Author: Ryan McKee
Date: April 17, 2025
"""


# === Standard Library Imports ===
from rclpy.node import Node
from colav_hybrid_eval.scripts.resets import (
    reset_CRUISE_to_T2LOS,
    reset_WAYPOINT_REACHED_to_CRUISE
)
from colav_interfaces.srv import Reset
from colav_interfaces.msg import Waypoints, AgentUpdate, ObstaclesUpdate, UnsafeSet

# === Configuration ===
from colav_hybrid_eval.config.qos_config import QOS_PROFILE

class InitializationError(Exception):
    """Custom exception for initialization-related failures."""
    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message
import rclpy

class ResetNode(Node):

    _RESETS = {
        'waypoint_reached_to_cruise': reset_WAYPOINT_REACHED_to_CRUISE,
        'cruise_to_t2los': reset_CRUISE_to_T2LOS
    }

    def __init__(
        self,
        name: str = 'resets_node',
        namespace: str = 'hybrid_automaton'
    ):  
        """
        initialise the node
        """
        super().__init__(name, namespace=namespace)

        self._waypoints = None
        self._agent_state = None
        self._obstacles_state = None
        self._unsafe_set = None

        # Create a subscription and publisher to /hybrid_automaton/waypoints
        self._node_subs = self._init_node_subs()
        self._node_pubs = self._init_node_pubs()
        self._node_srvs = self._init_node_srvs()

        self.get_logger().info(f'{namespace}/{name} node initialised!')
    
    def _init_node_pubs(self):
        try:
            return {
                'waypoints_pub': self.create_publisher(
                msg_type=Waypoints,
                topic='hybrid_automaton/waypoints',
                qos_profile=QOS_PROFILE),
            }
        except Exception as e:
            raise InitializationError("Publishers", f'Attempted initialisation of reset_node publishers, but error occured: {str(e)}')

    def _init_node_subs(self):
        try:
            return {
                'waypoints_sub': self.create_subscription(
                    msg_type=Waypoints,
                    topic='/hybrid_automaton/waypoints',
                    callback=lambda msg: self.__setattr__('_waypoints', msg),
                    qos_profile=QOS_PROFILE
                ),
                "agent_state": self.create_subscription(
                    msg_type=AgentUpdate,
                    topic='/agent_update',
                    callback=lambda msg: self.__setattr__('_agent_state', msg),
                    qos_profile=QOS_PROFILE
                ),
                "obstacles_state": self.create_subscription(
                    msg_type=ObstaclesUpdate,
                    topic='/obstacles_update',
                    callback=lambda msg: self.__setattr__('obstacles_update', msg),
                    qos_profile=QOS_PROFILE
                ),
                "unsafe_set": self.create_subscription(
                    msg_type=UnsafeSet,
                    topic='/unsafe_set',
                    callback=lambda msg: self.__setattr__('unsafe_set', msg),
                    qos_profile=QOS_PROFILE
                )
            }
        except Exception as e:
            raise InitializationError("subscribers", f'Attempted initialisation of reset_node subscriptions, but error occured: {str(e)}')

    def _init_node_srvs(self):
        try:
            return {
                "reset": self.create_service(
                    srv_type=Reset(),
                    srv_name='reset',
                    callback=self._reset_callback
                )
            }
        except Exception as e:
            raise InitializationError("services", f'Attempted initialisation of reset_node services, but error occured: {str(e)}')

    def _reset_callback(self, request: Reset.Request, response: Reset.Response):
        """
        callback for reset request
        - performs reset function on state variables depending on transition name passed in
        - throws exception if transition name does not have a reset associated
        - throws exception if something unexpected goes wrong.
        """
        try:
            reset_name = request.transition_name
            self.get_logger().info(f'reset request received for {reset_name}')

            if reset_name in list(self._RESETS.keys()):
                if reset_name == 'waypoint_reached_to_cruise':
                    waypoints = self._RESETS[reset_name](waypoints=self._waypoints)
                    self._node_pubs['waypoints'].publish(waypoints)
                elif reset_name == 'cruise_to_t2los':
                    waypoints = self._RESETS[reset_name](self._agent_state, self._obstacles_state, self._unsafe_set, self._waypoints)
                    self._node_pubs['waypoints'].publish(waypoints)
                else:
                    #something went wrong here 
                    raise Exception ('Invalid reset name')
                response._success = True
                response._message = f"Reset successfully applied"
            else:
                raise ValueError(f"Reset transition name does not exist: {str(reset_name)}")
        except Exception as e:
            self.get_logger().error(f'Error occured during reset_callback: {str(e)}')
            response._success = False
            response._message = f"{str(e)}"

        return response
    
def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ResetNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print (f'Exception occured: {str(e)}')

    rclpy.shutdown()

if __name__ == '__main__':
    main()