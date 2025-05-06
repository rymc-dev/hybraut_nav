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

class LifeCycleManager(Node):
    def __init__(self, name: str = 'lifecycle_manager', namespace: str = 'hybrid_automaton'):
        super().__init__(name, namespace=namespace)
        self.mission_active = False 
        self.mode = None
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
            validate_timestamps_within_tolerance(mission_request.stamp, get_current_ros_time(), Duration(sec=1))
            if mission_request.goal_waypoint is None: 
                raise ValueError('no goal waypoint')
            if mission_request.mission_uuid is None: 
                raise ValueError('no mission_uuid received')
            if mission_request.agent_uuid is None:
                raise ValueError('no agent_uuid received')
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
        self._feedback_timer = self.create_timer(1.0, self._feedback_timer_callback)
        while self.mission_active:
            rclpy.spin_once(self, timeout_sec=0.1)

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
            feedback = HybridAutomaton.Feedback()
            self.get_logger().info('feedback....')
            feedback.feedback.automaton_uuid = self.ros_automaton_uuid
            feedback.feedback.mode = self.mode if self.mode is not None else ''
            feedback.feedback.status = self.status if self.status is not None else ''
            feedback.feedback.dynamics = self.dynamics if self.dynamics is not None else DynamicParameter()
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

