#!/usr/bin/python3
"""
"""

import sys
import os

# Add path two directories back
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from colav_hybrid_eval.config.qos_config import QOS_PROFILE
import rclpy
from rclpy.node import Node
from scripts.dynamics import (
    dynamics_CRUISE,
    dynamics_T2LOS,
    dynamics_FB,
    dynamics_WAYPOINT_REACHED
)
from std_srvs.srv import Trigger
from colav_interfaces.msg import AgentUpdate, Waypoints, Waypoint, DynamicsUpdate, Dynamics
from std_msgs.msg import String
from colav_hybrid_eval.utils import get_current_ros_time

class DynamicsNode(Node):
    
    _MODES = {  # dict showing the name of the control modes.
        1: "CRUISE",
        2: "T2LOS",
        3: "FB",
        4: "WAYPOINT_REACHED"
    }

    _DYNAMICS = {
        _MODES[1]: dynamics_CRUISE,
        _MODES[2]: dynamics_T2LOS,
        _MODES[3]: dynamics_FB,
        _MODES[4]: dynamics_WAYPOINT_REACHED
    }

    def __init__(
        self,
        namespace:str = "hybrid_automaton",
        name: str = "dynamics_node"
    ):
        super().__init__(name, namespace=namespace)
        self._control_mode = None
        self._agent_state = None
        self._obstalces_state = None
        self._waypoint = None
        
        self._init_node_srvs()
        self.get_logger().info(f"{namespace}/{name} node initialised!")


    def _init_node_srvs(self, node_name: str = "dynamics_node"):
        """""" 
        try:
            return {
                "start_dynamic_evaluations": self.create_service(
                    srv_type=Trigger,
                    srv_name=f'{node_name}/start_dynamics_evaluation',
                    callback=self._start_dynamics_evaluation_callback
                
                ),
                "stop_dynamics_evaluations": self.create_service(
                    srv_type=Trigger,
                    srv_name=f'{node_name}/stop_dynamics_evaluation',
                    callback=self._stop_dynamics_evaluation_callback
                )
            }
        except Exception as e:
            self.get_logger().error('Error when iniitialising hybrid automaton services')

    def _stop_dynamics_evaluation_callback(self, request: Trigger.Request, response: Trigger.Response):
        pass

    def _start_dynamics_evaluation_callback(self, request: Trigger.Request, response: Trigger.Response):
        """callback for starting dynamics evaluation callback"""
        try:
            self._dynamics_pub = self.create_publisher(
                msg_type=DynamicsUpdate,
                topic='/hybrid_automaton/dynamics',
                qos_profile=QOS_PROFILE
            )
            self._control_mode_sub = self.create_subscription(
                msg_type=String,
                topic='/hybrid_automaton/mode',
                callback=self._control_mode_callback,
                qos_profile=QOS_PROFILE
            )
            self._agent_state_sub=  self.create_subscription(
                AgentUpdate,
                '/agent_update',
                self._agent_update_callback,
                qos_profile=QOS_PROFILE
            )
            self._waypoints_sub = self.create_subscription(
                Waypoints,
                '/hybrid_automaton/waypoints',
                self._waypoints_callback,
                qos_profile=QOS_PROFILE
            )
            self._dynamics_timer = self.create_timer(
                float(0.1),
                self._update_dynamics_callback
            )
            response.success = True
            response.message = "dynamics evaluation successfully started!"
        except Exception as e:
            self.get_logger().error(f'error when attempting to start dynamics_evaluation: {str(e)}')
            response.success = False
            response.message = f"Error occured: {str(e)}"

        return response
    
    def _control_mode_callback(self, msg: String):
        self._control_mode = msg.data
    
    def _agent_update_callback(self, msg: AgentUpdate):
        self._agent_state = msg

    def _waypoints_callback(self, msg: Waypoints):
        """callback to get the current waypoint"""
        if len(msg.waypoints) > 0:
            self._waypoint = msg.waypoints[0]
    
    def _update_dynamics_callback(self):
        """updating dynamics"""
        dynamics_update = DynamicsUpdate()
        try:
            if self._control_mode not in list(self._MODES.values()):
                raise ValueError(f'control mode received: {self._control_mode} not in MODES')
          
            if self._control_mode == self._MODES[1]:
                # CRUISE DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[1]](agent_state=self._agent_state, dt = 0.1) # TODO: NEED DT TO BE CONFIGED BY COLAV_PARAMS
                dynamics_update.control_mode = self._MODES[1]

            elif self._control_mode == self._MODES[2]:
                # T2LOS DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[2]](agent_state = self._agent_state, waypoint=self._waypoint)
                dynamics_update.control_mode = self._MODES[2]

            elif self._control_mode == self._MODES[3]:
                # FALLBACK DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[3]]()
                dynamics_update.control_mode = self._MODES[3]

            elif self._control_mode == self._MODES[4]:
                # WAYPOINT_REACHE DYNAMICS
                dynamics: Dynamics = self._DYNAMICS[self._MODES[4]]()
                dynamics_update.control_mode = self._MODES[4]

            else: # EDGE CASE
                raise RuntimeError('something went wrong here.')
            
            dynamics_update.dynamics = dynamics
            dynamics_update.error = False
        except Exception as e:
            dynamics_update.error = True
            dynamics_update.error_message = f"Error occured: {str(e)}"

        dynamics_update.timestamp =  get_current_ros_time()
        self._dynamics_pub.publish(dynamics_update)

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DynamicsNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print (f'Exception occured: {str(e)}')

    rclpy.shutdown()

if __name__ == '__main__':
    main()