from transitions import Machine
import rclpy
from rclpy.node import Node
from rclpy.timer import Timer
from hybraut_model import HybridAutomaton

from rclpy.subscription import Subscription
from rclpy.publisher import Publisher

from rclpy.qos import QoSProfile, qos_profile_default
from rclpy.callback_groups import ReentrantCallbackGroup

from hybraut_interfaces.srv import TriggerTransition
from std_srvs.srv import Trigger

from rclpy.clock import Clock, ClockType
from builtin_interfaces.msg import Duration
from rclpy.callback_groups import CallbackGroup

from hybraut_executor_watchdog import FSM


SYSTEM_CLOCK: Clock = None

class AutomatonExecutor(FSM):

    state_name_map = {
        "INACTIVE": 0,
        "ACTIVE": 1
    }
    states = list(state_name_map.keys())
    
    state = "inactive"

    transition_evaluation_frequency: int = 1.0
    invariant_evaluation_frequency: int = 1.0
    dynamics_evaluation_frequency: int = 1.0

    current_mode: int = 0
    automaton_model: HybridAutomaton

    trigger_transition_pub: Publisher
    transition_engine_sub: Subscription

    transition_evaluator_timer: Timer
    invariant_evaluator_timer: Timer
    dynamics_evaluation_timer: Timer

    def __init__(self, node: Node, amdl: dict):
        
        super().__init__(node=node, cb_group=ReentrantCallbackGroup(), qos=QoSProfile(depth=10))
        self.error_count = 0
        self.recovery_attempts = 0

        self._automaton_model = HybridAutomaton.register_automaton(
            node=node,
            amdl_dict=amdl
        )

        self._node = node

        self.machine = Machine(
            model=self,
            states=AutomatonExecutor.states,
            initial="INACTIVE"
        )
        self.machine.add_transition(
            trigger="activate_automaton", 
            source="INACTIVE", 
            dest="ACTIVE",
            before="on_before_activate",
            after="on_after_activate" 
        )
        self.machine.add_transition(
            trigger="deactivate_automaton", 
            source="ACTIVE", 
            dest="INACTIVE",
            before="on_before_deactivate",
            after="on_after_deactivate"
        )
        
        self._clock = Clock(clock_type=ClockType.ROS_TIME)
        self._activation_time = None

        self.transition_evaluator_timer: Timer = node.create_timer(
            timer_period_sec= (1.0 / self.transition_evaluation_frequency),
            callback=self._transition_evaluation_callback,
            callback_group=ReentrantCallbackGroup(),
            autostart=False,
            clock=SYSTEM_CLOCK
        )

        self.invariant_evaluator_timer: Timer = node.create_timer(
            timer_period_sec= (1.0 / self.invariant_evaluation_frequency),
            callback=self._invariant_evaluation_callback,
            callback_group=ReentrantCallbackGroup(),
            autostart=False,
            clock=SYSTEM_CLOCK
        ) 

        self.dynamics_evaluation_timer: Timer = node.create_timer(
            timer_period_sec= (1.0 / self.dynamics_evaluation_frequency),
            callback=self._dynamics_evaluation_callback,
            callback_group=ReentrantCallbackGroup(),
            autostart=False,
            clock=SYSTEM_CLOCK
        )

    def toggle(self):
        if self.state == "INACTIVE":
            self.activate_automaton()
            self._node.get_logger().info('activating automaton executor...')
        elif self.state == "ACTIVE":
            self.deactivate_automaton()
            self._node.get_logger().info('deactivating automaton executor...')
        else:
            self._node.get_logger().warn(f"Unknown state: {self.state}")

    def _initialize_system_states(self, qos: QoSProfile = qos_profile_default, cb_group: CallbackGroup = ReentrantCallbackGroup()):
        """ 
        system states which automaton model automatically subscribes to and can utilize for guards and such.
        """
        system_state_namespace = "/automaton/system_state"
        system_state_topics = [
            "time_since_last_transition",
            "time_in_current_mode",
            "last_evaluation_time",
            "time_since_activation",
            "transition_timeout"
        ]
        for topic in system_state_topics:
            pub = self._node.create_publisher(
                msg_type=Duration,
                topic="/automaton/system_state/time_since_last_transition",
                qos_profile=qos,
                callback_group=cb_group
            )
            self.__setattr__(
                f"{system_state_namespace}/{topic}_pub",
                pub
            )

    def on_before_activate(self):
        
        self._activation_time = self._clock.now()
        self.transition_evaluator_timer.reset()
        self.invariant_evaluator_timer.reset()
        self.dynamics_evaluation_timer.reset()

    def on_after_activate(self):
        self._initialize_services()

    def on_before_deactivate(self):
        self.transition_evaluator_timer.cancel()
        self.invariant_evaluator_timer.cancel()
        self.dynamics_evaluation_timer.cancel()

    def on_after_deactivate(self):
        self._shutdown_services()
        self._activation_time = None

    def _initialize_services(self):
        self._transition_engine_srv = self._node.create_service(
            srv_type=TriggerTransition,
            srv_name='/automaton/trigger_transition',
            callback=self._transition_engine_callback,
            qos_profile=qos_profile_default,
            callback_group=ReentrantCallbackGroup()
        )

        self._enforce_invariant_srv = self._node.create_service(
            srv_type=Trigger,
            srv_name='/automaton/enforce_invariant',
            callback=self._invariant_enforcement_callback,
            qos_profile=qos_profile_default,
            callback_group=ReentrantCallbackGroup()
        )

    def _shutdown_services(self):
        if hasattr(self, '_transition_engine_srv'):
            self._node.destroy_service(self._transition_engine_srv)
            del self._transition_engine_srv

        if hasattr(self, '_enforce_invariant_srv'):
            self._node.destroy_service(self._enforce_invariant_srv)
            del self._enforce_invariant_srv

    def _transition_evaluation_callback(self):
        if self._activation_time is not None:
            now = self._clock.now()
            elapsed = now - self._activation_time
            self._node.get_logger().info(
                f"transition evaluations... Elapsed time since activation: {elapsed.nanoseconds / 1e9:.2f} seconds"
            )

    def _invariant_evaluation_callback(self):
        if self._activation_time is not None:
            now = self._clock.now()
            elapsed = now - self._activation_time
            self._node.get_logger().info(
                f"invariant evaluations... Elapsed time since activation: {elapsed.nanoseconds / 1e9:.2f} seconds"
            )

    def _dynamics_evaluation_callback(self):
        if self._activation_time is not None:
            now = self._clock.now()
            elapsed = now - self._activation_time
            self._node.get_logger().info(
                f"dynamics evaluation... Elapsed time since activation: {elapsed.nanoseconds / 1e9:.2f} seconds"
            )

    def _transition_engine_callback(self):
        pass

    def _invariant_enforcement_callback(self):
        pass


    """ === on Transition Functions === """

    def on_recoverable_error(self, event):
        """Override to add error tracking."""
        # Call parent implementation first
        super().on_recoverable_error(event)
        
        # Add custom behavior
        self.error_count += 1
        self.node.get_logger().info(f"Total errors encountered: {self.error_count}")
        
        # Perform additional error analysis
        if self.error_count > 5:
            self.node.get_logger().warning("High error count detected!")

    def on_attempt_fix(self, event):
        """Override to add recovery attempt tracking."""
        # Call parent implementation
        super().on_attempt_fix(event)
        
        # Add custom behavior
        self.recovery_attempts += 1
        self.node.get_logger().info(f"Recovery attempt #{self.recovery_attempts}")

    def pre_guard_enabled(self, event):
        """Hook called before guard enabled logic."""
        self.node.get_logger().info("Preparing for guard activation...")

    def post_mission_complete(self, event):
        """Hook called after mission complete logic."""
        self.node.get_logger().info(f"Mission statistics: {self.error_count} errors, {self.recovery_attempts} recoveries")

    def _execute_shutdown_logic(self, event):
        """Custom shutdown logic."""
        self.node.get_logger().info("Performing custom cleanup before shutdown...")
        # Add custom cleanup code here

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
from utils import load_yml

def main():

    rclpy.init()
    node = Node('mock_node')
    executor = MultiThreadedExecutor(num_threads=4)
    thread = threading.Thread(target=executor.spin)
    thread.start()
    
    executor.add_node(node)
    
    automaton = load_yml('/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml')

    automaton_runtime = AutomatonExecutor(
        node=node,
        amdl=automaton
    )
    automaton_runtime.toggle()
    import time
    time.sleep(10.0)
    automaton_runtime.toggle()

    rclpy.shutdown()

if __name__ == '__main__':
    main()
