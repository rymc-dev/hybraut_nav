
"""
ROS2 Hybrid Automaton node. performs lifecycle managements of the hybrid automaton 
starting and stopping the mode based on requests while managing control mode of the hybrid automaton
as defined within the hybrid_automaton_config.yml
Performs transitions resets and transition evaluations
"""

# from rclpy.lifecycle import Node, State, TransitionCallbackReturn
import rclpy
import os
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.lifecycle import LifecycleNode, State, TransitionCallbackReturn
from std_msgs.msg import String, Bool
                                           
from hybrid_automaton_interfaces.msg import Transition as COLAVTransition, Dynamics
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from colav_hybrid_automaton.automaton.utils import load_yml
from colav_hybrid_automaton.automaton.factory import (
    create_hybrid_automaton_config,
    create_state_subscriptions,
    create_state_publishers
)
from colav_interfaces.msg import Waypoint, Waypoints
from geometry_msgs.msg import Point
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.timer import Timer
from rclpy.publisher import Publisher
from typing import List, Optional
from rclpy.subscription import Subscription
from rclpy.client import Client
import threading
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState
from rclpy.guard_condition import GuardCondition
from functools import partial

from colav_hybrid_automaton.automaton.constants import (
    QOS_PROFILE, 
    HybridAutomatonStatus
)

from colav_hybrid_automaton.automaton.callbacks import (
    evaluate_transitions_timer_callback,
    evaluate_dynamics_timer_callback,
    evaluate_invariants_timer_callback,
    on_invariant_status_received,
    on_mode_callback,
    on_status_received_callback,
    handle_invariant_timeout_guard
)

SYSTEM_CLOCK = None

