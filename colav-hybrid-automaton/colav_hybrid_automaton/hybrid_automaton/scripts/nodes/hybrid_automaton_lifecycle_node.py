
"""
ROS2 Hybrid Automaton node. performs lifecycle managements of the hybrid automaton 
starting and stopping the mode based on requests while managing control mode of the hybrid automaton
as defined within the hybrid_automaton_config.yml
Performs transitions resets and transition evaluations
"""

# from rclpy.lifecycle import Node, State, TransitionCallbackReturn
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.lifecycle import LifecycleNode, State, TransitionCallbackReturn
from std_msgs.msg import String, Bool
from hybrid_automaton.config import QOS_PROFILE, HybridAutomatonStatus
from hybrid_automaton_interfaces.msg import TransitionPending, Transition as COLAVTransition, Dynamics
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from hybrid_automaton.utils import load_yml, process_automaton_config
from colav_interfaces.msg import Waypoint, Waypoints
from geometry_msgs.msg import Point
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.timer import Timer
from rclpy.publisher import Publisher
from typing import List, Optional, Any
from rclpy.subscription import Subscription
from std_srvs.srv import Trigger
from rclpy.service import Service
from rclpy.client import Client
from hybrid_automaton.utils import create_state_subscriptions
import threading
import time
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState
from rclpy.guard_condition import GuardCondition

SYSTEM_CLOCK = None

