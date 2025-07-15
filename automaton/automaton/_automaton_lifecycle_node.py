
"""
ROS2 Hybrid Automaton node. performs lifecycle managements of the hybrid automaton 
starting and stopping the mode based on requests while managing control mode of the hybrid automaton
as defined within the hybrid_automaton_config.yml
Performs transitions resets and transition evaluations
"""

# from rclpy.lifecycle import Node, State, TransitionCallbackReturn
import rclpy
import os
from rclpy.executors import MultiThreadedExecutor
from rclpy.lifecycle import LifecycleNode, State, TransitionCallbackReturn
from automaton._internal.model.hybrid_automaton_model import HybridAutomaton
                                           
from automaton_interfaces.msg import AutomatonMode, AutomatonStatus
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from colav_interfaces.msg import Waypoint as ROSWaypoint, WaypointsState
from rclpy.action.server import ServerGoalHandle

from geometry_msgs.msg import Point
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.timer import Timer
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
import threading
from lifecycle_msgs.srv import ChangeState
from rclpy.guard_condition import GuardCondition

from automaton_interfaces.msg import AutomatonModeState 
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from automaton._internal.callbacks.dynamic_callbacks import dynamics_evaluation_callback
from automaton_interfaces.msg import AutomatonDynamicsEvaluation, AutomatonStatus, AutomatonTransitionEvaluations
from automaton_interfaces.msg import AutomatonInvariantsEvaluation
from automaton._internal.callbacks.invariant_callback import invariants_evaluation_callback
from automaton_interfaces.action import ExecuteMission
from automaton._internal.status_manager.status_fsm import StatusFSM


from rclpy.action import ActionServer, GoalResponse, CancelResponse
from automaton._internal.constants import QOS_PROFILE
import sys  

from automaton._internal.callbacks import (
    transition_evaluation_callback,
    on_mode_callback,
)
from automaton._internal.factory import (
    HybridAutomatonFactory
)

SYSTEM_CLOCK = None