class HybridAutomatonNode(LifecycleNode):
    """
    A Hybrid Automaton Node Managed Node which performs 
    executes dynamics, invariants transitions and so on
    based on hybrid automaton configuration.
    """

    _CONFIGURATION_PARAMS = {
        'configuration_path': [
            "", 
            "Absolute path to the Hybrid Automaton configuration file (.yml format)."
        ], 
        'evaluation_frequency': [ 
            100,
            "Frequency (in Hz) at which transition conditions are evaluated."
        ],
        'control_frequency': [
            100,
            "Frequency (in Hz) at which controller feedback is returned."
        ]
    }

    _ACTIVATION_PARAMS = {
        'waypoint_x': [
            0.0,
            "COLAV Hybrid Automaton State for goal waypoints 'x' position (m)."
        ], 
        'waypoint_y': [
            0.0,
            "COLAV Hybrid Automaton State for goal waypoints 'y' position (m)."
        ], 
        'waypoint_acceptance_radius': [
            10.0,
            "COLAV Hybrid Automaton State for goal waypoints 'acceptance radius' (m)."
        ]
    }
            
    def __init__(
        self, 
        name: str, 
        namespace: Optional[str]
    ):
        """init"""
        super().__init__(name, namespace=namespace)

        # Internal states
        self._mode:str = ""
        self._states:dict = None
        self._mode_dynamics = None
        self._mode_invariant = None 
        self._mode_transitions = None
        self._status:HybridAutomatonStatus = None
        self._invariant:bool = None
        self._current_transition_evaluation:Transition = None
        self._reset_event = None
        self._waiting_after_reset:bool = False
        self._reset_complete_time = None
        self._current_invariant_status = None

        # locks
        self.transition_lock = threading.Lock()
        self.error_lock = threading.Lock()
        self.executing_mode_lock = threading.Lock()
        self.completed_lock = threading.Lock()
        self._mode_callback_lock = threading.Lock()

        # Publishers
        self._mode_publisher:Publisher = None
        self._invariant_publisher: Publisher = None
        self._status_publisher:Publisher = None
        self._transition_evaluation_publisher:Publisher = None
        self._dynamics_publisher:Publisher = None
        self._waypoints_publisher: Publisher = None

        # Subscriptions
        self._transition_subscription:Subscription = None
        self._transition_evaluation_subscriber:Subscription = None
        self._mode_subscription:Subscription = None
        self._status_subscription:Subscription = None

        # clients: 
        self._trigger_lifecycle_transition:Client = None

        # Timers
        self._transition_evaluation_timer:Timer = None
        self._dynamics_timer:Timer = None
        self._invariant_timer:Timer = None

        # Internal Continuous states
        self._goal_waypoint:Waypoint = None

        self._available_modes:List[str] = None
        self._configuration: dict = None

        self._control_frequency:int = 100
        self._evaluation_frequency:int = 100

        self._transition_eval_lock = threading.Lock()
        self._dynamics_timer_callback_lock = threading.Lock()
        self._invariant_evaluation_lock = threading.Lock()

        for param_key in self._CONFIGURATION_PARAMS:
            self.declare_parameter(
                param_key,
                value=self._CONFIGURATION_PARAMS[param_key][0],
                descriptor=ParameterDescriptor(
                    description=self._CONFIGURATION_PARAMS[param_key][1]
                )
            )

        self.get_logger().info(f"{namespace}/{name}: managed node initialized")


    """ === LifeCycle Transition Functions === """

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """on configuration state initializes node attributes like subscribers and publishers"""
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'")

        try:
            # retrieve configuration params
            _configuration_file_path = self.get_parameter('configuration_path').value
            _evaluation_frequency= self.get_parameter('evaluation_frequency').value
            _control_frequency = self.get_parameter('control_frequency').value

            # configure the hybrid automaton

            if _evaluation_frequency > 100:
                raise ValueError("evalaution frequency is too high, can't be over 100 hz")
            
            if _control_frequency > 100: 
                raise ValueError("control frequency too high, can't be over 100 hz")
            
            self._evaluation_frequency = _evaluation_frequency
            self._control_frequency = _control_frequency
            self._configuration = create_hybrid_automaton_config(
                config=load_yml(
                    yml_path=_configuration_file_path
            ))
            self._states = create_state_subscriptions(node=self, state_configuration=self._configuration['states'])
            
            self._available_modes = list(self._configuration['modes'].keys())

            self._transition_evaluation_timer = self.create_timer(
                timer_period_sec=1/self._evaluation_frequency, 
                callback=lambda: evaluate_transitions_timer_callback(
                    lock= self._transition_eval_lock,
                    mode = self._mode,
                    available_modes = self._available_modes,
                    status = self._status,
                    states=self._states,
                    stamp = self.get_clock().now().to_msg(),
                    mode_transitions = self._mode_transitions,
                    status_publisher = self._status_publisher,
                    transiiton_evaluation_publisher = self._transition_evaluation_publisher,
                    logger = self.get_logger()
                ),
                callback_group=ReentrantCallbackGroup(),
                clock=SYSTEM_CLOCK,
                autostart=False
            )

            self._dynamics_timer = self.create_timer(
                timer_period_sec=1 / self._control_frequency,
                callback=lambda: evaluate_dynamics_timer_callback(
                    lock=self._dynamics_timer_callback_lock,
                    mode=self._mode,
                    available_modes=self._available_modes,
                    mode_dynamics=self._mode_dynamics,
                    states=self._states,
                    stamp=self.get_clock().now().to_msg(),
                    dynamic_publisher=self._dynamics_publisher,
                    logger=self.get_logger()
                ),
                callback_group=ReentrantCallbackGroup(),
                clock=SYSTEM_CLOCK,
                autostart=False
            )

            self._invariant_evaluation_timer = self.create_timer(
                timer_period_sec=1/self._evaluation_frequency,
                callback=evaluate_invariants_timer_callback,
                callback_group=ReentrantCallbackGroup(),
                autostart=False
            )

            # undeclare params from configuration mode
            for param_key in self._CONFIGURATION_PARAMS:
                self.undeclare_parameter(param_key)

            # declare params for activation mode
            for param_key in self._ACTIVATION_PARAMS:
                self.declare_parameter(
                    param_key,
                    value=self._ACTIVATION_PARAMS[param_key][0],
                    descriptor=ParameterDescriptor(
                        description = self._ACTIVATION_PARAMS[param_key][1]
                    )
                )
        except Exception as e: 
            self.get_logger().error(f"Configuration failed: {e}")
            return TransitionCallbackReturn.FAILURE
        
        return super().on_configure(state)

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """
        activates the hybrid automaton
        """
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")

        try:
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

            # validate values are not None for goal waypoint if they are return errror
            self._goal_waypoint = Waypoint(
                position=Point(x=goal_waypoint_params['waypoint_x'], y=goal_waypoint_params['waypoint_y']),
                acceptance_radius=goal_waypoint_params['waypoint_acceptance_radius']
            )

            self._trigger_lifecycle_transition_cli = self.create_client(ChangeState, f'/hybrid_automaton/change_state')
            while not self._trigger_lifecycle_transition_cli.wait_for_service(timeout_sec=1.0):
                self.get_logger().info("waiting for /hybrid_automaton/change_state")

            # initialize hybrid automaton topic publishers
            self._mode_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/mode',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._invariant_publisher = self.create_publisher(
                Bool,
                '/hybrid_automaton/invariant',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._status_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/status',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._transition_evaluation_publisher = self.create_publisher(
                topic="/hybrid_automaton/transition_evaluations",
                msg_type=COLAVTransition,
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._dynamics_publisher = self.create_publisher(
                msg_type=Dynamics,
                topic='/hybrid_automaton/dynamics',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._waypoints_publisher = self.create_publisher(
                msg_type=Waypoints,
                topic='/hybrid_automaton/state/waypoints',
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            # initialize hybrid automaton topic subscriptions
            # self._transition_evaluation_subscriber = self.create_subscription(
            #     topic="/hybrid_automaton/transition_evaluations",
            #     msg_type=COLAVTransition,
            #     callback=lambda msg: self.__setattr__('_current_transition_evaluation', msg), # TODO: In callback lets do the prioritization analysis to see which mode we should transition to to set it to current state attributes instead of taking the whole message.
            #     qos_profile=QOS_PROFILE,
            #     callback_group=ReentrantCallbackGroup()
            # )
            self._status_subscription = self.create_subscription( # TODO: CLOSE THIS IN DEACTIVATE
                msg_type=String,
                topic='/hybrid_automaton/status',
                callback=on_status_received_callback,
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )

            # TODO: need to do transition evaluation next
            # TODO: Then do invariants
            # Should add script to move automaton to inactive mode to launch before starting mission manager.
            
            self._mode_subscription = self.create_subscription(
                String,
                '/hybrid_automaton/mode',
                callback=lambda msg: on_mode_callback(
                    lock=self._mode_callback_lock,
                    node=self,
                    available_modes=self._available_modes,
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

            self._invariant_subscription = self.create_subscription(
                Bool,
                '/hybrid_automaton/invariant',
                qos_profile=QOS_PROFILE,
                callback=on_invariant_status_received,
                callback_group=ReentrantCallbackGroup()
            )

            self._invariant_timeout_guard_lock = threading.Lock()
            self._trigger_invariant_timeout_guard:GuardCondition = self.create_guard_condition(
                handle_invariant_timeout_guard,
                callback_group=ReentrantCallbackGroup()
            )

            self._waypoints_publisher.publish(Waypoints(waypoints=[self._goal_waypoint]))
            
            # start timers
            self._transition_evaluation_timer.reset()
            self._dynamics_timer.reset()
            # self._invariant_evaluation_timer.reset()
    
            for param_key in self._ACTIVATION_PARAMS:
                self.undeclare_parameter(param_key)

        except Exception as e:
            self.get_logger().error(f"unexpected exception occured during transition from '{state.label}' to 'activate': {str(e)}")
            return TransitionCallbackReturn.FAILURE

        return super().on_activate(state)
    
    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")

        try:
            # stop the timers.
            self._transition_evaluation_timer.cancel()
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
            if hasattr(self, '_transition_evaluation_timer'):
                self._transition_evaluation_timer.cancel()
                self.destroy_timer(self._transition_evaluation_timer)
                self._transition_eval_timer:Timer = None

            if hasattr(self, '_dynamics_timer'):
                self._dynamics_timer.cancel()
                self.destroy_timer(self._dynamics_timer)
                self._dynamics_timer:Timer = None

            if hasattr(self, '_invariant_timer'):
                self._invariant_timer.cancel()
                self.destroy_timer(self._invariant_timer)
                self._invariant_timer:Timer = None

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
                self._transition_evaluation_timer.cancel()
                self.destroy_timer(self._transition_evaluation_timer)
                del self._transition_evaluation_timer

            if hasattr(self, '_dynamics_eval_timer'):
                self._dynamics_timer.cancel()
                self.destroy_timer(self._dynamics_timer)
                del self._dynamics_timer

            # Log and shut down node
            self.get_logger().info("Shutdown complete. Resources cleaned up.")

            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Exception occurred during shutdown: {e}")
            return TransitionCallbackReturn.FAILURE
        
def main():
    rclpy.init()
   
    automaton_node = HybridAutomatonNode(name='hybrid_automaton', namespace=None)
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())

    try:
        executor.add_node(automaton_node)
        executor.spin()
    except Exception as e:
        executor.shutdown()
        automaton_node.destroy_node()
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()