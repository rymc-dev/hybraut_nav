from rclpy.lifecycle import Node, State, TransitionCallbackReturn
from rclpy.callback_groups import ReentrantCallbackGroup
from hybrid_automaton.config.qos_config import QOS_PROFILE
from rcl_interfaces.msg import ParameterDescriptor
from std_msgs.msg import String
from hybrid_automaton.utils import create_state_subscriptions
from hybrid_automaton.utils import load_yml, process_automaton_config

class AutomatonManagedNode(Node):
     
    def __init__(self, node_name: str, namespace: str, **kwargs) -> None:
        """
        Initialize the managed node with default parameters and attributes.
        """
        super().__init__(node_name, namespace=namespace, **kwargs)

        self.config_file_path = ""
        self.config = None
        self.eval_hz = 1.0
        self.activate = False
        self.mode = ""

        self.topic_callback_group = ReentrantCallbackGroup()
        self.feedback_callback_group = ReentrantCallbackGroup()

        self.declare_parameter(
            'config_yml_path',
            value=self.config_file_path,
            descriptor=ParameterDescriptor(
                description="Absolute path to the Hybrid Automaton configuration file (.yml format)."
            )
        )
        self.declare_parameter(
            'transition_evaluation_hz',
            value=self.eval_hz,
            descriptor=ParameterDescriptor(
                description="Frequency (in Hz) at which transition conditions are evaluated."
            )
        )

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """
        Called during lifecycle configure transition. Sets up subscriptions and configuration.
        """
        self.get_logger().info(f"Configuring base node {self.get_name()}")

        try:
            self.config_file_path = self.get_parameter('config_yml_path').value
            self.eval_hz = self.get_parameter('transition_evaluation_hz').value

            self.config = load_yml(
                self.get_parameter('config_yml_path').get_parameter_value().string_value
            )
            self.config = process_automaton_config(self.config)

            self.mode_sub = self.create_subscription(
                msg_type=String,
                topic='/hybrid_automaton/mode',
                callback=lambda msg: setattr(self, 'mode', msg.data),
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
            )

            create_state_subscriptions(node=self)

        except Exception as e:
            self.get_logger().error(f"Configuration failed: {e}")
            return TransitionCallbackReturn.FAILURE

        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """
        Called during lifecycle activate transition.
        """
        self.activate = True
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: State) -> TransitionCallbackReturn: 
        """
        # Deactivate puts hybrid automaton system in which it will be in until the next waypoint is received by the 
        mission manager
        Called during lifecycle deactivate transition.
        """
        self.activate = False
        self.mode = ""

        return TransitionCallbackReturn.SUCCESS
    
    def on_cleanup(self, state):
        """return to unconfigured state for when configuration is done to hybrid automaton config"""
        self.activate = False
        self.mode = ""
        self.config_file_path = ""
        self.eval_hz = 1.0
        self.config = None
        self.destroy_subscription(self.mode_sub)
        self.mode_sub = None
        
        return super().on_cleanup(state)

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        """
        Called during lifecycle shutdown transition.
        """
        self.get_logger().info(f"Shutting down base node {self.get_name()}")

        try:            
            for publisher in self._publishers:
                self.destroy_publisher(publisher)

            for subscription in self._subscriptions:
                self.destroy_subscription(subscription)
            
            for timer in self._timers:
                self.destroy_timer(timer) 

            for service in self._services:
                self.destroy_service(service)
            
            for client in self._clients:
                self.destroy_client(client)
        except Exception as e:
            self.get_logger().error(
                f"Transition to 'shutdown' failed for node '{self.get_name()}' while in state '{state.label}'. "
                f"Exception: {str(e)}. Aborting transition."
            )
            return TransitionCallbackReturn.FAILURE

        return TransitionCallbackReturn.SUCCESS
