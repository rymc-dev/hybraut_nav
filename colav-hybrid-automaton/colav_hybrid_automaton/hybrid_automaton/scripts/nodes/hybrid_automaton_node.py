
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

class HybridAutomatonNode(LifecycleNode):

    def __init__(
        self,
        name: str,
        namespace: str
    ):
        super().__init__(name, namespace=namespace)
        
        self.mode = None
        self.status = None
        self.transition_pending = None
        self.transition_eval = None
        self._waiting_after_reset = False
        self._reset_complete_time = None
        self.current_transition_uuid = None
        self.current_invariant_status = None
        self.reset_event = None
        self.current_transition_eval = None
        self.automaton_active = False

        self.config_path = ""
        self.evaluation_hz = 1.0
        self.config = None

        self.mode_publisher = None
        self.status_publisher = None
        self.transition_pending_pub = None
        self.transition_eval_pub = None
        self.dynamics_pub = None

        self.transition_sub = None
        self.transition_pending_sub = None
        self.status_sub = None
        
        self.transition_eval_timer = None
        self.dynamics_eval_timer = None
        self.automaton_modes = None

        self.automaton_goal_waypoint = None

        self.declare_parameter(
            'config_path',
            value=self.config_path,
            descriptor=ParameterDescriptor(
                description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
            )
        )
        self.declare_parameter(
            'evaluation_hz',
            value=self.evaluation_hz,
            descriptor=ParameterDescriptor(
                description="Frequency (in Hz) at which transition conditions are evaluated."
            )
        )

        self.get_logger().info(f"{namespace}/{name}: managed node initialized")

    """ === LifeCycle Transition Functions === """

    def on_configure(self, state):
        """on configuration state initializes node attributes like subscribers and publishers"""
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'configure'")
        try:
            # load configuration 
            self.automaton_active = False
            self.config_path = self.get_parameter('config_path').value
            self.eval_hz = self.get_parameter('evaluation_hz').value
            self.config = load_yml(self.config_path)
            self.config = process_automaton_config(self.config)
            self.automaton_modes = list(self.config['modes'].keys())

            self.topic_io_callback = ReentrantCallbackGroup()
            # initialize hybrid automaton topic publishers
            self.mode_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/mode',
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_io_callback
            )
            self.status_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/status',
                qos_profile=QOS_PROFILE,
                # callback_group=self.topic_callback_group
            )
            self.transition_pending_pub = self.create_publisher(
                TransitionPending,
                '/hybrid_automaton/transition_pending',
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_io_callback
            )
            self.transition_eval_pub = self.create_publisher(
                topic="/hybrid_automaton/transitions",
                msg_type=Transition,
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_io_callback
            )
            self.dynamics_pub = self.create_publisher(
                msg_type=Dynamics,
                topic='/hybrid_automaton/dynamics',
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_io_callback
            )

            # initialize hybrid automaton topic subscriptions
            self.transition_sub = self.create_subscription(
                topic="/hybrid_automaton/transitions",
                msg_type=Transition,
                callback=lambda msg: self.__setattr__('transition_eval', msg),
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_io_callback
            )
            self.transition_pending_sub = self.create_subscription(
                topic="/hybrid_automaton/transition_pending",
                msg_type=TransitionPending,
                callback=self.transition_engine_callback,
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_io_callback
            )
            self.status_sub = self.create_subscription(
                topic='/hybrid_automaton/status',
                msg_type=String,
                callback=lambda msg: self.__setattr__('status', msg.data),
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_io_callback
            )

            self.goal_waypoint =  None

            self.declare_parameter(
                'waypoint_x',
                value=ParameterType.PARAMETER_DOUBLE,
                descriptor=ParameterDescriptor(
                    description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
                )
            )
            self.declare_parameter(
                'waypoint_y',
                value=ParameterType.PARAMETER_DOUBLE,
                descriptor=ParameterDescriptor(
                    description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
                )
            )
            self.declare_parameter(
                'waypoint_acceptance_radius',
                value=ParameterType.PARAMETER_DOUBLE,
                descriptor=ParameterDescriptor(
                    description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
                )
            )
        
            # initialize the hybrid automaton timers.
            self._transition_eval_timer = self.create_timer(
                1/self.eval_hz, 
                self._transition_eval_callback,
                callback_group=ReentrantCallbackGroup()
            )
            self._dynamics_eval_timer = self.create_timer(
                1/self.eval_hz,
                self._dynamics_callback,
                callback_group=ReentrantCallbackGroup()
            )
        except Exception as e: 
            self.get_logger().error(f"Configuration failed: {e}")
            return TransitionCallbackReturn.FAILURE,
    
        return super().on_configure(state)

    def on_activate(self, state):
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'activate'")

        try:
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
            self.goal_waypoint = Waypoint(
                position=Point32(x=goal_waypoint_params['waypoint_x'], y=goal_waypoint_params['waypoint_y']),
                acceptance_radius=goal_waypoint_params['waypoint_acceptance_radius']
            )
            waypoints = Waypoints(
                waypoints=[self.goal_waypoint]
            )

        except Exception as e:
            self.get_logger().error(f"exception occured retrieving goal waypoint param")
            return TransitionCallbackReturn.FAILURE
        
        self.automaton_active = True
        return super().on_activate(state)
    
    def on_deactivate(self, state):
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'deactivate'")

        try:
            # Deactivate the automaton
            self.automaton_active = False

            # Clear goal waypoint
            if hasattr(self, 'goal_waypoint'):
                del self.goal_waypoint

            self.get_logger().info("Hybrid Automaton deactivated and goal waypoint cleared.")
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Exception occurred during deactivation: {e}")
            return TransitionCallbackReturn.FAILURE
    
    def on_cleanup(self, state):
        """Cleanup resources allocated during the 'configure' state."""
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'cleanup'")

        try:
            # Destroy timers
            if hasattr(self, '_transition_eval_timer'):
                self._transition_eval_timer.cancel()
                self.destroy_timer(self._transition_eval_timer)
                del self._transition_eval_timer

            if hasattr(self, '_dynamics_eval_timer'):
                self._dynamics_eval_timer.cancel()
                self.destroy_timer(self._dynamics_eval_timer)
                del self._dynamics_eval_timer

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
                    delattr(self, pub_attr)

            # Destroy subscriptions
            for sub_attr in [
                'transition_sub',
                'transition_pending_sub',
                'status_sub'
            ]:
                if hasattr(self, sub_attr):
                    self.destroy_subscription(getattr(self, sub_attr))
                    delattr(self, sub_attr)

            # Remove other attributes
            for attr in [
                'automaton_active',
                'config_path',
                'eval_hz',
                'config',
                'automaton_modes',
                'goal_waypoint',
                'topic_io_callback'
            ]:
                if hasattr(self, attr):
                    delattr(self, attr)

            self.get_logger().info("Cleanup successful.")
            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Cleanup failed: {e}")
            return TransitionCallbackReturn.FAILURE

    def on_shutdown(self, state):
        self.get_logger().info(f"Node '{self.get_name()}' is in state '{state.label}'. Transitioning to 'shutdown'")
        try:
            # Clean up resources as needed
            self.automaton_active = False

            # Stop and destroy timers if still active
            if hasattr(self, '_transition_eval_timer'):
                self._transition_eval_timer.cancel()
                self.destroy_timer(self._transition_eval_timer)
                del self._transition_eval_timer

            if hasattr(self, '_dynamics_eval_timer'):
                self._dynamics_eval_timer.cancel()
                self.destroy_timer(self._dynamics_eval_timer)
                del self._dynamics_eval_timer

            # Log and shut down node
            self.get_logger().info("Shutdown complete. Resources cleaned up.")

            return TransitionCallbackReturn.SUCCESS
        except Exception as e:
            self.get_logger().error(f"Exception occurred during shutdown: {e}")
            return TransitionCallbackReturn.FAILURE

    
    """ === Callback Functions === """

    def transition_engine_callback(self, msg: TransitionPending):
        """This is a callback for transitioning from one automaton mode to another"""
        if not self.automaton_active:
            return
        
        return

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
        """Evaluate transitions based on the current control mode in the Hybrid Automaton."""
        if not self.automaton_active: # this signifies we are in the activated state for this mode.
            return
        
        return
        
        # stamp = self.get_clock().now().to_msg()
        
        # if self.transition_event.is_set():
        #     self.get_logger().info('transition event in progress, skipping evaluation')
            
        #     transition_eval = Transition(success=True, error_message='No error, currently transitioning.')
        #     transition_pending = TransitionPending(transition_pending = True, stamp=stamp, transition_uuid=self._current_transition_uuid)
        #     self.transition_pending_pub.publish(transition_pending)
        #     return
        # else:
        #     transition_id = uuid.uuid4()
        #     ros_uuid = UUID()
        #     ros_uuid.uuid = list(transition_id.bytes)
        #     self._current_transition_uuid = ros_uuid
        #     transition_eval = Transition(stamp=stamp, transition_uuid=ros_uuid)
        #     transition_pending = TransitionPending(stamp=stamp, transition_uuid=ros_uuid)

        #     def publish_error(message: str):
        #         transition_eval.success = False
        #         transition_eval.error_message = message
        #         transition_eval.stamp = stamp
        #         self.transition_eval_pub.publish(transition_eval)

        #     try:
        #         try:
        #             current_mode = self.mode.lower()
        #             transition_eval.mode = current_mode
        #         except Exception:
        #             raise RuntimeError("Hybrid Automaton Control Mode not received on /hybrid_automaton/mode")

        #         available_modes = self.config['modes']
        #         if current_mode not in available_modes:
        #             raise ValueError(
        #                 current_mode,
        #                 f"Published mode '{current_mode}' is not configured. Available modes: {list(available_modes)}"
        #             )

        #         transitions = available_modes[current_mode].get('transitions', {})
        #         transition_names = list(transitions.keys())

        #         transition_eval.success = True
        #         transition_eval.transition_names = []
        #         transition_eval.transition_values = []
        #         transition_eval.transition_priority = []
        #         error_messages = []

        #         for name in transition_names:
        #             try:
        #                 transition_config = self.config['transitions'][name]
        #                 guard_key = transition_config['guard']
        #                 guard_config = self.config['guards'][guard_key]
        #                 guard_func = guard_config['function']
        #                 state_inputs = [self.config['states'][s]['state'] for s in guard_config['state_inputs']]

        #                 result = bool(guard_func(*state_inputs))
        #                 transition_eval.transition_names.append(name)
        #                 transition_eval.transition_values.append(result)
        #                 transition_eval.transition_priority.append(transitions[name]['priority'])

        #             except Exception as e:
        #                 self.get_logger().error(f"Transition '{name}' guard evaluation failed: {e}")
        #                 error_messages.append(f"{name}: {e}")
        #                 transition_eval.success = False

        #         if error_messages:
        #             transition_eval.error_message = "Errors during evaluation: " + "; ".join(error_messages)

        #         if any(transition_eval.transition_values):
        #             transition_pending.transition_pending = True
        #             self.transition_event.set()

        #     except Exception as e:
        #         publish_error(str(e))
        #         return
            
        # self.transition_eval_pub.publish(transition_eval)
        # self.transition_pending_pub.publish(transition_pending)
    
    def _dynamics_callback(self):
        """updating dynamics"""
        if not self.automaton_active:
            return
        
        return

        # dynamics_update = Dynamics()
        # ros_stamp = self.get_clock().now().to_msg()
        # dynamics_update.stamp = ros_stamp
        # generated_uuid = uuid.uuid4()

        # ros_uuid = UUID()
        # ros_uuid.uuid = list(generated_uuid.bytes)

        # dynamics_update.dynamic_uuid = ros_uuid

        # def publish_error(mode:str, message: str):
        #     dynamics_update.success = False
        #     dynamics_update.error_message = message
        #     dynamics_update.stamp = ros_stamp
        #     self._dynamics_pub.publish(dynamics_update)

        # try:
        #     try: 
        #         current_mode = self.mode.lower()
        #     except Exception as e: 
        #         raise ValueError('Hybrid Automaton Control Mode not received /hybrid_automaton/mode')
            
        #     if current_mode not in [mode for mode in self.config['modes']]:
        #         publish_error(current_mode, f"Current Hybrid Automaton Mode published to /hybrid_automaton/mode: '{current_mode}' is not among Hybrid Automaton Mode configuration: '{[mode for mode in self.config['modes']]}'")
        #         return

        #     dynamics_update.mode = current_mode
        #     self.config['dynamics'][self.config['modes'][current_mode]['dynamics']]
        #     dynamics_update.dynamic_parameters.controller_name = self.config['modes'][current_mode]['dynamics']
        #     dynamics_update.dynamic_parameters.dynamic_name = list(self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['output'].keys())
        #     dynamics_update.dynamic_parameters.dynamic_units = list(self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['output'].values())

        #     dynamic_function =  self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['function']
        #     if 'state_inputs' in  self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]:
        #         state_input_names = self.config['dynamics'][dynamics_update.dynamic_parameters.controller_name]['state_inputs']
        #         state_inputs = [self.config['states'][state_name]['state'] for state_name in state_input_names]
        #         dynamics_update.dynamic_parameters.dynamic_value = dynamic_function(*state_inputs)
        #     else: 
        #         dynamics_update.dynamic_parameters.dynamic_value = dynamic_function()

        #     # dynamics_update.dynamics = dynamics
        #     dynamics_update.success = True
        # except Exception as e:
        #     publish_error(mode='', message=str(f"Exception occured: {e}"))
        #     return
        
        # self._dynamics_pub.publish(dynamics_update)

    """ === Util Functions === """
    def validate_mode(self, mode:str):
        if not isinstance(mode, str):
            raise TypeError('mode is not of correct type string')
        if mode not in self.automaton_modes:
            raise ValueError('current mode is not in automaton modes')


from rclpy.executors import MultiThreadedExecutor
import rclpy

def main():
    rclpy.init()
    node = HybridAutomatonNode(name='hybrid_automaton_node', namespace='hybrid_automaton')
    executor = MultiThreadedExecutor(num_threads=8)

    try:
        executor.add_node(node)
        executor.spin()
    except Exception as e:
        executor.shutdown()
        node.destroy_node()
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()