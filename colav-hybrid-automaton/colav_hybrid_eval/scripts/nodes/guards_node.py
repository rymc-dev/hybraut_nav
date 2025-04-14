import sys
import os

# Add path two directories back
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult, ParameterType
import os
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate
from colav_interfaces.srv import EvaluateTransitions
from colav_interfaces.msg import TransitionResult

from config.qos_config import QOS_PROFILE
from scripts.guards import (
    guard_CRUISE_to_FB,
    guard_CRUISE_to_T2LOS,
    guard_CRUISE_to_T2Theta,
    guard_CRUISE_to_WAYPOINT_REACHED,
    guard_T2LOS_to_CRUISE,
    guard_T2LOS_to_FB,
    guard_T2Theta_to_FB,
    guard_T2Theta_to_T2LOS
)
from rclpy.executors import MultiThreadedExecutor
from colav_interfaces.msg import Waypoint, UnsafeSet


class HAGuardsNode(Node):
    _MODES = {  # dict showing the name of the control modes.
        1: "CRUISE",
        2: "T2LOS",
        3: "FB",
        4: "WAYPOINT_REACHED"
    }
    _GUARDS = {
        f"{_MODES[1]}_to_{_MODES[2]}": guard_CRUISE_to_T2LOS,
        f"{_MODES[1]}_to_{_MODES[4]}": guard_CRUISE_to_FB,
        f"{_MODES[1]}_to_{_MODES[5]}": guard_CRUISE_to_WAYPOINT_REACHED,
        f"{_MODES[2]}_to_{_MODES[1]}": guard_CRUISE_to_T2LOS,
        f"{_MODES[2]}_to_{_MODES[4]}": guard_T2LOS_to_FB,
    }

    def __init__(
        self,
        namespace:str = "hybrid_automaton",
        name:str = "guards"
    ):
        super().__init__(name, namespace=namespace)

        # Initialize the ThreadPoolExecutor
        self.executor = MultiThreadedExecutor()

        self._current_agent_state = AgentUpdate()
        self._current_obstacles_state = ObstaclesUpdate()
        self._current_waypoint = Waypoint()
        self._current_unsafe_set = UnsafeSet()

        # Initialisation functions
        self._NODE_SUBS = self._init_node_subs()
        self._NODE_SRVS = self._init_node_srvs()

    def _init_node_srvs(self):
        """initialize the nodes services"""
        try:
            return {
                "evalute_transitions": self.create_service(
                    srv_type=EvaluateTransitions,
                    srv_name="/hybrid_automaton/evaluate_transitions",
                    callback=self._evaluate_transitions
                )
            }
        except Exception as e:
            self.get_logger().error(f"{self.__class__}::init_node_srvs: Exception occured: {str(e)}")
            raise e
        
    def _evaluate_transitions(self, request: EvaluateTransitions.Request, response: EvaluateTransitions.Response):
        """evalute the transitions passed in"""
        try:
            if request.transition_names is not []:
                    guards_to_check = []
                    for transition in request._transition_names:
                        if transition not in self._GUARDS:
                            raise KeyError(f"Transition '{transition}' not found in _GUARDS dictionary")
                        guards_to_check.append(self._GUARDS[transition])

                    transition_results = []
    
                    for guard_to_check in guards_to_check:
                        
                        if guard_to_check is self._GUARDS[f"{self._MODES[1]}_to_{self._MODES[2]}"]:
                            """CRUISE to T2LOS"""
                            transition = guard_CRUISE_to_T2LOS(agent_state=self._current_agent_state , current_waypoint=self._current_waypoint , heading_error_tolerance=0.1, tolerance=1)
                            transition_results.append(
                                TransitionResult(
                                    transition_name= f"{self._MODES[1]}_to_{self._MODES[2]}",
                                    success = transition,
                                    message = "transition executed"
                                )
                            )

                        elif guard_to_check is self._GUARDS[f"{self._MODES[1]}_to_{self._MODES[3]}"]:
                            """CRUISE to T2Theta"""   
                            transition = guard_CRUISE_to_T2Theta(
                                agent_state=self._current_agent_state, 
                                obstacles_state=self._current_obstacles_state,
                                unsafe_set=self._current_unsafe_set,
                                waypoint=self._current_waypoint
                            )
                            transition_results.append(
                                TransitionResult(
                                    transition_name = f"{self._MODES[1]}_to_{self._MODES[4]}",
                                    success=transition,
                                    message="transition exeucted"
                                )
                            )

                        elif guard_to_check is self._GUARDS[f"{self._MODES[1]}_to_{self._MODES[4]}"]:
                            """CRUISE to FB"""
                            pass

                        elif guard_to_check is self._GUARDS[f"{self._MODES[1]}_to_{self._MODES[5]}"]:
                            """CRUISE to WAYPOINT_REACHED"""
                            pass

                        elif guard_to_check is self._GUARDS[f"{self._MODES[2]}_to_{self._MODES[1]}"]:
                            """T2LOS to CRUISE"""
                            pass

                        elif guard_to_check is self._GUARDS[f"{self._MODES[2]}_to_{self._MODES[4]}"]:
                            """T2LOS to FB"""
                            pass

                        elif guard_to_check is self._GUARDS[f"{self._MODES[3]}_to_{self._MODES[2]}"]:
                            """"""
                            pass
                        else:
                            print('GUARD EXCEPTION OCCURED')
                            raise RuntimeError('guard exception')
                        
                    response.overall_success = True
                    response.message = "Transitions have been evaluated"
                    response.results = transition_results
            else:
                response.overall_success = True
                response.message = "No transition names sent for evaluation"
        except Exception as e:
            self.get_logger(f"{self.__class__}::_evaluate_transitions: Exception occured: {str(e)}")
            response.overall_success = False
            response.message = str(e)
        
        return response

    def _init_node_subs(self):
        try:
            return {
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
        
    def _agent_update_callback(self, msg: AgentUpdate):
        pass

    def _obstacles_update(self, msg:ObstaclesUpdate):
        pass


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