class AutomatonLifecycleNode(LifecycleNode):
    """
    A Hybrid Automaton Node Managed Node which performs 
    executes dynamics, invariants transitions and so on
    based on hybrid automaton configuration.
    """

    _CONFIGURATION_PARAMS = {
        'famd_path': [
            "/path/to/famd.yml", 
            "absolute path to the hybrid automatons famd file."
        ]
    }

    # _ACTIVATION_PARAMS = {
    #     'waypoint_x': [
    #         0.0,
    #         "COLAV Hybrid Automaton State for goal waypoints 'x' position (m)."
    #     ], 
    #     'waypoint_y': [
    #         0.0,
    #         "COLAV Hybrid Automaton State for goal waypoints 'y' position (m)."
    #     ], 
    #     'waypoint_acceptance_radius': [
    #         10.0,
    #         "COLAV Hybrid Automaton State for goal waypoints 'acceptance radius' (m)."
    #     ]
    # }

    def __init__(
        self, 
        name: str,
    ):
        """init"""
        super().__init__(name)

        for param_key in self._CONFIGURATION_PARAMS:
            self.declare_parameter(
                param_key,
                value=self._CONFIGURATION_PARAMS[param_key][0],
                descriptor=ParameterDescriptor(
                    description=self._CONFIGURATION_PARAMS[param_key][1]
                )
            )

        self.get_logger().info(f"🤖 hybrid_automaton: managed node initialized")


    """ === LifeCycle Transition Functions === """

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """on configuration state initializes node attributes like subscribers and publishers"""
        self.get_logger().info(f"🔄 Node '{self.get_name()}' 📍 '{state.label}' ➡️ configure")

        try:
            famd_path = self.get_parameter('famd_path').value
            automaton_model:HybridAutomaton = HybridAutomatonFactory.hybrid_automaton_registry(
                automaton_famd_path=famd_path,
                generate_mmd_diagrams=True
            )
            automaton_model.create_state_publishers(self)
            automaton_model.create_state_subscriptions(self)

            self.automaton_model = automaton_model

            # # NOTE: should probably make status_publisher and mode publisher apart of the automaton_model
            self.mode_publisher = self.create_publisher(
                msg_type=AutomatonModeState,
                topic='/hybrid_automaton/mode_state',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self.status_publisher = self.create_publisher(
                msg_type=AutomatonStatus,
                topic='/hybrid_automaton/status',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )

            self.transitions_evaluation_publisher = self.create_publisher(
                msg_type=AutomatonTransitionEvaluations,
                topic='/hybrid_automaton/transitions_evaluation',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self.transitions_evaluation_timer:Timer = self.create_timer(
                timer_period_sec=1/self.automaton_model.transition_evaluation_frequency_hz, 
                callback=lambda: transition_evaluation_callback(
                    lock = threading.Lock(),
                    automaton_model=self.automaton_model,
                    stamp=self.get_clock().now().to_msg(),
                    mode_publisher=self.mode_publisher,
                    transition_evaluation_publisher=self.transitions_evaluation_publisher,
                    status_publisher=self.status_publisher
                ),
                callback_group=ReentrantCallbackGroup(),
                clock=SYSTEM_CLOCK,
                autostart=False
            )

            self.dynamics_evaluation_publisher: Publisher = self.create_publisher(
                msg_type=AutomatonDynamicsEvaluation,
                topic='/hybrid_automaton/dynamics_evaluation',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self.dynamic_evaluation_timer: Timer = self.create_timer(
                timer_period_sec=1 / self.automaton_model.control_frequency_hz,
                callback=lambda: dynamics_evaluation_callback(
                    lock=threading.Lock(),
                    automaton_model=self.automaton_model,
                    stamp=self.get_clock().now().to_msg(),
                    dynamics_evaluation_publisher=self.dynamics_evaluation_publisher,
                    status_publisher=self.status_publisher
                ),
                callback_group=ReentrantCallbackGroup(),
                clock=SYSTEM_CLOCK,
                autostart=False
            )

            self.invariants_evaluation_publisher: Publisher = self.create_publisher(
                msg_type=AutomatonInvariantsEvaluation,
                topic='/hybrid_automaton/invariants_evaluation',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self.invariants_evaluation_timer: Timer = self.create_timer(
                timer_period_sec=1/self.automaton_model.transition_evaluation_frequency_hz,
                callback=lambda: invariants_evaluation_callback(
                    lock=threading.Lock(),
                    automaton_model=self.automaton_model,
                    stamp=self.get_clock().now().to_msg(),
                    invariants_evaluation_publisher=self.invariants_evaluation_publisher,
                    status_publisher=self.status_publisher
                ),
                callback_group=ReentrantCallbackGroup(),
                autostart=False
            )

            self._goal_lock = threading.Lock()
            self.automaton_action_server = ActionServer(
                self,
                ExecuteMission,
                'execute_mission',
                execute_callback=self.execute_callback,
                goal_callback=self.goal_callback,
                handle_accepted_callback=self.handle_accepted_callback,
                cancel_callback=self.cancel_callback,
                callback_group=ReentrantCallbackGroup()
            )
        except Exception as e: 
            self.get_logger().error(f"unexpected exception occured during transition from '{state.label}' to 'configured': {str(e)}")
            return TransitionCallbackReturn.FAILURE
        
        self.get_logger().info(f"✅ Node '{self.get_name()}' configured!")
        return super().on_configure(state)

    def goal_callback(self, mission_request: ExecuteMission.Goal):
        """Accept or reject a client request to begin an action."""
        self.get_logger().info('Received goal request')

        goal_response = GoalResponse.ACCEPT
        try:
            if not isinstance(mission_request.goal_waypoint, ROSWaypoint ):
                self.get_logger().warning(f"invalid goal_waypoint type received.")
                goal_response = GoalResponse.REJECT

            if mission_request.goal_waypoint.acceptance_radius < 0.5:
                self.get_logger().warning(
                    f"Invalid goal waypoint received: each waypoint must have an acceptance radius greater than 0.5 meters. Received: {mission_request.goal_waypoint}"
                )
                goal_response = GoalResponse.REJECT
        except Exception as e:
            self.get_logger().error(f"exception occured during hybrid automaton request validation: '{str(e)}'")
            goal_response = GoalResponse.REJECT
        
        self.get_logger().info(f"Goal {goal_response.name.lower()}ed.")
        return goal_response

    def handle_accepted_callback(self, goal_handle: ServerGoalHandle):
        """handles valid accepted goals, cancels the current goal if their is a goal active
        if not then we just send the next goal."""
        with self._goal_lock:
            # This server only allows one goal at a time
            if self._goal_handle is not None and self._goal_handle.is_active:
                self.get_logger().info('Aborting previous goal')
                # Abort the existing goal
                self._goal_handle.abort()
            
            # validate hybrid automaton request
            req: HybridAutomaton.Goal = goal_handle._goal_request


            self._goal_handle = goal_handle

        goal_handle.execute()

    def execute_callback(self, goal_handle: ServerGoalHandle):
        """Execute the goal."""
        self.get_logger().info(f"Executing goal. Mission is to sequentially navigate to each of the goal waypoints: '{goal_handle._goal_request.goal_waypoints.waypoints}'")

        # Append the seeds for the Fibonacci sequence
        self._current_status = AutomatonStatus.INITIALIZING.name
        rate = self.create_rate(1.0, SYSTEM_CLOCK)
        rate.sleep()
        self._action_server_feedback_timer.reset()

        for idx, goal_waypoint in enumerate(goal_handle._goal_request.goal_waypoints.waypoints):
            self._waypoint_idx = idx
            self._current_goal_waypoint = goal_waypoint
            self._activate_automaton.trigger()
            
            self._mission_active = True
            
            rate = self.create_rate(frequency=10.0, clock=SYSTEM_CLOCK)
            
            while self._mission_active:
                rclpy.spin_once(self, timeout_sec=1.0)

        # # Start executing the action
        # for i in range(1, goal_handle.request.order):
        #     # If goal is flagged as no longer active (ie. another goal was accepted),
        #     # then stop executing
        #     if not goal_handle.is_active:
        #         self.get_logger().info('Goal aborted')
        #         return HybridAutomaton.Result()

        #     if goal_handle.is_cancel_requested:
        #         goal_handle.canceled()
        #         self.get_logger().info('Goal canceled')
        #         return HybridAutomaton.Result()

        #     # Update Fibonacci sequence
        #     feedback_msg.sequence.append(feedback_msg.sequence[i] + feedback_msg.sequence[i-1])

        #     self.get_logger().info('Publishing feedback: {0}'.format(feedback_msg.sequence))

        #     # Publish the feedback
        #     goal_handle.publish_feedback(feedback_msg)

        #     # Sleep for demonstration purposes
        #     time.sleep(1)

        # with self._goal_lock:
        #     if not goal_handle.is_active:
        #         self.get_logger().info('Goal aborted')
        #         return HybridAutomaton.Result()

        #     goal_handle.succeed()

        # Populate result message
        result = HybridAutomaton.Result()
        # result.sequence = feedback_msg.sequence

        self.get_logger().info('Returning result: {0}'.format(result.sequence))

        return result



    def cancel_callback(self, goal):
        """Accept or reject a client request to cancel an action."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """
        activates the hybrid automaton
        """
        self.get_logger().info(f"🔌 {self.get_name()}: {state.label} ➡️ activating")
        
        try:
            automaton_watchdog_fsm = StatusFSM(
                self.status_publisher,
                logger=self.get_logger()
            )
            # initialize transition trigger client
            goal_waypoint_params = {
                'waypoint_x': None,
                'waypoint_y': None,
                'waypoint_acceptance_radius': None
            }
            def get_param(param_name: str):
                param = self.get_parameter(param_name)
                if param.type_ == ParameterType.PARAMETER_NOT_SET: 
                    raise ValueError('parameter not given')
                return param
                
            for param_key in goal_waypoint_params.keys():
                goal_waypoint_params[param_key] = get_param(param_key).value

            # need to do some validation on the waypoint here, to ensure its not within distatce threshold 
            # of agent state

            # validate values are not None for goal waypoint if they are return errror
            self._goal_waypoint = ROSWaypoint(
                position=Point(x=goal_waypoint_params['waypoint_x'], y=goal_waypoint_params['waypoint_y']),
                acceptance_radius=goal_waypoint_params['waypoint_acceptance_radius']
            )

            self._trigger_lifecycle_transition_cli = self.create_client(ChangeState, f'/hybrid_automaton/change_state')
            while not self._trigger_lifecycle_transition_cli.wait_for_service(timeout_sec=1.0):
                self.get_logger().info("waiting for /hybrid_automaton/change_state")

            # initialize hybrid automaton topic publishers
            self._mode_publisher = self.create_publisher(
                AutomatonMode,
                '/hybrid_automaton/mode',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._invariant_publisher = self.create_publisher(
                AutomatonInvariantsEvaluation,
                '/hybrid_automaton/invariant',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._status_publisher = self.create_publisher(
                AutomatonStatus,
                '/hybrid_automaton/status',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._guard_evaluation_publisher = self.create_publisher(
                topic="/hybrid_automaton/guard_evaluations",
                msg_type=AutomatonTransitionEvaluations, # TODO: should rename this GuardsEvaluation to make it semantically correct
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._dynamics_publisher = self.create_publisher(
                msg_type=AutomatonDynamicsEvaluation,
                topic='/hybrid_automaton/dynamics',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._waypoints_publisher = self.create_publisher(
                msg_type=WaypointsState,
                topic='/hybrid_automaton/state/waypoints',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )

            self._guard_evaluation_subscriber = self.create_subscription(
                topic="/hybrid_automaton/guards_evaluation",
                msg_type=AutomatonDynamicsEvaluation,
                callback=lambda msg: transition_evaluation_callback(
                    lock=self._transition_eval_lock,
                    mode=self._mode,
                    states=self._states,
                    transition_config=self._mode_transitions,
                    status=self._status,
                    available_modes=self._MODE_ENUM_MAP,
                    transition_evaluation=msg,
                    mode_publisher=self._mode_publisher,
                    status_publisher=self._status_publisher,
                    waypoints_publisher=self._waypoints_publisher,
                    logger=self.get_logger()
                ),
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            # self._status_subscription = self.create_subscription( # TODO: CLOSE THIS IN DEACTIVATE
            #     msg_type=HybridAutomatonStatus,
            #     topic='/hybrid_automaton/status',
            #     callback=on_status_received_callback,
            #     qos_profile=QOS_PROFILE,
            #     callback_group=ReentrantCallbackGroup()
            # )

            # TODO: need to do transition evaluation next
            # TODO: Then do invariants
            # Should add script to move automaton to inactive mode to launch before starting mission manager.
            
            self._mode_subscription = self.create_subscription(
                AutomatonMode,
                '/hybrid_automaton/mode',
                callback=lambda msg: on_mode_callback(
                    lock=self._mode_callback_lock,
                    node=self,
                    available_modes=self._MODE_ENUM_MAP,
                    current_mode=self._mode,
                    mode=msg,
                    mode_configuration=self._configuration['modes'],
                    transition_configuration=self._configuration['transitions'],
                    dynamics_configuration=self._configuration['dynamics'],
                    invariants_configuration=self._configuration['invariants'],
                    reset_configuration=self._configuration['resets'],
                    guard_configuration=self._configuration['guards'],
                    status_publisher=self._status_publisher,
                    logger=self.get_logger()
                ),
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )

            # Todo: Remove this when ready.
            # self._invariant_subscription = self.create_subscription(
            #     Invariant,
            #     '/hybrid_automaton/invariant',
            #     qos_profile=QOS_PROFILE,
            #     callback=on_invariant_received_callback,
            #     callback_group=ReentrantCallbackGroup()
            # )

            self._invariant_timeout_guard_lock = threading.Lock()
            # self._trigger_invariant_timeout_guard:GuardCondition = self.create_guard_condition(
            #     handle_invariant_timeout_guard,
            #     callback_group=ReentrantCallbackGroup()
            # )

            self._waypoints_publisher.publish(WaypointsState(waypoints=[self._goal_waypoint]))
            self._mode_publisher.publish(AutomatonMode(type=self._configuration['initial_mode'], stamp=self.get_clock().now().to_msg())) # TODO: Need to add some validation to ensure init is given validly.
            
            # start timers
            # self._guards_evaluation_timer.reset()
            self._dynamics_timer.reset()
            # self._invariant_evaluation_timer.reset()
    
            for param_key in self._ACTIVATION_PARAMS:
                self.undeclare_parameter(param_key)

        except Exception as e:
            self.get_logger().error(f"unexpected exception occured during transition from '{state.label}' to 'activate': {str(e)}")
            return TransitionCallbackReturn.FAILURE

        self.get_logger().info(f"🚀 {self.get_name()}: activation complete!")
        return super().on_activate(state)
    
    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")

        try:
            # stop the timers.
            self._guards_evaluation_timer.cancel()
            self._dynamics_timer.cancel()
            self._invariant_evaluation_timer.cancel()

            # destory the subscriptions and publishers
            self.destroy_subscription(self._mode_publisher)
            self._mode_publisher: Publisher = None
            self.destroy_subscription(self._mode_subscription)
            self._mode_subscription: Subscription = None
            self.destroy_publisher(self._status_publisher)
            self._status_publisher: Publisher = None
            self.destroy_subscription(self._status_subscription)
            self._status_subscription:Subscription = None
            self.destroy_publisher(self._invariant_publisher)
            self._invariant_publisher: Publisher = None
            self.destroy_subscription(self._invariant_subscription)
            self._invariant_subscription:Subscription = None
            
            self._trigger_transition_cli = None
            self._trigger_transition_srv = None
            # Destroy publishers
            for pub_attr in [
                'mode_publisher',
                'status_publisher',
                'transition_pending_pub',
                'transition_eval_pub',
                'dynamics_pub'
            ]:
                if hasattr(self, pub_attr):
                    self.destroy_publisher(getattr(self, pub_attr))
                    self.__setattr__(pub_attr, None)

            # Destroy subscriptions
            for sub_attr in [
                'transition_sub',
                'transition_pending_sub',
                'status_sub'
            ]:
                if hasattr(self, sub_attr):
                    self.destroy_subscription(getattr(self, sub_attr))
                    self.__setattr__(sub_attr, None)

            # Clear goal waypoint state parameter
            if hasattr(self, 'goal_waypoint'):
                del self.goal_waypoint
        except Exception as e:
            self.get_logger().error(f"Exception occurred during deactivation: {e}")
            return TransitionCallbackReturn.FAILURE
    
        self.declare_parameter(
            'waypoint_x',
            value=ParameterType.PARAMETER_DOUBLE,
            descriptor=ParameterDescriptor(
                description="COLAV Hybrid Automaton State for goal waypoints 'x' position (m)."
            )
        )
        # TODO: IN CLEANUP REMOVE PARAM WAYPOINTS
        self.declare_parameter(
            'waypoint_y',
            value=ParameterType.PARAMETER_DOUBLE,
            descriptor=ParameterDescriptor(
                description="COLAV Hybrid Automaton State for goal waypoints 'y' Position (m)."
            )
        )
        self.declare_parameter(
            'waypoint_acceptance_radius',
            value=ParameterType.PARAMETER_DOUBLE,
            descriptor=ParameterDescriptor(
                description="COLAV Hybrid Automaton State for goal waypoints 'acceptance radius' (m)."
            )
        )
        return TransitionCallbackReturn.SUCCESS
    
    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        """Cleanup resources allocated during the 'configure' state."""
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'cleanup'")

        try:
            # Destroy timers
            if hasattr(self, '_guards_evaluation_timer'):
                self._guards_evaluation_timer.cancel()
                self.destroy_timer(self._guards_evaluation_timer)
                # self._transition_eval_timer:Timer = None

            if hasattr(self, '_dynamics_timer'):
                self._dynamics_timer.cancel()
                self.destroy_timer(self._dynamics_timer)
                # self._dynamics_timer:Timer = None

            if hasattr(self, '_invariant_timer'):
                self._invariant_timer.cancel()
                self.destroy_timer(self._invariant_timer)
                # self._invariant_timer:Timer = None

            # Remove other attributes
            for attr in [
                'automaton_active',
                'config_path',
                'eval_hz',
                'config',
                'automaton_modes',
                'goal_waypoint',
                'topic_io_callback_group'
            ]:
                if hasattr(self, attr):
                    delattr(self, attr)

            for param_key in self._CONFIGURATION_PARAMS:
                self.declare_parameter(
                    param_key,
                    value=self._CONFIGURATION_PARAMS[param_key][0],
                    descriptor=ParameterDescriptor(
                        description=self._CONFIGURATION_PARAMS[param_key][1]
                    )
                )
        except Exception as e:
            self.get_logger().error(f"Cleanup failed: {e}")
            return TransitionCallbackReturn.FAILURE
        
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")
        try:

            # Stop and destroy timers if still active
            if hasattr(self, '_transition_eval_timer'):
                self._guards_evaluation_timer.cancel()
                self.destroy_timer(self._guards_evaluation_timer)
                del self._guards_evaluation_timer

            if hasattr(self, '_dynamics_eval_timer'):
                self._dynamics_timer.cancel()
                self.destroy_timer(self._dynamics_timer)
                del self._dynamics_timer

            # Log and shut down node
            self.get_logger().info("Shutdown complete. Resources cleaned up.")
            self._exit_timer = self.create_timer(0.1, self._exit_after_shutdown)
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Exception occurred during shutdown: {e}")
            return TransitionCallbackReturn.FAILURE
        
    def _exit_after_shutdown(self):
        # Cancel timer so it runs only once
        self._exit_timer.cancel()
        self.destroy_timer(self._exit_timer)

        self.get_logger().info('Exiting node process cleanly after shutdown')

        rclpy.shutdown()
        sys.exit(0)

        
def main():
    rclpy.init()
   
    automaton_node = AutomatonLifecycleNode(name='hybrid_automaton')
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())

    try:
        executor.add_node(automaton_node)
        executor.spin()
    except Exception as e:
        executor.shutdown()
        automaton_node.destroy_node()
        
    if rclpy.ok():
        rclpy.shutdown()

if __name__ == '__main__':
    main()