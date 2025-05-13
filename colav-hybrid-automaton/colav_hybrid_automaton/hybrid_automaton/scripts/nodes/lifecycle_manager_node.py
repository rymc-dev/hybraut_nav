import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from hybrid_automaton_interfaces.action import HybridAutomaton
from colav_interfaces.msg import Waypoints
from unique_identifier_msgs.msg import UUID
from std_msgs.msg import String
from builtin_interfaces.msg import Duration, Time
from rcl_interfaces.msg import ParameterDescriptor
from std_srvs.srv import Trigger
from ament_index_python.packages import get_package_share_directory
import os
import uuid

from hybrid_automaton.utils import (
    validate_timestamps_within_tolerance,
    get_current_ros_time,
    subtract_time,
    load_yml,
    process_automaton_config
)
from hybrid_automaton.config import QOS_PROFILE, HybridAutomatonStatus
from hybrid_automaton_interfaces.msg import Dynamics, TransitionPending, TransitionTimer, DynamicParameter

# Default path to the hybrid automaton config
default_hybrid_automaton_config = os.path.join(
    get_package_share_directory('colav_hybrid_automaton'),
    'config',
    'colav_hybrid_automaton_config.yml'
)

class LifeCycleManager(Node):
    def __init__(self,
                 name: str = 'lifecycle_manager',
                 namespace: str = 'hybrid_automaton'):
        super().__init__(name, namespace=namespace)

        # Declare and load configuration
        self.declare_parameter(
            'hybrid_automaton_config_path',
            value=default_hybrid_automaton_config,
            descriptor=ParameterDescriptor(
                description='Path to the Hybrid Automaton configuration file'
            )
        )
        config_path = self.get_parameter(
            'hybrid_automaton_config_path'
        ).get_parameter_value().string_value
        self.config = process_automaton_config(load_yml(config_path))

        # Transition evaluation frequency
        self.declare_parameter(
            'transition_evaluation_hz',
            value=self.config['params']['transition_evaluation_hz'],
            descriptor=ParameterDescriptor(
                description='Guard evaluation frequency (Hz)'
            )
        )

        # Internal state variables
        self.initial_mode = self.config['init']['mode']
        self.final_modes = self.config['modes_goal']
        self.mission_active = False
        self.mission_start_time = None
        self.automaton_uuid = None
        self.ros_automaton_uuid = None
        self.mode = None
        self.status = None
        self.dynamics = None
        self.time_since_last_transition = None
        self.transition_pending = None
        self.waypoints = None

        # Publishers and subscriptions
        self.mode_publisher = self.create_publisher(
            String,
            '/hybrid_automaton/mode',
            QOS_PROFILE
        )
        self.status_publisher = self.create_publisher(
            String,
            '/hybrid_automaton/status',
            QOS_PROFILE
        )
        self.create_subscription(
            String,
            '/hybrid_automaton/mode',
            lambda msg: setattr(self, 'mode', msg),
            QOS_PROFILE
        )
        self.create_subscription(
            String,
            '/hybrid_automaton/status',
            lambda msg: setattr(self, 'status', msg.data),
            QOS_PROFILE
        )
        self.create_subscription(
            Dynamics,
            '/hybrid_automaton/dynamics',
            lambda msg: setattr(self, 'dynamics', msg),
            QOS_PROFILE
        )
        self.create_subscription(
            TransitionPending,
            '/hybrid_automaton/transition_pending',
            lambda msg: setattr(self, 'transition_pending', msg),
            QOS_PROFILE
        )
        self.create_subscription(
            TransitionTimer,
            '/hybrid_automaton/transition_timer',
            lambda msg: setattr(self, 'time_since_last_transition', msg),
            QOS_PROFILE
        )
        self.create_subscription(
            Waypoints,
            '/hybrid_automaton/state/waypoints',
            lambda msg: setattr(self, 'waypoints', msg),
            QOS_PROFILE
        )

        # Action server
        self._hybrid_automaton_action_server = ActionServer(
            self,
            HybridAutomaton,
            'hybrid_automaton_action_server',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self._cancel_callback
        )

    def goal_callback(self, goal: HybridAutomaton.Goal, 
                      mission_request_tolerance: Duration = Duration(sec=1)):
        try:
            validate_timestamps_within_tolerance(
                goal.stamp,
                get_current_ros_time(),
                Duration(sec=10)
            )
        except Exception as e:
            self.get_logger().error(f"Mission Request Rejected: {e}")
            return GoalResponse.REJECT

        self.mission_start_time = goal.stamp
        self.automaton_uuid = uuid.uuid4()
        self.ros_automaton_uuid = UUID(uuid=list(self.automaton_uuid.bytes))
        self.mission_active = True
        self.get_logger().info('Accepted, Starting Hybrid Automaton...')
        return GoalResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self._current_goal_handle = goal_handle

        # Publish initial mode
        self.mode_publisher.publish(String(data=self.initial_mode))

        # Start underlying services
        for srv_name in [
            '/hybrid_automaton/start_dynamics_eval',
            '/hybrid_automaton/start_transition_eval',
            '/hybrid_automaton/start_transition_engine'
        ]:
            cli = self.create_client(Trigger, srv_name)
            if not cli.wait_for_service(timeout_sec=2.0):
                raise TimeoutError(f"Timeout waiting for {srv_name}")
            future = cli.call_async(Trigger.Request())
            rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
            if not future.done() or not future.result().success:
                raise RuntimeError(f"Service {srv_name} failed to start")

        # Start feedback timer
        hz = self.get_parameter('transition_evaluation_hz').value
        self._feedback_timer = self.create_timer(1.0/hz, self._feedback_timer_callback)

        # Spin until mission_active is cleared
        while self.mission_active:
            rclpy.spin_once(self)

        # Cleanup timer and goal handle
        self.destroy_timer(self._feedback_timer)
        self._current_goal_handle = None

        # Return final result (sends to client)
        result = HybridAutomaton.Result()
        result.success = True
        result.message = 'Mission Completed!'
        return result

    def _feedback_timer_callback(self):
        try:
            # Detect final mode
            if isinstance(self.mode, String) and self.mode.data.lower() in self.final_modes:
                self.get_logger().info(f"In final mode: {self.mode.data}")

            # Completed status -> finalize
            if isinstance(self.status, str) and \
               self.status == HybridAutomatonStatus.COMPLETED.name:
                # Publish final no-op feedback
                fb = HybridAutomaton.Feedback()
                fb.feedback.automaton_uuid = self.ros_automaton_uuid
                fb.feedback.mode = 'FINAL'
                fb.feedback.status = 'COMPLETED'
                fb.feedback.dynamics = DynamicParameter()
                fb.feedback.time_since_last_transition = Duration()
                fb.feedback.transition_pending = TransitionPending()
                stamp = get_current_ros_time()
                fb.feedback.stamp = stamp
                fb.feedback.elapsed_time = subtract_time(
                    stamp, self.mission_start_time
                )
                fb.feedback.waypoints = Waypoints()
                fb.feedback.error = False
                fb.feedback.message = ''

                self._current_goal_handle.publish_feedback(fb)
                self._current_goal_handle.succeed()
                self.mission_active = False
                return

            # Normal feedback loop
            fb = HybridAutomaton.Feedback()
            fb.feedback.automaton_uuid = self.ros_automaton_uuid
            fb.feedback.mode = self.mode.data if self.mode is not None else ''
            fb.feedback.status = self.status if self.status is not None else 'IDLE'
            fb.feedback.dynamics = (
                self.dynamics.dynamic_parameters
                if self.dynamics is not None else DynamicParameter()
            )
            fb.feedback.time_since_last_transition = (
                self.time_since_last_transition
                if self.time_since_last_transition is not None else Duration()
            )
            fb.feedback.transition_pending = (
                self.transition_pending
                if self.transition_pending is not None else TransitionPending()
            )
            stamp = get_current_ros_time()
            fb.feedback.stamp = stamp
            fb.feedback.elapsed_time = subtract_time(
                stamp, self.mission_start_time
            )
            fb.feedback.waypoints = (
                self.waypoints if self.waypoints is not None else Waypoints()
            )
            fb.feedback.error = False
            fb.feedback.message = ''
            self._current_goal_handle.publish_feedback(fb)
        except Exception as e:
            self.get_logger().error(f"Error in feedback callback: {e}")

    def _cancel_callback(self, goal_handle):
        self.get_logger().info('Received request to cancel goal')
        self.mission_active = False
        return CancelResponse.ACCEPT


def main(args=None):
    rclpy.init(args=args)
    node = LifeCycleManager()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()