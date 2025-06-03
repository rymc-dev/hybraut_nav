import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor 
from lifecycle_msgs.srv import GetState
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState
from hybrid_automaton_interfaces.action import HybridAutomaton
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from hybrid_automaton.config import HybridAutomatonMissionProfile 
from hybrid_automaton.utils import is_timestamps_within_tolerance
from colav_interfaces.msg import Waypoints, Waypoint
import time
import threading
from builtin_interfaces.msg import Duration
from rclpy.action.server import ServerGoalHandle
from unique_identifier_msgs.msg import UUID
from rclpy.guard_condition import GuardCondition
from rclpy.timer import Timer
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from lifecycle_msgs.msg import State
from hybrid_automaton.config import HybridAutomatonStatus
from hybrid_automaton_interfaces.msg import Output
from std_msgs.msg import String
from hybrid_automaton_interfaces.msg import Dynamics
from hybrid_automaton.config import QOS_PROFILE
from hybrid_automaton_interfaces.msg import DynamicParameter
from colav_interfaces.msg import Waypoints

SYSTEM_CLOCK = None

class HybridAutomatonMissionControlNode(Node):
    
    def __init__(
        self,
        name: str,
        namespace: str
    ):
        super().__init__(name, namespace=namespace)

        self._current_mode = "IDLE"
        self._current_status = "INITIALIZING"
        self._current_dynamics = None
        self._current_waypoints = None

        self.create_subscription(
            msg_type=String,
            topic='/hybrid_automaton/mode',
            callback=lambda msg: self.__setattr__('_current_mode', msg.data.lower()),
            callback_group=ReentrantCallbackGroup(),
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            msg_type=String,
            topic='/hybrid_automaton/status',
            callback=lambda msg: self.__setattr__('_current_status', msg.data.lower()),
            callback_group=ReentrantCallbackGroup(),
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            msg_type=Dynamics,
            topic='/hybrid_automaton/dynamics',
            callback=lambda msg: self.__setattr__('_current_dynamics', msg),
            callback_group=ReentrantCallbackGroup(),
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            msg_type=Waypoints,
            topic='/hybrid_automaton/state/waypoints',
            callback=lambda msg: self.__setattr__('_current_waypoints', msg),
            callback_group=ReentrantCallbackGroup(),
            qos_profile=QOS_PROFILE
        )

        self._state_cli = self.create_client(
            srv_type=GetState,
            srv_name='/colav/hybrid_automaton/lifecycle/get_state'
        )
        if not self._state_cli.wait_for_service(timeout_sec=30.0):
            self.get_logger().error('/colav/hybrid_automaton/lifecycle/get_state: srv not available!')

        self._change_state_cli = self.create_client(
            srv_type=ChangeState,
            srv_name='/colav/hybrid_automaton/lifecycle/change_state'
        )
        if not self._change_state_cli.wait_for_service(timeout_sec=30.0):
            self.get_logger().error('/colav/hybrid_automaton/lifecycle/get_state: srv not available!')
        
        self._automaton_params_setter_cli = self.create_client(
            srv_type=SetParameters,
            srv_name='/colav/hybrid_automaton/lifecycle/set_parameters'
        )
        if not self._automaton_params_setter_cli.wait_for_service(timeout_sec=30.0):
            self.get_logger().error('/colav/hybrid_automaton/lifecycle/set_parameters: srv not available!')

        self._default_configuration_path = '/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav-hybrid-automaton/colav_hybrid_automaton/config/colav_hybrid_automaton_config.yml'
        self._default_evaluation_frequency = 10
        self._default_control_frequency = 100
        self._current_goal_waypoint:Waypoint = None

        self._activate_automaton:GuardCondition = self.create_guard_condition(
            self._activate_automaton_callback,
            callback_group=MutuallyExclusiveCallbackGroup()
        )
        self._activating_automaton_lock:threading.Lock = threading.Lock()

        self._action_server_feedback_timer = self.create_timer(
            0.1,
            self._action_server_feedback_timer_callback,
            callback_group=ReentrantCallbackGroup(),
            autostart=False
        )

        future = self._automaton_params_setter_cli.call_async(
            SetParameters.Request(
                parameters=[
                    Parameter(
                        name='configuration_path', 
                        value=ParameterValue(type=ParameterType.PARAMETER_STRING, string_value=self._default_configuration_path)
                    ),
                    Parameter(
                        name='evaluation_frequency',
                        value=ParameterValue(type=ParameterType.PARAMETER_INTEGER, integer_value=self._default_evaluation_frequency)
                    ),
                    Parameter(
                        name='control_frequency',
                        value=ParameterValue(type=ParameterType.PARAMETER_INTEGER, integer_value=self._default_control_frequency)
                    )
            ]))
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.done():
            if not all(result.successful for result in future.result().results):
                self.get_logger().error('setting params failed for configuration')

        # Transition to inactive state
        future = self._change_state_cli.call_async(
            ChangeState.Request(transition=Transition(id=Transition.TRANSITION_CONFIGURE))
        )
        rclpy.spin_until_future_complete(self,future, timeout_sec=5.0)
        if future.done():
            if not future.result().success:
                self.get_logger().error('transition request to configure for hybrid automaton lifecycle failed')


        self._goal_handle = None
        self._goal_lock = threading.Lock()
        self._hybrid_automaton_action_server = ActionServer(
            self,
            HybridAutomaton,
            'hybrid_automaton_action_server',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            handle_accepted_callback=self.handle_accepted_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )
        self.get_logger().info(f"{namespace}/{name}: initialized")

    def _activate_automaton_callback(self):
        self._activating_automaton_lock.acquire()

        try:
            # check current state is inactivate
            # if not in active state trigger cancel log that lifecycle is in wrong state for activating automaton
            future = self._state_cli.call_async(request=GetState.Request())
            try:
                rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
            except Exception as e: 
                pass
            finally:
                if not future.done():
                    self.get_logger().warning('error occured during the callback for _activate_automaton_callback to get the current hybrid automaton state')
                    self._goal_handle.is_cancel_requested = True
            
            future_response:GetState.Response = future.result()
            if not future_response.current_state.id == State.PRIMARY_STATE_INACTIVE:
                self.get_logger().warning("error occured during callback to state automaton, need to be in lifecycle state inactive to transition to activate")

            future = self._automaton_params_setter_cli.call_async(
                SetParameters.Request(
                    parameters=[
                        Parameter(
                            name='waypoint_x', 
                            value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=self._current_goal_waypoint.position.x)
                        ),
                        Parameter(
                            name='waypoint_y',
                            value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=self._current_goal_waypoint.position.y)
                        ),
                        Parameter(
                            name='waypoint_acceptance_radius',
                            value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=self._current_goal_waypoint.acceptance_radius)
                        )
            ]))
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            if future.done():
                if not all(result.successful for result in future.result().results):
                    self.get_logger().error('setting params failed for configuration')

            # set param for goal waypoint x,y and acceptance radius based on the self_goal_waypoint
            future = self._change_state_cli.call_async(request=ChangeState.Request(
                transition=Transition(id=Transition.TRANSITION_ACTIVATE)
            ))

            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            if future.done():
                if not future.result().success:
                    self.get_logger().error('transition request to configure for hybrid automaton lifecycle failed')
            # call the change state service to move to activate
            future = self._state_cli.call_async(request=GetState.Request())
            try:
                rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
            except Exception as e: 
                pass
            finally:
                if not future.done():
                    self.get_logger().warning('error occured during the callback for _activate_automaton_callback to get the current hybrid automaton state')
                    self._goal_handle.is_cancel_requested = True

            future_response:GetState.Response = future.result()
            if not future_response.current_state.id == State.PRIMARY_STATE_ACTIVE:
                self.get_logger().warning("error occured during callback to state automaton, need to be in lifecycle state inactive to transition to activate")
            # release lock and trigger the timer which monitors the automatons lifecycle state to ensure it is still in active.
        except Exception as e:
            self.get_logger().error(f"Exception occured while starting hybrid automaton: {str(e)}")

        self.get_logger().info('Hybrid automaton activated')

    def _deactivate_automaton_callback(self):
        pass


    def destroy(self):
        self._hybrid_automaton_action_server.destroy()
        super().destroy_node()

    def goal_callback(self, goal_request: HybridAutomaton.Goal):
        """Accept or reject a client request to begin an action."""
        self.get_logger().info('Received goal request')

        goal_response = GoalResponse.ACCEPT
        try:
            # Validate goal_request
            uuid_attrs = ['mission_uuid', 'agent_uuid'] # UUID Validation
            for uuid_attr in uuid_attrs:
                if not any(byte != 0 for byte in getattr(goal_request, uuid_attr).uuid):
                    self.get_logger().warning(f"invalid {uuid_attr} set for goal_request.")
                    goal_response = GoalResponse.REJECT

            if not any((goal_request.mission_profile == profile.name for profile in HybridAutomatonMissionProfile)):
                self.get_logger().warning(f"invalid mission profile: '{goal_request.mission_profile}', must be one of the current available mission profiles: '{[profile.name for profile in HybridAutomatonMissionProfile]}'.")
                goal_response = GoalResponse.REJECT

            if not is_timestamps_within_tolerance(self.get_clock().now().to_msg(), goal_request.stamp, Duration(sec=2)):
                self.get_logger().warning(f"invalid mission stamp. time request received: {goal_request._stamp}, time now: {self.get_clock().now().to_msg()}, Tolerance: {Duration(sec=1)}, suggests issues with clients of clock synchronization")
                goal_response = GoalResponse.REJECT
            
            if not len(goal_request.goal_waypoints.waypoints) > 0:
                self.get_logger().warning(f"invalid goal waypoints received: '{goal_request.goal_waypoints}'.")
                goal_response = GoalResponse.REJECT

            if any([goal_waypoint.acceptance_radius < 0.5 for goal_waypoint in goal_request.goal_waypoints.waypoints]): # Validate acceptance radiuses for goal_waypoints > 0.5
                self.get_logger().warning(
                    f"Invalid goal waypoints received: each waypoint must have an acceptance radius greater than 0.5 meters. Received: {goal_request.goal_waypoints}"
                )
                goal_response = GoalResponse.REJECT
        except Exception as e:
            self.get_logger().error(f"exception occured during hybrid automaton request validation: '{str(e)}'")
            goal_response = GoalResponse.REJECT
        
        self.get_logger().info(f"Goal {goal_response.name.lower()}ed.")
        return goal_response

    def handle_accepted_callback(self, goal_handle: ServerGoalHandle):
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

    def cancel_callback(self, goal):
        """Accept or reject a client request to cancel an action."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    def _action_server_feedback_timer_callback(self):
        # This timer is going to execute simultaneously to execute callback parsing the hybrid automaton data
        # into a format that can that can be returned to the server cli.
        feedback_msg = HybridAutomaton.Feedback()
        feedback_msg.feedback = Output(
            mode=self._current_mode,
            status=self._current_status,
            dynamics=DynamicParameter() if self._current_dynamics is None else self._current_dynamics.dynamic_parameters,
            waypoints=Waypoints() if self._current_waypoints is None else self._current_waypoints,
            stamp=self.get_clock().now().to_msg()
        )
        self._goal_handle.publish_feedback(feedback_msg) 

    
    def execute_callback(self, goal_handle: ServerGoalHandle):
        """Execute the goal."""
        self.get_logger().info(f"Executing goal. Mission is to sequentially navigate to each of the goal waypoints: '{goal_handle._goal_request.goal_waypoints.waypoints}'")

        # Append the seeds for the Fibonacci sequence
        self._current_status = HybridAutomatonStatus.INITIALIZING.name
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

    


    # async def _goal_callback(self, goal_handle):
    #     goal_handle.pass

    # async def _execute_callback(self, goal_handle):
    #     pass


def main():
    rclpy.init()
    node = HybridAutomatonMissionControlNode(name='manager', namespace='colav/hybrid_automaton')
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