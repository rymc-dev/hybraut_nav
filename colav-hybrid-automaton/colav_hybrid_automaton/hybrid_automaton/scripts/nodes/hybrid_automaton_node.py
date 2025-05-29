
"""
ROS2 Hybrid Automaton node. performs lifecycle managements of the hybrid automaton 
starting and stopping the mode based on requests while managing control mode of the hybrid automaton
as defined within the hybrid_automaton_config.yml
Performs transitions resets and transition evaluations
"""

# from rclpy.lifecycle import Node, State, TransitionCallbackReturn
from rclpy.lifecycle import LifecycleNode, State, TransitionCallbackReturn
from std_msgs.msg import String
from hybrid_automaton.config import QOS_PROFILE, HybridAutomatonStatus
from hybrid_automaton_interfaces.msg import TransitionPending, Transition, Dynamics
import uuid
from unique_identifier_msgs.msg import UUID
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from hybrid_automaton.utils import load_yml, process_automaton_config
from colav_interfaces.msg import Waypoint, Waypoints
from geometry_msgs.msg import Point32
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.timer import Timer
from rclpy.publisher import Publisher
from typing import List, Optional
from rclpy.subscription import Subscription
from std_srvs.srv import Trigger
from rclpy.service import Service
from rclpy.client import Client
from hybrid_automaton.utils import create_state_subscriptions
SYSTEM_CLOCK = None

