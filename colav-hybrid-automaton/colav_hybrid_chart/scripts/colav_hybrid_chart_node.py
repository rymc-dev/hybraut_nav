import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult, ParameterType
import os
import sys

# Add two directories back to sys.path: necessary for local debugging when the package isn't built with colcon,
# allowing imports to work correctly without relying on the build process.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, ControllerFeedback, Dynamics, DynamicsUpdate

from colav_interfaces.srv import StartHybridAutomaton
from std_srvs.srv import Trigger
from colav_hybrid_chart.config.qos_config import QOS_PROFILE
from colav_hybrid_chart.utils.node_utils import create_cli
from utils.ros_timer_utils import get_current_ros_time
from colav_interfaces.msg import GuardsStatus, Waypoints, Waypoint, ControllerFeedback
from std_msgs.msg import String

class InitializationError(Exception):
    """Custom exception for initialization-related failures."""
    def __init__(self, component: str, message: str):
        super().__init__(f"[{component}] {message}")
        self.component = component
        self.message = message

class HAChart(Node):
    """
    This class implements a hybrid automaton chart for the COLAV project.
    It manages different modes of operation of the system, including transitions
    between modes based on guard conditions. The hybrid automaton is defined as:
        HA: (Q, X, F, Init, Inv, E, G, R)
    
    Where:
        Q: set of modes
        X: set of continuous states
        F: Dynamics (control policies for each mode)
        Init: Initial discrete and continuous states
        Inv: Invariants of the system
        E: set of transitions
        G: guard conditions
        R: reset conditions
    """

    # Define control modes with unique keys
    _MODES = {
        1: "cruise",
        2: "t2los",
        3: "fb",
        4: "waypoint_reached"
    }

    # Initial states of the automaton (discrete and continuous)
    _INIT_STATES = {
        "discrete": _MODES[1],
        "continuous": {
            "agent": AgentUpdate(),
            "obstacles": ObstaclesUpdate(),
            "waypoints": [],
            "unsafe_set": UnsafeSet()
        }
    }

    # Current states (continuous)
    _STATES = {
        "agent": AgentUpdate(),
        "obstacles": ObstaclesUpdate(),
        "waypoints": [],
        "unsafe_set": UnsafeSet()
    }

    # Transitions for each mode along with their priorities
    _TRANSITIONS = {
        _MODES[1]: {  # CRUISE
            f"{_MODES[1]}_to_{_MODES[2]}_1": 3,  # CRUISE to T2LOS (priority 3)
            f"{_MODES[1]}_to_{_MODES[2]}_2": 4,  # CRUISE to T2LOS (priority 4)
            f"{_MODES[1]}_to_{_MODES[3]}": 1,      # CRUISE to FALLBACK (priority 1)
            f"{_MODES[1]}_to_{_MODES[4]}": 2,      # CRUISE to WAYPOINT_REACHED (priority 2)
        },
        _MODES[2]: {  # T2LOS
            f"{_MODES[2]}_to_{_MODES[3]}": 1,      # T2LOS to FALLBACK (priority 1)
            f"{_MODES[2]}_to_{_MODES[1]}": 3,      # T2LOS to CRUISE (priority 3)
            f"{_MODES[2]}_to_{_MODES[4]}": 2,      # T2LOS to WAYPOINT_REACHED (priority 2)
        },
        _MODES[3]: [  # FALLBACK
            # Define fallback transitions if required
        ],
        _MODES[4]: {  # WAYPOINT_REACHED
            f"{_MODES[4]}_to_{_MODES[1]}": 1       # WAYPOINT_REACHED to CRUISE (priority 1)
        }
    }

    # Define transitions with reset conditions
    _RESETS = {
        _MODES[1]: [  # CRUISE 
            f"{_MODES[1]}_to_{_MODES[2]}1"
        ],
        _MODES[4]: [  # WAYPOINT_REACHED
            f"{_MODES[4]}_to_{_MODES[1]}"
        ]
    }

    _INVARIANTS = {}

    def __init__(self, namespace: str = "hybrid_automaton", name: str = "chart"):
        """
        Initialize the COLAV Hybrid Automaton Chart node.
        """
        super().__init__(name, namespace=namespace)
        self._NODE_SUBS = self._init_node_subs()
        self._NODE_CLIS = self._init_ha_clis()
        self._current_dynamics = None
        # Create services to start and stop the hybrid automaton.
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
        self.get_logger().info(f"{namespace}/{name} node initialised!")

    def _start_hybrid_automaton_callback(self, request: StartHybridAutomaton.Request,
                                           response: StartHybridAutomaton.Response) -> StartHybridAutomaton.Response:
        """
        Callback to start the hybrid automaton.
        """
        try:
            self.get_logger().info(f"/start_hybrid_automaton service called with request at time: secs: {request.stamp.sec}, nanosecs: {request.stamp.nanosec} with goal_waypoint of: {request.goal_waypoint}")
            self._ha_pubs = self._init_ha_pubs()  # Initialize controller feedback publisher
            self._init_ha(request)

            # Start hybrid_automaton_eval processes required by this chart                  
            # start the guards_evaluation
            future = self._NODE_CLIS["start_guards_evaluation"].call_async(Trigger.Request())
            future_response = future.result()
            # Blocking until service responds:
            # if not response.success: # TODO: NEED TO FIGURE OUT WHY THE FUTURE CLI IS NOT RECEIVING A RESPONSE
            #     raise Exception(f'Failed to start guards_evaluation: reason: {response.message}')

            # start the dynamics evluation
            future = self._NODE_CLIS["start_dynamics_evaluation"].call_async(Trigger.Request())
            future_response = future.result()
            
            self._dynamics_sub = self.create_subscription(
                msg_type=DynamicsUpdate,
                topic="/hybrid_automaton/dynamics",
                callback=self._dynamics_callback,
                qos_profile=QOS_PROFILE
            )

            # Start a timer to evaluate transitions periodically
            self._transition_eval_timer = self.create_timer(
                0.1,  # This timer period might later be parameterized.
                self._evaluate_transitions
            )
            self._guards_status = None

            response.success = True
            response.message = "Hybrid Automaton started successfully"
        except Exception as e:
            self.get_logger().warning(f"Error in starting hybrid automaton: {str(e)}")
            response.success = False
            response.message = str(e)
        return response

    def _dynamics_callback(self, msg: DynamicsUpdate):
        self._current_dynamics = msg

    def _init_ha_clis(self) -> dict:
        """
        Creates hybrid automaton-specific service clients.
        """
        try:
            return {
                "start_guards_evaluation": create_cli(
                    node=self,
                    srv_type=Trigger,
                    srv_name='/hybrid_automaton/guards_node/start_guard_evaluation'
                ),
                "stop_guards_evaluation": create_cli(
                    node=self,
                    srv_type=Trigger,
                    srv_name='/hybrid_automaton/guards_node/stop_guards_evaluation'
                ),
                "start_dynamics_evaluation": create_cli(
                    node=self,
                    srv_type=Trigger,
                    srv_name="/hybrid_automaton/dynamics_node/start_dynamics_evaluation"
                ),
                "stop_dynamics_evaluation":create_cli(
                    node=self,
                    srv_type=Trigger,
                    srv_name="/hybrid_automaton/dynamics_node/stop_dynamics_evaluation"
                )
            }
        except Exception as e:
            self.get_logger().error(f"Error occurred in client initialization: {str(e)}")
            raise e

    def _init_ha_pubs(self):
        """
        Initializes the publisher for controller feedback on the '/controller_feedback' topic.
        """
        try:
            return { 
                'controller_feedback': self.create_publisher(
                    ControllerFeedback,
                    '/hybrid_automaton/controller_feedback',
                    qos_profile=QOS_PROFILE
                ),
                'mode': self.create_publisher(
                    String,
                    '/hybrid_automaton/mode',
                    qos_profile=QOS_PROFILE
                ),
                'waypoints': self.create_publisher(
                    Waypoints,
                    '/hybrid_automaton/waypoints',
                    qos_profile=QOS_PROFILE
                )
            }
        except Exception as e:
            raise INi

    def _init_ha(self, request: StartHybridAutomaton.Request):
        """
        Initializes the hybrid automaton chart by setting the initial states.
        """
        # Ensure that key continuous states are not None
        if (self._STATES["agent"] is None or
                self._STATES["obstacles"] is None or
                self._STATES["unsafe_set"] is None):
            raise ValueError("Initial states cannot be None")
        
        # TODO: Validate that the timestamp for the request is within tolerance

        # TODO: Validate the timestamp for STATES is within tolerance.

        # TODO: Validate that mission_request.goal_waypoint is provided.

        self._CURRENT_MODE = self._INIT_STATES['discrete']
        # Update the continuous part of the initial state
        self._INIT_STATES["continuous"]["agent"] = self._STATES["agent"]
        self._INIT_STATES["continuous"]["obstacles"] = self._STATES["obstacles"]
        self._INIT_STATES["continuous"]["unsafe_set"] = self._STATES["unsafe_set"]
        self._INIT_STATES["continuous"]["waypoints"] = [request.goal_waypoint]

    def _evaluate_transitions(self):
        """
        Evaluates transitions between different modes based on guard conditions.
        """
        # Prepare request for evaluating transitions
        
        self._ha_pubs['mode'].publish(String(data=str(self._CURRENT_MODE).upper()))
        self._ha_pubs['waypoints'].publish(Waypoints(waypoints=self._STATES['waypoints']))

        try:
            if self._guards_status is not None:
                guards_to_check = self._guards_status.guard_names
                guard_results = {}
                for guard_name in guards_to_check:
                    if hasattr(self._guards_status, guard_name):
                        value = getattr(self._guards_status, guard_name)
                        guard_results[guard_name] = value
                    else:
                        self.get_logger().warn(f'Guard name: "{guard_name}" not found in guard_status fields ')
                active_guard = None
                priority = -1
                for guard, status in guard_results.items():
                    if self._TRANSITIONS[self._CURRENT_MODE][guard] < priority or priority == -1:
                        if status == True: # Means that the guard is active
                            priority = self._TRANSITIONS[self._CURRENT_MODE][guard]
                            active_guard = guard

                # make transition based on active guard
                if active_guard is not None:
                    # TODO: first check if there is a reset for this guar
                    new_control_mode = active_guard.split('_')[2] # Get transition to item from guard name
                    self._CURRENT_MODE = new_control_mode  
                    # If no reset condition for this guard then change control mode based on the transition
                from std_msgs.msg import Header
                from builtin_interfaces.msg import Time
                from colav_interfaces.msg import CmdVelYaw, ControlMode, ControlStatus
                # need to now publish the latest dynamic updates!!!!!!
                controller_feedback = ControllerFeedback(
                    header=Header(stamp=get_current_ros_time()),
                    mission_tag="mission", #TODO: Need to retrieve this from colav_params
                    agent_tag='agent', # TODO: Need to retrive this from colav_params
                    cmd=CmdVelYaw(velocity= self._current_dynamics.dynamics.velocity,yaw_rate=self._current_dynamics.dynamics.yaw_rate),
                    mode=ControlMode(type= next((k for k, v in self._MODES.items() if v == self._CURRENT_MODE), None)),
                    status=ControlStatus(type=1)
                )
                self._ha_pubs['controller_feedback'].publish(controller_feedback)

        except Exception as e:
            self.get_logger().error(f'Error occured: {str(e)}')


        # request = EvaluateTransitions.Request()
        # request.transition_names = [transition[0] for transition in self._TRANSITIONS[self._CURRENT_MODE]]
        # cli = self._NODE_CLIS['evaluate_transitions']
        # future = cli.call_async(request)
        # future.add_done_callback(self._transition_evaluation_callback)

    def _transition_evaluation_callback(self, future):
        """
        Callback function for evaluating mode transitions based on guard conditions.

        This function is triggered when the asynchronous transition evaluation completes.
        It processes the `future` response containing the result of guard evaluations for
        possible transitions from the current control mode.

        If the evaluation is successful:
        - It filters out the transitions with successful guard conditions.
        - Among the valid transitions, it selects the one with the highest priority (lowest numeric value).
        - Logs the name of the active transition.
        - (TODO) Executes any necessary reset or update actions and updates the `_CURRENT_MODE`.

        If the evaluation fails (`overall_success` is False), it raises a `RuntimeError`.

        Args:
            future (concurrent.futures.Future): A future object containing the result of the transition evaluation,
                                                which is expected to have an `overall_success` flag,
                                                a `results` list of evaluated transitions,
                                                and a `message` describing any failure.

        Raises:
            RuntimeError: If the evaluation response indicates failure.
            Exception: For any unexpected error encountered during processing.
        """

        try:
            response = future.result()
            if response.overall_success:
                # Filter active transitions (those with a successful guard evaluation)
                active_transitions = [t for t in response.results if t.success]
                if active_transitions:
                    # Determine the transition with the highest priority (lowest numerical value)
                    def get_priority(transition_name):
                        for trans, priority in self._TRANSITIONS[self._CURRENT_MODE]:
                            if trans == transition_name:
                                return priority
                        return float('inf')

                    active_transition = min(active_transitions, key=lambda t: get_priority(t.transition_name))
                    self.get_logger().info(f"Active transition: {active_transition.transition_name}")

                    # TODO: Execute any reset/update actions,
                    # and update the _CURRENT_MODE based on the chosen transition.
                    pass
                else:
                    # No transition was activated: execute dynamics for the current mode.
                    pass
            else:
                raise RuntimeError(f"Transition evaluation failed: {response.message}")
        except Exception as e:
            self.get_logger().error(str(e))
            raise e

    def _stop_hybrid_automaton_callback(self, request: Trigger.Request,
                                          response: Trigger.Response) -> Trigger.Response:
        """
        Placeholder for stopping the hybrid automaton.
        """
        # TODO: Add logic to gracefully stop the automaton.
        response.success = True
        response.message = "Stop function not implemented yet"
        return response

    def _init_node_subs(self) -> dict:
        """
        Initializes subscriptions
        - Initializes the subscriptions for the required for the hybrid automaton chart
        
        :raises: (InitializationError) if exception occurs
        """
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
                    topic='/unsafe_set',
                    callback=lambda msg: self._STATES.__setitem__("unsafe_set", msg),
                    qos_profile=QOS_PROFILE
                ),
                "guards_status_update": self.create_subscription(
                    msg_type=GuardsStatus,
                    topic='/hybrid_automaton/guards_status',
                    callback=lambda msg: setattr(self, '_guards_status', msg),
                    qos_profile=QOS_PROFILE
                )
            }
        except Exception as e:
            raise InitializationError('Subscriptions', f'error occured initializing subscriptions: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = HAChart()
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
