import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from hybrid_automaton_interfaces.action import HybridAutomaton
from rclpy.action import GoalResponse, CancelResponse
from hybrid_automaton.utils import validate_timestamps_within_tolerance
from builtin_interfaces.msg import Duration
from hybrid_automaton.utils import get_current_ros_time
import time
from std_msgs.msg import String
from hybrid_automaton.config import QOS_PROFILE
import uuid
from unique_identifier_msgs.msg import UUID
from hybrid_automaton_interfaces.msg import Dynamics, TransitionPending, Waypoints, TransitionTimer, DynamicParameter
from hybrid_automaton.utils import subtract_time
from builtin_interfaces.msg import Time
from ament_index_python.packages import get_package_share_directory
import os
from hybrid_automaton.utils import load_yml, process_automaton_config
from rcl_interfaces.msg import ParameterDescriptor
from std_srvs.srv import Trigger

default_hybrid_automaton_config = os.path.join(get_package_share_directory('colav_hybrid_automaton'), 'config', 'colav_hybrid_automaton_config.yml')

class LifeCycleManager(Node):
    def __init__(self, name: str = 'lifecycle_manager', namespace: str = 'hybrid_automaton'):
        super().__init__(name, namespace=namespace)
        self.declare_parameter(
            'hybrid_automaton_config_path',
            value=default_hybrid_automaton_config,
            descriptor=ParameterDescriptor(description='Path to the Hybrid Automaton configuration file')
        )
        # Load automaton configuration
        self.config = load_yml(
            self.get_parameter('hybrid_automaton_config_path').get_parameter_value().string_value
        )
        self.config = process_automaton_config(self.config)

        self.declare_parameter(
            'transition_evaluation_hz',
            value=self.config['params']['transition_evaluation_hz'],
            descriptor=ParameterDescriptor(description='transition evaluation hz for guard evaluations')
        )

        self.mission_active = False 
        self.initial_mode = self.config['init']['mode']
        self.final_modes = self.config['modes_goal']
        
        self.mode_publisher = self.create_publisher(
            topic="/hybrid_automaton/mode",
            msg_type=String,
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            topic="/hybrid_automaton/mode",
            msg_type=String,
            callback=lambda msg: self.__setattr__('mode', msg),
            qos_profile=QOS_PROFILE
        )

        self.create_subscription(
            topic="/hybrid_automaton/mode",
            msg_type=String,
            callback=lambda msg: self.__setattr__('mode', msg),
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            topic='/hybrid_automaton/transition_pending',
            msg_type=TransitionPending,
            callback=lambda msg: self.__setattr__('transition_pending', msg),
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            topic='/hybrid_automaton/transition_timer',
            msg_type=TransitionTimer,
            callback=lambda msg: self.__setattr__('transition_time', msg), # need to implement this
            qos_profile=QOS_PROFILE
        )   
        self.create_subscription(
            topic='/hybrid_automaton/dynamics',
            msg_type=Dynamics,
            callback=lambda msg: self.__setattr__('dynamics', msg),
            qos_profile=QOS_PROFILE
        )

        self.mission_start_time = None
        self.automaton_uuid = None
        self.status = None
        self.dynamics = None
        self.time_since_last_transition = None
        self.waypoints = None
        self.transition_pending = None
        


        self._hybrid_automaton_action_server = ActionServer(
            node=self,
            action_type=HybridAutomaton,
            action_name='hybrid_automaton_action_server',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self._cancel_callback
        )

    def goal_callback(self, mission_request: HybridAutomaton.Goal, mission_request_tolerance: Duration = Duration(sec=1)):
        # validate the waypoint and such
        try: 
            validate_timestamps_within_tolerance(mission_request.stamp, get_current_ros_time(), Duration(sec=10))
            # if mission_request.goal_waypoint is None: 
            #     raise ValueError('no goal waypoint')
            # if mission_request.mission_uuid is None: 
            #     raise ValueError('no mission_uuid received')
            # if mission_request.agent_uuid is None:
            #     raise ValueError('no agent_uuid received')
        except Exception as e: 
            self.get_logger().error(f"Mission Request: \n\n'{mission_request}' \n\Rejected due to Exception: {str(e)}")
            return GoalResponse.REJECT
        self.mission_start_time = mission_request.stamp
        self.automaton_uuid = uuid.uuid4()
        self.ros_automaton_uuid = UUID(uuid=list(self.automaton_uuid.bytes))
        self.mission_active = True
        self.get_logger().info(f"Mission Request: \n\n'{mission_request}' \n\nAccepted, Starting Hybrid Automaton...")
        return GoalResponse.ACCEPT
    
    def execute_callback(self, goal_handle):
        """Execute callback that starts the hybrid automaton and feedback loop."""
        self._current_goal_handle = goal_handle
        
        # publish the initial control mode via control mode publisher for service use
        self.mode_publisher.publish(String(data=self.initial_mode))
        # start up the different components via services
        dynamics_cli = self.create_client(srv_type=Trigger, srv_name="/hybrid_automaton/start_dynamics_eval")
        if not dynamics_cli.wait_for_service(timeout_sec=2.0):
            raise TimeoutError("Timeout occurred waiting for '/hybrid_automaton/start_dynamics_eval' service")
        # transition_engine_cli = self.create_client(srv_type=Trigger, srv_name=)
        transition_evaluator_cli = self.create_client(srv_type=Trigger, srv_name="/hybrid_automaton/start_transition_eval")
        while not transition_evaluator_cli.wait_for_service(timeout_sec=2.0):
            raise TimeoutError("timeout occured waiting for '/hybrid_automaton/start_transition_eval'")
        transition_engine_cli = self.create_client(srv_type=Trigger, srv_name='/hybrid_automaton/start_transition_engine')
        while not transition_engine_cli.wait_for_service(timeout_sec=2.0):
            raise TimeoutError("timeout occured waiting for '/hybrid_automaton/start_transition_engine'")

        # wait for future
        future = dynamics_cli.call_async(Trigger.Request())
        try:
            rclpy.spin_until_future_complete(self, future=future, timeout_sec=2.0)
        except Exception as e:
            raise e # should display logs here
        
        if not future.done() or future.result().success is False:
            raise RuntimeError('Exception occured dynamics start future request for dynamics evaluator')

        # wait for future
        future = None # TODO: Transition evalutor crashed need to look into this......!
        future = transition_evaluator_cli.call_async(Trigger.Request())
        try: 
            rclpy.spin_until_future_complete(self, future=future, timeout_sec=2.0)
        except Exception as e: 
            raise e
        
        if not future.done() or future.result().success is False:
            raise Exception(f"Exception occured while waiting for transition_evaluator")
        
        future = None
        future = transition_engine_cli.call_async(Trigger.Request())
        try: 
            rclpy.spin_until_future_complete(self, future=future, timeout_sec=2.0)
        except Exception as e: 
            raise e
        
        if not future.done() or future.result().success is False:
            raise Exception(f"Exception occured while wainting for transition_engine")

        # when the hybrid automaton components have been started. start the feedback callback.
        # wait until mission is completed.
        self._feedback_timer = self.create_timer((1/self.get_parameter('transition_evaluation_hz').value), self._feedback_timer_callback)
        while self.mission_active:
            rclpy.spin_once(self)

        # Once mission is done, cancel the feedback timer and reset the goal handle.
        self._feedback_timer.cancel()
        self._current_goal_handle = None
        goal_handle.succeed()  

        result = HybridAutomaton.Result(success = True, message='Mission Completed!')
        return result

    def _feedback_timer_callback(self):
        """
            provides automaton output to the action server cli.
        """
        try:
            if isinstance(self.mode, String):
                if self.mode.data.lower() in self.final_modes:
                    # Should use invariants here to check if we are in final mode and should finish the hybrid automaton.
                    self.get_logger().info(f"In final mode: {self.mode.data}")
            feedback = HybridAutomaton.Feedback()
            feedback.feedback.automaton_uuid = self.ros_automaton_uuid
            feedback.feedback.mode = self.mode.data if self.mode is not None else ''
            feedback.feedback.status = self.status if self.status is not None else ''
            feedback.feedback.dynamics = self.dynamics.dynamic_parameters if self.dynamics is not None else DynamicParameter()
            feedback.feedback.time_since_last_transition = self.time_since_last_transition if self.time_since_last_transition is not None else Duration()
            feedback.feedback.transition_pending = self.transition_pending if self.transition_pending is not None else TransitionPending()
            stamp = get_current_ros_time()
            feedback.feedback.stamp = stamp
            feedback.feedback.elapsed_time = subtract_time(stamp, self.mission_start_time)
            feedback.feedback.waypoints = self.waypoints if self.waypoints is not None else Waypoints()

            feedback.feedback.error = False
            feedback.feedback.message = ''
            self._current_goal_handle.publish_feedback(feedback)
        except Exception as e:
            raise e
        
    def _cancel_callback(self, goal_handle):
        """Action server cancel callback function."""
        self.get_logger().info('Received request to cancel goal')
        if self._is_thread:  
            self._thread_events['stop_event'].set()
        return CancelResponse.ACCEPT  


def main(args=None):
    rclpy.init()
    node = LifeCycleManager()
    rclpy.spin(node=node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

