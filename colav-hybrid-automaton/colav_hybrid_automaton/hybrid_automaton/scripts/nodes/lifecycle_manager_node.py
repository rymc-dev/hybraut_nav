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
import threading
import uuid
from rclpy.executors import MultiThreadedExecutor

from hybrid_automaton.utils import (
    validate_timestamps_within_tolerance,
    get_current_ros_time,
    subtract_time,
    load_yml,
    process_automaton_config
)
from hybrid_automaton.config import QOS_PROFILE, HybridAutomatonStatus
from hybrid_automaton_interfaces.msg import Dynamics, TransitionPending, TransitionTimer, DynamicParameter
from threading import Event, Lock, Thread
import time
import asyncio
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup

# Default path to the hybrid automaton config
default_hybrid_automaton_config = os.path.join(
    get_package_share_directory('colav_hybrid_automaton'),
    'config',
    'colav_hybrid_automaton_config.yml'
)

automaton_srv_names = [
    '/hybrid_automaton/start_dynamics_eval',
    '/hybrid_automaton/start_transition_eval',
    '/hybrid_automaton/start_transition_engine'
]
automaton_clis = [

]

class LifeCycleManager(Node):
    def __init__(self,
                 name: str = 'lifecycle_manager',
                 namespace: str = 'hybrid_automaton'):
        super().__init__(name, namespace=namespace)

        state_io_callback_group = ReentrantCallbackGroup()
        cli_callback_group = ReentrantCallbackGroup()
        hybrid_automaton_start_callback_group = ReentrantCallbackGroup()
        automaton_feedback_callback_group_timer = ReentrantCallbackGroup()
        action_server_callback_group = MutuallyExclusiveCallbackGroup()

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

        for srv_name in automaton_srv_names:
            cli = self.create_client(Trigger, srv_name, callback_group=cli_callback_group)
            if not cli.wait_for_service(timeout_sec=2.0):
                raise TimeoutError(f"Timeout waiting for {srv_name}")
            automaton_clis.append(cli)

        # Internal state variables
        self.initial_mode = self.config['init']['mode']
        self.final_modes = self.config['modes_goal']
        self.automaton_active_event = Event()
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
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.status_publisher = self.create_publisher(
            String,
            '/hybrid_automaton/status',
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.waypoint_publisher = self.create_publisher(
            Waypoints,
            '/hybrid_automaton/state/waypoints',
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.create_subscription(
            String,
            '/hybrid_automaton/mode',
            lambda msg: setattr(self, 'mode', msg),
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.create_subscription(
            String,
            '/hybrid_automaton/status',
            lambda msg: setattr(self, 'status', msg.data),
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.create_subscription(
            Dynamics,
            '/hybrid_automaton/dynamics',
            lambda msg: setattr(self, 'dynamics', msg),
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.create_subscription(
            TransitionPending,
            '/hybrid_automaton/transition_pending',
            lambda msg: setattr(self, 'transition_pending', msg),
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.create_subscription(
            TransitionTimer,
            '/hybrid_automaton/transition_timer',
            lambda msg: setattr(self, 'time_since_last_transition', msg),
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )
        self.create_subscription(
            Waypoints,
            '/hybrid_automaton/state/waypoints',
            lambda msg: setattr(self, 'waypoints', msg),
            QOS_PROFILE,
            callback_group=state_io_callback_group
        )

        self._automaton_trigger = False
        self._automaton_trigger_lock = False
        self._automaton_started_event = False

        self._feedback_active_event = Event()
        self._feedback_active_lock = Lock()

        self.create_timer(
            1.0,
            self._service_worker,
            callback_group=hybrid_automaton_start_callback_group
        )

        # Action server
        self._hybrid_automaton_action_server = ActionServer(
            self,
            HybridAutomaton,
            'hybrid_automaton_action_server',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            callback_group=action_server_callback_group
        )

    def _service_worker(self):
        # check if the automaton has been triggered to start
        if not self._automaton_trigger_lock:
            self._automaton_trigger_lock = True

            if not self._automaton_trigger:
                self._automaton_trigger_lock = False
                return
            
            self._automaton_trigger = False

            try:
                for idx, client in enumerate(automaton_clis):

                    service_name = automaton_srv_names[idx]
                    req = Trigger.Request()
                    fut = client.call_async(req)

                    # we can spin here or just wait on the future
                    rclpy.spin_until_future_complete(self, fut, timeout_sec=1.0)
                    if not fut.done():
                        self.get_logger().error(f"timeout on {service_name}")
                        continue

                    resp = fut.result()
                    if not resp.success:
                        self.get_logger().error(f"{service_name} failed: {resp.message}")
                    else:
                        self.get_logger().info(f"{service_name} succeeded")
            except Exception as e:
                self.get_logger().error('error occured starting hybrid automaton services')
            finally: 
                self._automaton_started_event = True
                self._automaton_trigger_lock = False
                return


    def goal_callback(
        self, 
        goal_handle: HybridAutomaton.Goal, 
        mission_request_tolerance: Duration = Duration(sec=1)
    ) -> GoalResponse:
        """Callback function triggered upon receiving a new mission goal for the Hybrid Automaton."""

        try:
            # Validate that the mission timestamp is within an acceptable range of the current ROS time
            validate_timestamps_within_tolerance(
                goal_handle.stamp,
                get_current_ros_time(),
                Duration(sec=10)  # Hard-coded for now, consider using mission_request_tolerance instead
            )

            # TODO: Add validation logic for the received waypoint, e.g., bounds or format checking
            
            # Store mission context
            self.mission_start_time = goal_handle.stamp
            self.automaton_uuid = uuid.uuid4()
            self.ros_automaton_uuid = UUID(uuid=list(self.automaton_uuid.bytes))

            # Publish initial waypoint
            initial_waypoints = Waypoints(waypoints=[goal_handle.goal_waypoint])
            self.waypoint_publisher.publish(initial_waypoints)
            

        except Exception as e:
            self.get_logger().error(f"Mission Request Rejected: {e}")
            return GoalResponse.REJECT
        
        self.get_logger().info("Mission request accepted. Hybrid Automaton starting mission.")
        return GoalResponse.ACCEPT
 
    def start_automaton_srvs(self, goal_handle):
        self._current_goal_handle = goal_handle
        self._automaton_trigger = True
        time.sleep(1.0)
        if not self._automaton_started_event:
            self.get_logger().error("Timeout occurred waiting for automaton to start.")
        else:
            self.get_logger().info("Automaton started successfully.")

    def execute_callback(self, goal_handle):
        """This is the callback function when the hybrid automaton mission request has been received"""

        self.get_logger().info("Hybrid Automaton mission goal received.")

        thread = threading.Thread(
            target=self.start_automaton_srvs, 
            args=(goal_handle,), 
            daemon=True  # optional: don't use daemon if you need to wait reliably
        )
        thread.start()


        self.mode_publisher.publish(String(data=self.initial_mode))
        
        # await self.feedback_executor()
        goal_handle.succeed()
        result = HybridAutomaton.Result(success=True, message='Mission Complete')
        self.automaton_active_event.clear()
        return result
    
    # async def feedback_executor(self):
    #     self.automaton_active_event.set()
    #     hz = self.get_parameter('transition_evaluation_hz').value
    #     self._feedback_timer = self.create_timer(1.0 / hz, self._feedback_timer_callback)
    #     while self.automaton_active_event.is_set():
    #         rclpy.spin_once(self, timeout_sec=0.1)
    #     self.destroy_timer(self._feedback_timer)
    #     return

    # def _feedback_timer_callback(self):
    #     try:
    #         # Detect final mode
    #         if isinstance(self.mode, String) and self.mode.data.lower() in self.final_modes:
    #             self.get_logger().info(f"In final mode: {self.mode.data}")

    #         # Completed status -> finalize
    #         if isinstance(self.status, str) and \
    #            self.status == HybridAutomatonStatus.COMPLETED.name:
    #             # Publish final no-op feedback
    #             fb = HybridAutomaton.Feedback()
    #             fb.feedback.automaton_uuid = self.ros_automaton_uuid
    #             fb.feedback.mode = 'FINAL'
    #             fb.feedback.status = 'COMPLETED'
    #             fb.feedback.dynamics = DynamicParameter()
    #             fb.feedback.time_since_last_transition = Duration()
    #             fb.feedback.transition_pending = TransitionPending()
    #             stamp = get_current_ros_time()
    #             fb.feedback.stamp = stamp
    #             fb.feedback.elapsed_time = subtract_time(
    #                 stamp, self.mission_start_time
    #             )
    #             fb.feedback.waypoints = Waypoints()
    #             fb.feedback.error = False
    #             fb.feedback.message = ''

    #             self._current_goal_handle.publish_feedback(fb)
    #             self._current_goal_handle.succeed()
    #             self.automaton_active_event.clear()
    #             return

    #         # Normal feedback loop
    #         fb = HybridAutomaton.Feedback()
    #         fb.feedback.automaton_uuid = self.ros_automaton_uuid
    #         fb.feedback.mode = self.mode.data if self.mode is not None else ''
    #         fb.feedback.status = self.status if self.status is not None else 'IDLE'
    #         fb.feedback.dynamics = (
    #             self.dynamics.dynamic_parameters
    #             if self.dynamics is not None else DynamicParameter()
    #         )
    #         fb.feedback.time_since_last_transition = (
    #             self.time_since_last_transition
    #             if self.time_since_last_transition is not None else Duration()
    #         )
    #         fb.feedback.transition_pending = (
    #             self.transition_pending
    #             if self.transition_pending is not None else TransitionPending()
    #         )
    #         stamp = get_current_ros_time()
    #         fb.feedback.stamp = stamp
    #         fb.feedback.elapsed_time = subtract_time(
    #             stamp, self.mission_start_time
    #         )
    #         fb.feedback.waypoints = (
    #             self.waypoints if self.waypoints is not None else Waypoints()
    #         )
    #         fb.feedback.error = False
    #         fb.feedback.message = ''
    #         self._current_goal_handle.publish_feedback(fb)
    #     except Exception as e:
    #         self.get_logger().error(f"Error in feedback callback: {e}")
    #         self.automaton_active_event.clear()

    # def _cancel_callback(self, goal_handle):
    #     self.get_logger().info('Received request to cancel goal')
    #     self.mission_active = False
    #     return CancelResponse.ACCEPT

from rclpy.executors import MultiThreadedExecutor

def main(args=None):
    rclpy.init(args=args)
    node = LifeCycleManager()
    executor = MultiThreadedExecutor(num_threads=6)
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()