class HybridAutomatonLifecycleNode(LifecycleNode):
    """
    A Hybrid Automaton Node Managed Node which performs 
    executes dynamics, invariants transitions and so on
    based on hybrid automaton configuration.
    """

    def __init__(
        self, 
        name: str, 
        namespace: Optional[str]
    ):
        """init"""
        super().__init__(name, namespace=namespace)
        
        # Internal States
        self._mode:str = None
        self._mode_dynamics = None
        self._mode_invariant = None 
        self._mode_transitions = None
        self._evaluation_timesteps_in_mode:int = None # TODO: This will be equal to the evaluations since invariant == false if transition is not made after invariant for mode evaluates as true. Invariant activity should occur. before deactiving automatically teh hybrid automaton
        self._status:HybridAutomatonStatus = None
        self._invariant:bool = None
        self._current_transition_evaluation:Transition = None
        self._reset_event = None
        self._waiting_after_reset:bool = False
        self._reset_complete_time = None
        self._current_invariant_status = None
        self._automaton_active = False
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
        # srv
        self._trigger_transition_srv:Service = None
        # cli
        self._trigger_transition_cli:Client = None
        # Timers
        self._transition_evaluation_timer:Timer = None
        self._dynamics_timer:Timer = None
        self._invariant_timer:Timer = None
        # Callback Groups
        self._transition_engine_callback_group:ReentrantCallbackGroup = None
        self._transition_evaluation_timer_callback_group:ReentrantCallbackGroup = None
        self._dynamics_timer_callback_group:ReentrantCallbackGroup = None
        self._topic_io_callback_group:ReentrantCallbackGroup = None
        self._trigger_transition_callback_group:MutuallyExclusiveCallbackGroup = None
        # self._dynamics_eval_timer_callback_group:ReentrantCallbackGroup = None
        # Internal Continuous states
        self._automaton_goal_waypoint:Waypoint = None
        # Internal Configuration
        self._automaton_modes:List[str] = None
        self._configuration_path: str = "" # Path to configuration
        self._configuration: dict = None
        self._evaluation_frequency: int = 100 # default evaluation per second
        self._control_frequency: int = 100 # default 100 evaluations per second

        self.declare_parameter(
            'configuration_path',
            value=self._configuration_path,
            descriptor=ParameterDescriptor(
                description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
            )
        )
        self.declare_parameter(
            'evaluation_frequency',
            value=self._evaluation_frequency,
            descriptor=ParameterDescriptor(
                description="Frequency (in Hz) at which transition conditions are evaluated."
            )
        )
        self.declare_parameter(
            'control_frequency',
            value=self._control_frequency,
            descriptor=ParameterDescriptor(
                description="Frequency (in Hz) at which controller feedback is returned."
            )
        )

        self.get_logger().info(f"{namespace}/{name}: managed node initialized")


    """ === LifeCycle Transition Functions === """

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """on configuration state initializes node attributes like subscribers and publishers"""
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'")

        try:
            self._configuration_path = self.get_parameter('configuration_path').value
            self._evaluation_frequency= self.get_parameter('evaluation_frequency').value
            self._control_frequency = self.get_parameter('control_frequency').value

            self._configuration = process_automaton_config(
                config=load_yml(
                    yml_path=self._configuration_path
            ))
            create_state_subscriptions(node=self)
            self._automaton_modes = list(self._configuration['modes'].keys())

            self.declare_parameter(
                'waypoint_x',
                value=0.0,
                descriptor=ParameterDescriptor(
                    description="COLAV Hybrid Automaton State for goal waypoints 'x' position (m)."
                )
            )
            # TODO: IN CLEANUP REMOVE PARAM WAYPOINTS
            self.declare_parameter(
                'waypoint_y',
                value=0.0,
                descriptor=ParameterDescriptor(
                    description="COLAV Hybrid Automaton State for goal waypoints 'y' Position (m)."
                )
            )
            self.declare_parameter(
                'waypoint_acceptance_radius',
                value=0.0,
                descriptor=ParameterDescriptor(
                    description="COLAV Hybrid Automaton State for goal waypoints 'acceptance radius' (m)."
                )
            )
            self._transition_evaluation_timer = self.create_timer(
                timer_period_sec=1/self._evaluation_frequency, 
                callback=self._transition_evaluation_timer_callback,
                callback_group=ReentrantCallbackGroup(),
                clock=SYSTEM_CLOCK,
                autostart=False
            )
            self._transition_eval_lock = threading.Lock()
            self._dynamics_timer = self.create_timer(
                timer_period_sec=1/self._control_frequency,
                callback=self._dynamics_timer_callback,
                callback_group=ReentrantCallbackGroup(),
                clock=SYSTEM_CLOCK,
                autostart=False
            )
            self._dynamics_timer_callback_lock = threading.Lock()
            self._invariant_evaluation_timer = self.create_timer(
                timer_period_sec=1/self._evaluation_frequency,
                callback=self._invariant_evaluation_timer_callback,
                callback_group=ReentrantCallbackGroup(),
                autostart=False
            )
            self._invariant_evaluation_lock = threading.Lock()
        except Exception as e: 
            self.get_logger().error(f"Configuration failed: {e}")
            return TransitionCallbackReturn.FAILURE

        self.undeclare_parameter('configuration_path')
        self.undeclare_parameter('evaluation_frequency')
        self.undeclare_parameter('control_frequency')
    
        return super().on_configure(state)

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")

        try:
            # initialize transition trigger client
            self._trigger_transition_cli = self.create_client(ChangeState, f'{self.get_namespace()}/{self.get_name()}/change_state')
            while not self._trigger_transition_cli.wait_for_service(timeout_sec=1.0):
                self.get_logger().info('Waiting for change_state service...')

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
            self._transition_evaluation_subscriber = self.create_subscription(
                topic="/hybrid_automaton/transition_evaluations",
                msg_type=COLAVTransition,
                callback=lambda msg: self.__setattr__('_current_transition_evaluation', msg), # TODO: In callback lets do the prioritization analysis to see which mode we should transition to to set it to current state attributes instead of taking the whole message.
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._status_subscription = self.create_subscription( # TODO: CLOSE THIS IN DEACTIVATE
                msg_type=String,
                topic='/hybrid_automaton/status',
                callback=self._on_status_received_callback,
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._mode_subscription = self.create_subscription(
                String,
                '/hybrid_automaton/mode',
                callback=self._on_mode_received_callback,
                qos_profile=QOS_PROFILE,
                callback_group=ReentrantCallbackGroup()
            )
            self._invariant_subscription = self.create_subscription(
                Bool,
                '/hybrid_automaton/invariant',
                qos_profile=QOS_PROFILE,
                callback=self._on_invariant_callback,
                callback_group=ReentrantCallbackGroup()
            )

            
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
            waypoints = Waypoints(
                waypoints=[self._goal_waypoint]
            )
            self._mode_publisher.publish(String(data="cruise")) 
            self._waypoints_publisher.publish(waypoints)

        except Exception as e:
            self.get_logger().error(f"exception occured retrieving goal waypoint param")
            return TransitionCallbackReturn.FAILURE
        
        self.undeclare_parameter('waypoint_x')
        self.undeclare_parameter('waypoint_y')
        self.undeclare_parameter('waypoint_acceptance_radius')

        self._trigger_invariant_timeout_guard:GuardCondition = self.create_guard_condition(
            self._invariant_timeout_guard_callback,
            callback_group=ReentrantCallbackGroup()
        )
        self._invariant_timeout_guard_lock = threading.Lock()

        # start timers
        self._transition_evaluation_timer.reset()
        self._dynamics_timer.reset()
        self._invariant_evaluation_timer.reset()


        # self._invariant_evaluation_timer.reset()

        return super().on_activate(state)
    
    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")

        try:
            # stop the timers.
            self._transition_evaluation_timer.cancel()
            self._dynamics_timer.cancel()
            self._invariant_evaluation_timer.cancel()

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

        except Exception as e:
            self.get_logger().error(f"Cleanup failed: {e}")
            return TransitionCallbackReturn.FAILURE
        
        self.declare_parameter(
            'configuration_path',
            value=self._configuration_path,
            descriptor=ParameterDescriptor(
                description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
            )
        )
        self.declare_parameter(
            'evaluation_frequency',
            value=self._evaluation_frequency,
            descriptor=ParameterDescriptor(
                description="Frequency (in Hz) at which transition conditions are evaluated."
            )
        )
        self.declare_parameter(
            'control_frequency',
            value=self._control_frequency,
            descriptor=ParameterDescriptor(
                description="Frequency (in Hz) at which controller feedback is returned."
            )
        )

        self.get_logger().info("Cleanup successful.")
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")
        try:
            # Clean up resources as needed
            self.automaton_active = False

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
        

    """ === Callback Functions === """
    """ === Subscription Callbacks === """
    
    def _on_mode_received_callback(self, msg: String):
        """
        callback for receiving mode
        This function validates the mode received extracting transitions 
        data like the guards and resets functions assigning priority to each of them
        """
         
        with self._mode_callback_lock:
            _mode = None
            _mode_transitions_dict = {}
            _mode_dynamics = {} 
            _mode_invariant = {}     

            try:
                # Get current mode
                _mode = msg.data.lower()

                _mode_transitions = self._configuration['modes'][_mode].get('transitions', {})

                for _mode_transition in _mode_transitions:
                    _mode_transitions_dict[_mode_transition] = {
                        'guard':  { 
                            **self._configuration['guards'][self._configuration['transitions'][_mode_transition]['guard']], 
                            'name': self._configuration['transitions'][_mode_transition]['guard'] 
                        },
                        'reset': None if self._configuration['transitions'][_mode_transition]['reset'] is None else { 
                            **self._configuration['resets'][self._configuration['transitions'][_mode_transition]['reset']],
                            'name': self._configuration['transitions'][_mode_transition]['reset']
                        },
                        'priority': self._configuration['modes'][_mode]['transitions'][_mode_transition]['priority']
                    }

                _dynamic_function_name = self._configuration['modes'][_mode]['dynamics']
                _mode_dynamics[_dynamic_function_name]  = self._configuration['dynamics'][_dynamic_function_name]['function']

                _invariant_name = self._configuration['modes'][_mode]['invariants']
                _mode_invariant[_invariant_name] =  self._configuration['invariants'][_invariant_name]['function']
            except Exception as e: 
                self.get_logger().error(f'Exception occured _on_mode__received_callback: {str(e)}')
                self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                return
                
            self._mode = _mode
            self._mode_dynamics = _mode_dynamics
            self._mode_invariant = _mode_invariant
            self._mode_transitions = _mode_transitions_dict

    def _on_invariant_callback(self, msg: Bool):
        """Callback for receiving an invariant update."""
        if msg.data is False:  # invariant is true
            if self._invariant_timeout_guard_lock.acquire(blocking=False):
                try:
                    self._trigger_invariant_timeout_guard.trigger()
                finally:
                    self._invariant_timeout_guard_lock.release()

    def _invariant_timeout_guard_callback(self):
        """
        Triggered by a guard condition when an invariant holds.
        Waits for 1 second to allow a mode transition.
        If no transition occurs, checks if the mode is final.
        """
        with self._invariant_timeout_guard_lock:
            self.get_logger().info('Invariant timeout guard triggered')
            previous_mode = self._mode
            rate = self.create_rate(1.0, SYSTEM_CLOCK)
            rate.sleep()
            if self._mode == previous_mode:
                self.get_logger().info(
                    f"Invariant held in mode {self._mode} with no transition within time tolerance."
                )
                self._status_publisher.publish(String(data=HybridAutomatonStatus.COMPLETED.name))

    def _on_status_received_callback(self, msg: String):
        if msg.data == HybridAutomatonStatus.COMPLETED.name: # simply move hybrid automaton back to deactivate lifecycle state
            with self.completed_lock:
                self._status = HybridAutomatonStatus.COMPLETED
                self.get_logger().info('Waypoint reached hybrid automaton has completed.')
                future = self._trigger_transition_cli.call_async(ChangeState.Request(transition=Transition(id=Transition.TRANSITION_DEACTIVATE)))
        if msg.data == HybridAutomatonStatus.EXECUTING_MODE.name: # all this does is change the hybrid automaton state for executing mode
            with self.executing_mode_lock: 
                self._status = HybridAutomatonStatus.EXECUTING_MODE
        if msg.data == HybridAutomatonStatus.ERROR.name:
            with self.error_lock: # On exception print set the status and move hybrid automaton to deactivate state
                self.destroy_subscription(self._status_subscription)
                self._status = HybridAutomatonStatus.ERROR
                future = self._trigger_transition_cli.call_async(ChangeState.Request(transition=Transition(id=Transition.TRANSITION_DEACTIVATE)))
                
                rclpy.spin_until_future_complete(self,future, timeout_sec=5.0)
                if future.done():
                    if not future.result().success:
                        self.get_logger().error('transition request to configure for hybrid automaton lifecycle failed')
                
        if msg.data == HybridAutomatonStatus.TRANSITIONING.name:
            with self.transition_lock:
                try:
                    self._status = HybridAutomatonStatus.TRANSITIONING.name
                    # TODO: Move invariant check to evaluation loop if needed

                    if isinstance(self._current_transition_evaluation, COLAVTransition):
                        current_transition_eval: COLAVTransition = self._current_transition_evaluation

                        if not current_transition_eval.success:
                            self.get_logger().error(f"Transition evaluation failed: {current_transition_eval.message}")
                            self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                            return

                        pending = [
                            name for idx, name in enumerate(current_transition_eval.transition_names)
                            if current_transition_eval.transition_values[idx]
                        ]
                    else:
                        self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                        return

                    transition = self._select_highest_priority_transition(pending)
                    self.get_logger().info(f"Executing {transition} transition.")

                    if transition is None:
                        raise RuntimeError('transition is none')

                    if self._mode_transitions[transition]['reset'] is not None:
                        self.get_logger().info(f"Executing reset: '{self._mode_transitions[transition]['reset']['name']}'")
                        state_inputs = [self._configuration['states'][s]['state'] for s in self._mode_transitions[transition]['reset']['state_inputs']]
                        reset_outputs = self._mode_transitions[transition]['reset']['function'](*state_inputs)
                        self._waypoints_publisher.publish(*reset_outputs) # at the moment only reset type I am doing is waypoints TODO: Need to change this function

                    transition_to = self._parse_transition(transition)
                    self._mode_publisher.publish(String(data=transition_to))

                    # poll transition
                    timeout = 1
                    start_time = time.time()
                    rate = self.create_rate(100)
                    while not self._mode == transition_to:
                        if time.time() - start_time > timeout:
                            self.get_logger().warn("Mode transition timed out.")
                            break
                        rate.sleep()  # avoid busy waiting

                    self._status_publisher.publish(String(data=HybridAutomatonStatus.EXECUTING_MODE.name))
                except Exception as e:
                    self.get_logger().error(f"exception occured attempting transition: {str(e)}, transitioning to error state")
                    self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name)) 
                

    """ == Timer Callbacks"""
    def _invariant_evaluation_timer_callback(self):
        """invariant timer callback function"""
        with self._invariant_evaluation_lock:
            try:
                _invariant_key = next(iter(self._mode_invariant))
                _invariant_inputs = self.get_invariant_inputs(_invariant_key)
                _invariant_value:bool = self._mode_invariant[_invariant_key](*_invariant_inputs)

                self._invariant = True
                self._invariant_publisher.publish(Bool(data=_invariant_value))
            except Exception as e: 
                self._status = HybridAutomatonStatus.ERROR.name
                self.get_logger().error(f"Exception occured during invariant evaluation callback: {str(e)}")
                self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                # TODO: Maybe should stop the timer here.
                return

            
    def _transition_evaluation_timer_callback(self):
        """
        callback evaluates transitions available for the current Hybrid automaton mode.
        """
        with self._transition_eval_lock: 
            try:
                stamp = self.get_clock().now().to_msg()
                eval: COLAVTransition = COLAVTransition(stamp=stamp, mode=self.validate_mode(self._mode))
                
                if self._status is HybridAutomatonStatus.TRANSITIONING:            
                    return
                else:
                    eval.success = True
                    eval.transition_names = []
                    eval.transition_values = []
                    eval.transition_priority = []

                    error_messages = []
                    for transition_key in self._mode_transitions:
                        try:
                            transition_config = self._mode_transitions[transition_key]
                            state_inputs = [self._configuration['states'][s]['state'] for s in transition_config['guard']['state_inputs']]
                            guard_eval = bool(transition_config['guard']['function'](*state_inputs))
                            
                            eval.transition_names.append(transition_key)
                            eval.transition_values.append(guard_eval)
                            eval.transition_priority.append(transition_config['priority'])
                        except Exception as e:
                            error_messages.append(f"{transition_config['name']}: {str(e)}")
                            eval.success = False

                    if error_messages:
                        raise ValueError("Errors during evaluation: " + "; ".join(error_messages))

                    if any(eval.transition_values):
                        self._status = HybridAutomatonStatus.TRANSITIONING
                        self._status_publisher.publish(String(data=str(HybridAutomatonStatus.TRANSITIONING.name)))
                    else:
                        self._status = HybridAutomatonStatus.EXECUTING_MODE
                        self._status_publisher.publish(String(data=str(HybridAutomatonStatus.EXECUTING_MODE.name)))
                    self._current_transition_evaluation = eval
                    self._transition_evaluation_publisher.publish(eval)
            except Exception as e:
                self._status_publisher.publish(String(data=str(HybridAutomatonStatus.ERROR.name)))
                eval.success = False
                eval.message = str(e)

    def _dynamics_timer_callback(self):
        """
        dynamic update callback function
        """
        with self._dynamics_timer_callback_lock: 
            try:
                if self._mode is None:
                    raise ValueError()
        
                msg = Dynamics(mode= self.validate_mode(self._mode), stamp=self.get_clock().now().to_msg())

                dynamic_key = next(iter(self._mode_dynamics))
                msg.dynamic_parameters.controller_name = dynamic_key
                dynamic_function = self._mode_dynamics[dynamic_key]
                state_inputs = self.get_dynamic_inputs(dynamic_key)

                msg.dynamic_parameters.dynamic_name = ['velocity', 'yaw_rate']
                msg.dynamic_parameters.dynamic_units = ['m/s', 'r/s']
                msg.dynamic_parameters.dynamic_value = dynamic_function(*state_inputs)
                msg.success = True
            except Exception as e:
                self.get_logger().error(f'Exception during dynamics creation: {str(e)}')
                msg.success = False
                msg.message = str(e)
            
            self._dynamics_publisher.publish(msg)

    # === Helper Functions === 

    def _reset_callback(self, transition):
        """performs state reset"""
        self.get_logger().info(f"performing reset '{self._mode_transitions[transition]}' for transition.")
        reset_func = self._configuration['resets'][reset_name]['function']
        input_names = self._configuration['resets'][reset_name]['state_inputs']
        state_inputs = [self._configuration['states'][state_name]['state'] for state_name in input_names]
        reset_outputs = reset_func(*state_inputs)
        state_outputs = self._configuration['resets']['remove_first_waypoint']['state_outputs']
        for idx, state_output in enumerate(state_outputs):
            # self._configuration['states'][state_output]['pub'].publish(reset_outputs[idx])
            self._waypoints_publisher.publish(reset_outputs[idx])

    def _parse_transition(self, transition) -> str:
        """
        Publishes the transition when no reset is needed.
        """
        _, _, transition_to_raw = transition.partition("to_")

        # Split at the last underscore
        base, _, maybe_num = transition_to_raw.rpartition('_')

        if maybe_num.isdigit() and base in list(self._configuration['modes'].keys()):
            transition_to = base
        else:
            transition_to = transition_to_raw

        return transition_to

    def _select_highest_priority_transition(self, pending):
        """
        Helper function to select the highest-priority transition from a list of pending transitions.
        """
        if len(pending) == 1:
            return pending[0]
        
        highest_priority = float('inf')
        transition = None
        for name in pending:
            prio = self._configuration['modes'][self._mode]['transitions'][name]['priority']
            if prio < highest_priority:
                highest_priority = prio
                transition = name
        return transition

    def validate_mode(self, mode) -> str:
        if not isinstance(mode, str):
            raise TypeError('mode is not of correct type string')
        if mode not in self._automaton_modes:
            raise ValueError('current mode is not in automaton modes')
        
        return mode

    def get_guard_inputs(self, guard_key: str) -> List[Any]:
        pass

    def get_reset_inputs(self, reset_key: str) -> List[Any]:
        pass

    def get_dynamic_inputs(self, dynamic_key: str) -> List[Any]:
        dynamics_config = self._configuration.get('dynamics', {}).get(dynamic_key, {})
        state_input_names = dynamics_config.get('state_inputs', [])

        return [
            self._configuration['states'][name]['state']
            for name in state_input_names
            if name in self._configuration['states']
        ]

    def get_invariant_inputs(self, invariant_key: str) -> List[Any]:
        """Retrieves the state values for the given invariant's state inputs."""

        invariants = self._configuration.get('invariants', {})
        states = self._configuration.get('states', {})

        state_input_names = invariants.get(invariant_key, {}).get('state_inputs', [])

        return [
            states[name]['state']
            for name in state_input_names
            if name in states
        ]

        

def main():
    rclpy.init()
    node = HybridAutomatonLifecycleNode(name='lifecycle', namespace='colav/hybrid_automaton')
    executor = MultiThreadedExecutor(num_threads=16)

    try:
        executor.add_node(node)
        executor.spin()
    except Exception as e:
        executor.shutdown()
        node.destroy_node()
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()