class HybridAutomatonNode(LifecycleNode):
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
        self._evaluation_timesteps_in_mode:int = None # TODO: This will be equal to the evaluations since invariant == false if transition is not made after invariant for mode evaluates as true. Invariant activity should occur. before deactiving automatically teh hybrid automaton
        self._status:HybridAutomatonStatus = None
        self._invariant:bool = None
        self._current_transition_uuid: UUID = None
        self._current_transition_evaluation:Transition = None
        self._reset_event = None
        self._waiting_after_reset:bool = False
        self._reset_complete_time = None
        self._current_invariant_status = None
        self._automaton_active = False
        # Publishers
        self._mode_publisher:Publisher = None
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
        self._transition_evaluation_timer:Timer  = None
        self._dynamics_timer:Timer = None
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
        self._evaluation_frequency: int = 1 # default evaluation per second
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
            
            # need to create the callback groups
            self._transition_engine_callback_group = ReentrantCallbackGroup()
            self._transition_evaluation_timer_callback_group = ReentrantCallbackGroup()
            self._dynamics_timer_callback_group = ReentrantCallbackGroup()
            self._topic_io_callback_group = ReentrantCallbackGroup()

            # initialize hybrid automaton topic publishers

            self._status_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/status',
                qos_profile=QOS_PROFILE,
                callback_group=self._topic_io_callback_group
            )
            self._transition_evaluation_publisher = self.create_publisher(
                topic="/hybrid_automaton/transition_evaluations",
                msg_type=Transition,
                qos_profile=QOS_PROFILE,
                callback_group=self._topic_io_callback_group
            )
            self._dynamics_publisher = self.create_publisher(
                msg_type=Dynamics,
                topic='/hybrid_automaton/dynamics',
                qos_profile=QOS_PROFILE,
                callback_group=self._topic_io_callback_group
            )
            self._waypoints_publisher = self.create_publisher(
                msg_type=Waypoints,
                topic='/hybrid_automaton/state/waypoints',
                qos_profile=QOS_PROFILE,
                callback_group=self._topic_io_callback_group
            )
            # initialize hybrid automaton topic subscriptions
            self._transition_evaluation_subscriber = self.create_subscription(
                topic="/hybrid_automaton/transition_evaluations",
                msg_type=Transition,
                callback=lambda msg: self.__setattr__('_current_transition_evaluation', msg), # TODO: In callback lets do the prioritization analysis to see which mode we should transition to to set it to current state attributes instead of taking the whole message.
                qos_profile=QOS_PROFILE,
                callback_group=self._topic_io_callback_group
            )

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
            self._transition_evaluation_timer = self.create_timer(
                timer_period_sec=1/self._evaluation_frequency, 
                callback=self._transition_eval_callback,
                callback_group=self._transition_evaluation_timer_callback_group,
                clock=SYSTEM_CLOCK,
                autostart=False
            )
            self._dynamics_timer = self.create_timer(
                timer_period_sec=1/self._control_frequency,
                callback=self._dynamics_callback,
                callback_group=self._dynamics_timer_callback_group,
                clock=SYSTEM_CLOCK,
                autostart=False
            )
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
            
            # create trigger transition service
            # self._trigger_transition_srv = self.create_service(
            #     srv_type=Trigger,
            #     srv_name='/hybrid_automaton/trigger_transition',
            #     callback=self._transition_engine_callback,
            #     callback_group = ReentrantCallbackGroup()
            # )
            # self._trigger_transition_cli = self.create_client(
            #     srv_type=Trigger,
            #     srv_name='/hybrid_automaton/trigger_transition',
            #     callback_group=ReentrantCallbackGroup()
            # )
            # if not self._trigger_transition_cli.wait_for_service(timeout_sec=5.0):
            #     self.get_logger().warning('trigger_transition srv not starting during activation')
            #     return TransitionCallbackReturn.FAILURE
            
            self._status_subscription = self.create_subscription( # TODO: CLOSE THIS IN DEACTIVATE
                msg_type=String,
                topic='/hybrid_automaton/status',
                callback=self._on_status_received_callback,
                qos_profile=QOS_PROFILE,
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
            
            self._mode_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/mode',
                qos_profile=QOS_PROFILE,
                callback_group=self._topic_io_callback_group
            )

            self._mode_subscription = self.create_subscription(
                String,
                '/hybrid_automaton/mode',
                callback=lambda msg: self.__setattr__('_mode', msg.data.lower()),
                qos_profile=QOS_PROFILE,
                callback_group=self._topic_io_callback_group
            )

            # validate values are not None for goal waypoint if they are return errror
            self._goal_waypoint = Waypoint(
                position=Point32(x=goal_waypoint_params['waypoint_x'], y=goal_waypoint_params['waypoint_y']),
                acceptance_radius=goal_waypoint_params['waypoint_acceptance_radius']
            )
            waypoints = Waypoints(
                waypoints=[self._goal_waypoint]
            )
            self._mode_publisher.publish(String(data="cruise")) # TODO: Need to get initial mode from config but for now this will do donkey

            # start timers
            self._transition_evaluation_timer.reset()
            self._dynamics_timer.reset()

            # get rid of waypoint params

        except Exception as e:
            self.get_logger().error(f"exception occured retrieving goal waypoint param")
            return TransitionCallbackReturn.FAILURE
        
        self.undeclare_parameter('waypoint_x')
        self.undeclare_parameter('waypoint_y')
        self.undeclare_parameter('waypoint_acceptance_radius')

        return super().on_activate(state)
    
    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")

        try:
            # stop the timers.
            self._transition_evaluation_timer.cancel()
            self._dynamics_timer.cancel()

            # stop the transition engine service
            # self.destroy_client(self._trigger_transition_cli)
            # self.destroy_service(self._trigger_transition_srv)

            self.destroy_subscription(self._mode_publisher)
            self._mode_publisher: Publisher = None
            self.destroy_subscription(self._mode_subscription)
            self._mode_subscription: Subscription = None
            self.destroy_subscription(self._status_subscription)
            self._status_subscription:Subscription = None
            
            self._trigger_transition_cli = None
            self._trigger_transition_srv = None

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
        
        self.undeclare_parameter('waypoint_acceptance_radius')
        self.undeclare_parameter('waypoint_x')
        self.undeclare_parameter('waypoint_y')
        
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
            value=self._evaluation_frequency,
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

    def _on_status_received_callback(self, msg: String):
        if msg.data == HybridAutomatonStatus.COMPLETED.name:
            self._status = HybridAutomatonStatus.COMPLETED
        if msg.data == HybridAutomatonStatus.EXECUTING_MODE.name:
            self._status = HybridAutomatonStatus.EXECUTING_MODE
        if msg.data == HybridAutomatonStatus.ERROR.name:
            self._status = HybridAutomatonStatus.ERROR
        if msg.data == HybridAutomatonStatus.ERROR.name:
            self._status = HybridAutomatonStatus.ERROR
        if msg.data == HybridAutomatonStatus.TRANSITIONING.name:
            self.get_logger().info('Starting Transition')

            # # TODO:  Get invariant need to move invariant check to evaluation loop back
            # invariant = self._configuration['modes'][self._mode].get('invariants')
            # if not invariant:
            #     return  # No invariant found

            # inv_func = self._configuration['invariants'][invariant]['function']
            # state_inputs_raw = self._configuration['invariants'][invariant].get('state_inputs', [])
            # state_inputs = [
            #     self._configuration['states'][state_input]['state']
            #     for state_input in state_inputs_raw if state_input in self._configuration['states']
            # ]
            # try:
            #     invariant_output = inv_func(*state_inputs)
            # except Exception as e:
            #     self.get_logger().error(str(e))
            #     self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
            #     return

            # If no transition is pending, re-publish current mode
            if isinstance(self._current_transition_evaluation, Transition):
                # Transition evaluation
                current_transition_eval:Transition = self._current_transition_evaluation

                if not current_transition_eval.success:
                    self.get_logger().error(f"Transition evaluation failed: {current_transition_eval.message}")
                    self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                    return

                self.current_transition_uuid = current_transition_eval.transition_uuid
                pending = [
                    name for idx, name in enumerate(current_transition_eval.transition_names)
                    if current_transition_eval.transition_values[idx]
                ]
            else:
                # should never get to this point
                self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                return 
                # # No transitions pending: finalize or return based on invariant output
                # if invariant_output is False:
                #     self._status_publisher.publish(String(data=HybridAutomatonStatus.COMPLETED.name))
                #     return
                
                # self.status_publisher.publish(String(data=HybridAutomatonStatus.ACTIVE.name))
                # return

            # Select the highest-priority transition
            transition = self._select_highest_priority_transition(pending)
            # no transitions and invariants is still true therefore we still active
            if transition is None: # should not be none
                self._status_publisher.publish(String(data=HybridAutomatonStatus.ERROR.name))
                return

            # Handle reset if required
            reset_name = self._configuration['transitions'][transition].get('reset')
            if reset_name and reset_name in self._configuration['resets']:
                
                self._perform_reset(transition)
                self._parse_and_publish_transition(transition)
                self._status_publisher.publish(String(data=HybridAutomatonStatus.EXECUTING_MODE.name))
            else:
                self._parse_and_publish_transition(transition)
                self._status_publisher.publish(String(data=HybridAutomatonStatus.EXECUTING_MODE.name))

    def _perform_reset(self, transition):
        """performs state reset"""
        reset_name = self._configuration['transitions'][transition].get('reset')
        reset_func = self._configuration['resets'][reset_name]['function']
        input_names = self._configuration['resets'][reset_name]['state_inputs']
        state_inputs = [self._configuration['states'][state_name]['state'] for state_name in input_names]
        reset_outputs = reset_func(*state_inputs)
        state_outputs = self._configuration['resets']['remove_first_waypoint']['state_outputs']
        for idx, state_output in enumerate(state_outputs):
            self._configuration['states'][state_output]['pub'].publish(reset_outputs[idx])

    def _parse_and_publish_transition(self, transition):
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

        self._mode_publisher.publish(String(data=transition_to))


    def _select_highest_priority_transition(self, pending):
        """
        Helper function to select the highest-priority transition from a list of pending transitions.
        """
        if len(pending) == 1:
            return pending[0]
        
        highest_priority = float('inf')
        transition = None
        for name in pending:
            prio = self.config['modes'][self.mode]['transitions'][name]['priority']
            if prio < highest_priority:
                highest_priority = prio
                transition = name
        return transition

            
    def _transition_engine_callback(self, req: Trigger.Request) -> Trigger.Response:
        """This is a callback for transitioning from one automaton mode to another"""
        
        return Trigger.Response(
            success = True,
            message = "people"
        )

        # try:
        #     # Transition occurs if transition pending is true and mode is type string
        #     if msg.transition_pending and isinstance(self.mode, str):
        #         self.get_logger().info('transition event in progress.')
        #         # TODO: ASSIGN TIMESTAMP TO STATUS PUBLISHED
        #         stamp = self.get_clock().now().to_msg()
        #         try:
        #             self.validate_mode(mode=self.mode)
        #         except Exception as e:
        #             self.get_logger().error(str(e))
        #             self.status_publisher.publish(String(data= HybridAutomatonStatus.TRANSITION_ERROR.name))
        #             return
            
        #         self.status_publisher.publish(String(data=HybridAutomatonStatus.TRANSITIONING.name))
                
        #     # Get invariant
        #     # invariant = self.check_invariant(self.mode)
        #     transition = self._select_highest_priority_transition(pending)
        #     pending = [
        #         name for idx, name in enumerate(curr_transition_eval.transition_names)
        #         if curr_transition_eval.transition_values[idx]
        #     ]

        # except Exception as e:
        #     self.get_logger().error(str(e))

    def check_invariant(self, mode:str):
        """checks the invariant function for mode"""
        try:
            invariant = self.config['modes'][mode].get('invariants')
            if not invariant:
                return  # No invariant found

            inv_func = self.config['invariants'][invariant]['function']
            state_inputs_raw = self.config['invariants'][invariant].get('state_inputs', [])
            state_inputs = [
                self.config['states'][state_input]['state']
                for state_input in state_inputs_raw if state_input in self.config['states']
            ]

            return inv_func(*state_inputs)
        except Exception as e:
            self.get_logger().error(str(e))
            self.status_publisher.publish(String(data=HybridAutomatonStatus.FAILED.name))
            return
        
    def _transition_eval_callback(self):
        """
        Transition evaluations 
        """
        try:
            stamp = self.get_clock().now().to_msg()
            eval = Transition(stamp=stamp, mode=self.validate_mode(self._mode))
            
            if self._status is HybridAutomatonStatus.TRANSITIONING:            
                return
                # eval.transition_uuid = self.current_transition_uuid
                # eval.success = True
                # eval.message = f"transition evaluation skipped currently transitioning"
            else:
                self.current_transition_uuid = UUID(uuid = list(uuid.uuid4().bytes))
                eval.transition_uuid = self.current_transition_uuid

                transitions = self._configuration['modes'][eval.mode].get('transitions', {})
                transition_names = list(transitions.keys())

                eval.success = True
                eval.transition_names = []
                eval.transition_values = []
                eval.transition_priority = []

                error_messages = []
                for name in transition_names:
                    try:
                        transition_config = self._configuration['transitions'][name]
                        guard_key = transition_config['guard']
                        guard_config = self._configuration['guards'][guard_key]
                        guard_func = guard_config['function']
                        state_inputs = [self._configuration['states'][s]['state'] for s in guard_config['state_inputs']]

                        result = bool(guard_func(*state_inputs))
                        eval.transition_names.append(name)
                        eval.transition_values.append(result)
                        eval.transition_priority.append(transitions[name]['priority'])
                    except Exception as e:
                        error_messages.append(f"{name}: {e}")
                        eval.success = False

                if error_messages:
                    raise ValueError("Errors during evaluation: " + "; ".join(error_messages))

                if any(eval.transition_values):
                    self._status = HybridAutomatonStatus.TRANSITIONING
                    self._transition_evaluation_publisher.publish(eval)
                    # rate = self.create_rate(frequency=1.0, clock=SYSTEM_CLOCK)
                    # self._current_transition_evaluation = eval
                    self._status_publisher.publish(String(data=str(self._status.name)))
                    return

                self._status = HybridAutomatonStatus.EXECUTING_MODE
                self._status_publisher.publish(String(data=str(self._status.name)))
        except Exception as e:
            self._status = HybridAutomatonStatus.ERROR
            self._status_publisher.publish(String(str(self._status.name)))
            eval.success = False
            eval.message = str(e)

        self._transition_evaluation_publisher.publish(eval)

    def _handle_transition_response(self, future):
        try:
            result = future.result()
            self.get_logger().info(f"Transition completed: {result.success}, message: {result.message}")
        except Exception as e:
            self.get_logger().error(f"Transition service call failed: {e}")


    
    def _dynamics_callback(self):
        """
        dynamic update callback function
        """
        try:
            msg = Dynamics(mode= self.validate_mode(self._mode), stamp=self.get_clock().now().to_msg())

            self._configuration['dynamics'][self._configuration['modes'][msg.mode]['dynamics']]
            msg.dynamic_parameters.controller_name = self._configuration['modes'][msg.mode]['dynamics']
            msg.dynamic_parameters.dynamic_name = list(self._configuration['dynamics'][msg.dynamic_parameters.controller_name]['output'].keys())
            msg.dynamic_parameters.dynamic_units = list(self._configuration['dynamics'][msg.dynamic_parameters.controller_name]['output'].values())

            dynamic_function = self._configuration['dynamics'][msg.dynamic_parameters.controller_name]['function']

            if 'state_inputs' in  self._configuration['dynamics'][msg.dynamic_parameters.controller_name]:
                state_input_names = self._configuration['dynamics'][msg.dynamic_parameters.controller_name]['state_inputs']
                state_inputs = [self._configuration['states'][state_name]['state'] for state_name in state_input_names]
                msg.dynamic_parameters.dynamic_value = dynamic_function(*state_inputs)
            else: 
                msg.dynamic_parameters.dynamic_value = dynamic_function()

            msg.success = True
        except Exception as e:
            msg.success = False
            msg.message = str(e)
        
        self._dynamics_publisher.publish(msg)

    # """ === Util Functions subscriber bscription 
    def validate_mode(self, mode) -> str:
        if not isinstance(mode, str):
            raise TypeError('mode is not of correct type string')
        if mode not in self._automaton_modes:
            raise ValueError('current mode is not in automaton modes')
        
        return mode


from rclpy.executors import MultiThreadedExecutor
import rclpy

def main():
    rclpy.init()
    node = HybridAutomatonNode(name='hybrid_automaton', namespace='colav')
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