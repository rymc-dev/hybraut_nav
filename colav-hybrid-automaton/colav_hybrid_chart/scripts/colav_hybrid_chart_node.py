import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult, ParameterType
import os
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, ControllerFeedback
from colav_interfaces.srv import StartHybridAutomaton
from std_srvs.srv import Trigger
from colav_hybrid_chart.config.qos_config import QOS_PROFILE
from colav_interfaces.srv import EvaluateTransitions
from colav_hybrid_chart.utils.node_utils import create_cli

class HAChart(Node):
    """
        This class implements a hybrid automaton chart for the COLAV project.
        It is responsible for managing the different modes of operation of the system,
        including the transitions between these modes based on guard conditions.
        The chart is designed to handle various control policies and behaviors
        for the system while in each mode.

        formal definition of the hybrid automaton chart: 
            HA: (Q, X, F, Init, Inv, E, G, R)

            where: 
                Q: set of modes
                X: set of continuous states
                F: Dynamics of the system (mode behavior/control policies)
                Init: Initial state of the system (discrete state (chart initial control mode) and continuous state (environment))
                Inv: Invariants of the system (
                E: set of transitions
                G: guard conditions
                R: reset conditions
    """

    """
    _MODES: This dict stores the key-values for control modes for the hybrid automaton
            the numbers associated with the names of the actual control modes.
    """
    _MODES = {  # dict showing the name of the control modes.
        1: "CRUISE",
        2: "T2LOS",
        4: "FB",
        4: "WAYPOINT_REACHED"
    }

    """
    _INIT_STATES: This dict stores the initial discrete and continuous states from when the hybrid automaton 
                  is started
    """
    _INIT_STATES = {  # Corrected assignment with '='
        "discrete": _MODES[1],  # Discrete state is the initial control mode
        "continuous": { # Continuous state space is defined as agent, obstacles, unsafe set and waypoints
            "agent": AgentUpdate(), # agent will have initial agent passed in.
            "obstacles": ObstaclesUpdate(), # obstacles will have initial obstacles passed in
            "waypoints": [], # waypoints will have initial goal waypoint appended on init.
            "unsafe_set": UnsafeSet() # unsafe set will have initial unsafe set passed in 
        }
    }

    """
    _STATES: This dict stores the continuous states
    """
    _STATES = {
        "agent": AgentUpdate(),
        "obstacles": ObstaclesUpdate(),
        "waypoints": [],
        "unsafe_set": UnsafeSet()
    }

    """
    _TRANSITIONS: This dict shows the transitions associated with the hybrid automatons
                  different control modes
    """
    _TRANSITIONS = {
        _MODES[1]: [ # 1. CRUISE
            (f"{_MODES[1]}_to_{_MODES[2]}_1", 3), # T2LOS: guard/reset: PRIORITY = 4
            (f"{_MODES[1]}_to_{_MODES[2]}_2", 4), # T2LOS: gurad PRIORITY = 4
            (f"{_MODES[1]}_to_{_MODES[3]}", 1), # FALLBACK: PRIORITY = 1
            (f"{_MODES[1]}_to_{_MODES[4]}", 2), # WAYPOINT_REACHED: PRIORITY = 2
        ],
        _MODES[2]: [ # 2: T2LOS
            (f"{_MODES[3]}_to_{_MODES[4]}", 1), # FALLBACK: PRIORITY = 1
            (f"{_MODES[3]}_to_{_MODES[1]}", 3), # CRUISE: PRIORITY = 3
            (f"{_MODES[3]}_to_{_MODES[5]}", 2), # WAYPOINT_REACHED: PRIORITY = 5
        ],
        _MODES[3]: [ # 3: FB
        ],
        _MODES[4]: [ # 4: WAYPOINT_REACHED
            (f"{_MODES[5]}_to_{_MODES[1]}", 1) # CRUISE: PRIORITY = 1 
        ]
    }

    _RESETS = { # dict showing the name of the transitions which have reset conditions
        # _TRANSITIONS[_MODES[5]]: "test"
    }

    _INVARIANTS = {
    }

    def __init__(
        self,
        namespace:str = "hybrid_automaton",
        name:str = "chart"
    ):
        """
        colav_hybrid_chart init
        """
        super().__init__(name, namespace=namespace)
        self._NODE_SUBS = self._init_node_subs()
        # Initialisation functions
        self.create_service(
            StartHybridAutomaton,
            '/hybrid_automaton/start',
            self._start_hybrid_automaton_callback
        )
        self.create_service(
            Trigger,
            '/hybrid_automaton/stop',
            self._stop_hybrid_automaton_callback
        )

    def _start_hybrid_automaton_callback(self, request:StartHybridAutomaton.Request, response:StartHybridAutomaton.Response):
        try:
            # Initialize the hybrid automaton chart init states
            self.get_logger().info(f"/start_hybrid_automaton service called with request: {request}")
            self._NODE_CLIS = self._init_ha_clis()
            self._init_controller_feedback_pub() # Initialize the controller feedback publisher
            self._init_ha(request) # Initialize the hybrid automaton chart
            
            self._transition_eval_timer = self.create_timer(
                1.0, # TODO: Need to make this a parameter received from colav_params_server
                self._evaluate_transitions
            )
            response.success = True
            response.message = "Hybrid Automaton started successfully"
        except Exception as e:
            self.get_logger().warning(f'Error in starting hybrid automaton: {str(e)}')
            response.success = False
            response.message = str(e) 

        return response
    
    def _init_ha_clis(self):
        """creates hybrid automaton specific clients."""
        try:
            return {
                "evalute_transitions": create_cli(node=self, srv_type=EvaluateTransitions, srv_name='/hybrid_automaton/evaluate_transitions')
            }
        except Exception as e:
            self.get_logger().error(f"error occured: {str(e)}")
            raise e

    def _init_controller_feedback_pub(self):
        """
            This function initializes the publisher for controller feedback.
            It creates a publisher that will publish messages to the '/controller_feedback' topic.
        """
        try:
            return self.create_publisher(
                ControllerFeedback,
                '/controller_feedback',
                qos_profile=QOS_PROFILE
            )
        except Exception as e: 
            self.get_logger().error(f"Error in initializing controller feedback publisher: {str(e)}")
            raise e

    def _init_ha(self, request:StartHybridAutomaton.Request):
        """
            This function initializes the hybrid automaton chart.
            It sets the initial states and prepares the system for operation.
        """
        if self._STATES["agent"] is None or \
            self._STATES["obstacles"] is None or \
            self._STATES["unsafe_set"] is None:
            raise ValueError("Initial states cannot be None")
        
        # TODO: Got to validate the timestamp for STATES is within tolerance

        # TODO: Validate that the request mission_request.goal_waypoints is not empty and has at least one waypoint!!!!!
        self._CURRENT_MODE = self._INIT_STATES['discrete']
        self._INIT_STATES["continuous"]["agent"] = self._STATES["agent"]
        self._INIT_STATES["continuous"]["obstacles"] = self._STATES["obstacles"]
        self._INIT_STATES["continuous"]["unsafe_set"] = self._STATES["unsafe_set"]
        self._INIT_STATES["continuous"]["waypoints"] = [request.mission_request.goal_waypoint]
    
    def _evaluate_transitions(self):
        """
            This function evaluates the transitions between the different modes of operation
            based on the guard conditions defined in the hybrid automaton chart.
        """
        # Evaluate transitions
        request = EvaluateTransitions.Request()
        request.transition_names = [transition[0] for transition in self._TRANSITIONS[self._CURRENT_MODE]]
        future = self._NODE_CLIS['evalute_transitions'].call_async(request)
        future.add_done_callback(self._transition_evaluation_callback)
        # if transition results all return no transition
            # Call the Dynamics controller for this mode and publish to controller feedback topic
        # else 
            # Transition to next control mode based on priority
            # Make init dynamics request
            # publish new dynamics to controller feedback
    def _transition_evaluation_callback(self, future):
        try: # create callback group based on future.messages, call all the guard functions asyncronously and return results in response.
            response = future.result()
            if response.overall_success:
                # Iterate through 
                active_transitions = []
                for transition in response.results:
                    if transition.success:
                        active_transitions.append(transition)
                
                active_transition_priority = -1
                active_transition = None
                for op_active_transition in active_transitions:
                    if active_transition_priority == -1:
                        active_transition = op_active_transition
                        active_transition_priority = self._TRANSITIONS[active_transition['transition_name'][1]]
                    if self._TRANSITIONS[active_transition['transition_name']][1] < active_transition_priority:
                        active_transition = op_active_transition
                        active_transition_priority = self._TRANSITIONS[active_transition['transition_name']][1]

                # MOVE TO NEW CONTROL MODE
                pass
                # self._CURRENT_MODE = 
            else:
                raise RuntimeError(f"transition evaluation failed: {response.message}")
        except Exception as e:
            self.get_logger().error(str(e))
            raise e


    def _stop_hybrid_automaton_callback(self, request:Trigger.Request, response:Trigger.Response):
        pass

    def _init_node_subs(self):
        try:
            return {
                "agent_update": self.create_subscription(
                    msg_type=AgentUpdate,
                    topic='/agent_update',
                    callback=lambda msg: self._STATES.__setitem__("agent", msg),
                    qos_profile=QOS_PROFILE
                ),
                "obstacles_update": self.create_subscription(
                    msg_type=ObstaclesUpdate,
                    topic='/obstacles_update',
                    callback=lambda msg: self._STATES.__setitem__("obstacles", msg),
                    qos_profile=QOS_PROFILE
                ),
                "unsafe_set_update": self.create_subscription(
                    msg_type=UnsafeSet,
                    topic='/unsafe_set_update',
                    callback=lambda msg: self._STATES.__setitem__("unsafe_set", msg),
                    qos_profile=QOS_PROFILE
                )
            }
        except Exception as e:
            self.get_logger().error(str(e))
            raise e

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = HAChart()
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
