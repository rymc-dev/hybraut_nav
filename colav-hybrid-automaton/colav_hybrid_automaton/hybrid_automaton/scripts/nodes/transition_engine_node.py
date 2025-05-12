

"""
ROS2 Hybrid Automaton node. performs lifecycle managements of the hybrid automaton 
starting and stopping the mode based on requests while managing control mode of the hybrid automaton
as defined within the hybrid_automaton_config.yml
"""

import os
import sys

# TODO: Let's change the StartHybridAutomaton to a action server 
#       instead of a service I think this would be better as feedback
#       can be the output message. means less to think about.

from std_msgs.msg import String
from hybrid_automaton_interfaces.msg import (
    Mode,
    Transition,
    TransitionPending,
    TransitionTimer,
    Waypoint,
    Waypoints,
    # output
)
from unique_identifier_msgs.msg import UUID
from colav_interfaces.msg import GuardsStatus, Waypoints, ControllerFeedback
# from hybrid_automaton.utils import get_current_ros_time  
# from colav_hybrid_automaton.hybrid_automaton.utils.hybrid_automaton.node_utils import create_cli
from hybrid_automaton.config import QOS_PROFILE
from std_srvs.srv import Trigger
from colav_interfaces.srv import StartHybridAutomaton
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, DynamicsUpdate
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor
from hybrid_automaton.utils import load_yml, process_automaton_config
from hybrid_automaton_interfaces.msg import Transition, TransitionPending, TransitionTimer
from ament_index_python.packages import get_package_share_directory
from hybrid_automaton_interfaces.srv import Reset
# Add two directories back to sys.path: necessary for local debugging when the package isn't built with colcon,
# allowing imports to work correctly without relying on the build process.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from builtin_interfaces.msg import Duration
from rclpy.time import Time

default_hybrid_automaton_config = os.path.join(get_package_share_directory('colav_hybrid_automaton'), 'config', 'colav_hybrid_automaton_config.yml')

class TransitionEngineNode(Node):
    """
    transition engine manages the current mode, evaluating transitions in
    real time and performing transitions and resets on states based on 
    real world evaluations.
    """

    def __init__(
        self,
        namespace: str = "hybrid_automaton",
        name: str = "transition_engine"
    ):
        """
        Initialize the COLAV Hybrid Automaton Chart node.
        """
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

        # declare parameter for transition evaluation hz
        self.declare_parameter(
            'transition_evaluation_hz',
            value=self.config['params']['transition_evaluation_hz'],
            descriptor=ParameterDescriptor(description='transition evaluation hz for guard evaluations')
        )

        self.mode_publisher = self.create_publisher(
            String,
            '/hybrid_automaton/mode',
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            topic="/hybrid_automaton/mode",
            msg_type=String,
            callback=lambda msg: self.__setattr__('mode', msg.data),
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            topic="/hybrid_automaton/transitions",
            msg_type=Transition,
            callback=lambda msg: self.__setattr__('transition_eval', msg),
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            topic="/hybrid_automaton/transition_pending",
            msg_type=TransitionPending,
            callback=lambda msg: self.__setattr__('transition_pending', msg),
            qos_profile=QOS_PROFILE
        )

        self.mode = None
        self.transition_pending = None
        self.transition_eval = None
        self._waiting_after_reset = False
        self._reset_complete_time = None

        self.reset_srv_cli = self.create_client(
            srv_type=Reset,
            srv_name='/hybrid_automaton/reset_states'
        )

        self.create_service(
            Trigger,
            '/hybrid_automaton/start_transition_engine',
            self._start_transition_engine
        )
        self.create_service(
            Trigger,
            '/hybrid_automaton/stop_transition_engine',
            self._stop_hybrid_automaton_callback
        )

    def _start_transition_engine(
            self,
            request: Trigger.Request,
            response: Trigger.Response) -> Trigger.Response:
        """
        Callback to start the hybrid automaton.
        """
        try:
            # Start a timer to evaluate transitions periodically
            self._transition_eval_timer = self.create_timer(
                1/self.get_parameter('transition_evaluation_hz').value,  # This timer period might later be parameterized.
                self.transition_check_callback
            )
            response.success = True
            response.message = "Transition engnie successfully started"
        except Exception as e:
            self.get_logger().warning(
                f"Error in starting hybrid automaton: {str(e)}")
            response.success = False
            response.message = str(e)
        return response


    def make_zero_uuid(self) -> UUID:
        u = UUID()
        u.uuid = [0]*16
        return u

    def transition_check_callback(self):
        """
        Evaluates transitions between different modes based on guard conditions.
        """
        # Prepare request for evaluating transitions
        if self._waiting_after_reset:
            now = self.get_clock().now()
        if now - self._reset_complete_time < Duration(seconds=1.0):
            return  # Still waiting
        else:
            self._waiting_after_reset = False  # Done waiting


        if not isinstance(self.transition_pending, TransitionPending):
            return
        
        try:
            mode = self.mode.lower()
        except Exception as e: 
            self.get_logger().error('self.mode has not been received by this node')
            return
        
        if self.transition_pending.transition_pending: # transition is pending

            transition_eval:Transition = self.transition_eval
            # Need to first check if transition eval is instece 
            if not isinstance(transition_eval, Transition):
                self.get_logger().error('transition evaluation not received')
                return
            if transition_eval.success == False: 
                self.get_logger().error(f"Something went wrong with transition evaluation: {transition_eval.error_message}")
                return
            pending_transitions = [
                transition_name
                for idx, transition_name in enumerate(transition_eval.transition_names)
                if transition_eval.transition_values[idx] is True
            ]
            transition = None
            if len(pending_transitions) == 0:
                # would need to set transition pending to False in this case via publisher
                return
            elif len(pending_transitions) == 1: # returns the first transition in the list as the only transition
                transition = pending_transitions[0]
            elif len(pending_transitions) > 1: # finds highest priority transition in case multiple evalute as true
                highest_priority = -1
                for transition_name in pending_transitions:
                    curr_priority = self.config['modes'][mode]['transitions'][transition_name]['priority']
                    if highest_priority == -1 or curr_priority < highest_priority:
                        transition = transition_name
                        highest_priority = curr_priority

            
            if transition is not None:
                if self.config['transitions'][transition]['reset'] is not None: 
                    if self.config['transitions'][transition]['reset'] in list(self.config['resets'].keys()):
                        reset_name = self.config['transitions'][transition]['reset']
                        client = self.create_client(Reset, '/hybrid_automaton/reset_states')

                        if not client.wait_for_service(timeout_sec=5.0):
                            self.get_logger().error('Service /hybrid_automaton/reset_states not available')
                            return

                        req = Reset.Request()
                        req.transition_uuid = self.make_zero_uuid()
                        req.reset_name = reset_name
                        future = client.call_async(req)
                        future.add_done_callback(self._handle_reset_response)
     
            _, _, transition_to_raw = transition.partition("to_")

            # Split at the last underscore
            base, _, maybe_num = transition_to_raw.rpartition('_')

            if maybe_num.isdigit() and base in list(self.config['modes'].keys()):
                transition_to = base
            else:
                transition_to = transition_to_raw

            self.mode_publisher.publish(String(data=transition_to))
            self.mode = transition_to
        else: 
            self.mode_publisher.publish(String(data=mode))
            self.mode = mode

    def _stop_hybrid_automaton_callback(
            self,
            request: Trigger.Request,
            response: Trigger.Response) -> Trigger.Response:
        """
        Placeholder for stopping the hybrid automaton.
        """
        # TODO: Add logic to gracefully stop the automaton.
        response.success = True
        response.message = "Stop function not implemented yet"
        return response


    def _handle_reset_response(self, future):
        try:
            resp = future.result()
            if resp.success:
                self._waiting_after_reset = True
                self._reset_complete_time = self.get_clock().now()
            self.get_logger().info(f"Reset service response: success={resp.success}, message=\"{resp.message}\"")
        except Exception as e:
            self.get_logger().error(f"Reset service call failed: {str(e)}")

from rclpy.executors import MultiThreadedExecutor

def main(args=None):
    rclpy.init(args=args)
    node = TransitionEngineNode()
    executor = MultiThreadedExecutor()

    # Add your node to the multithreaded executor
    executor.add_node(node)

    try:
        # This will spin callbacks in parallel threads
        executor.spin()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        node.get_logger().error(f"Exception in executor: {e}")
    finally:
        # Cleanly shut down
        executor.shutdown()       # stop the executor
        node.destroy_node()       # tear down the node
        rclpy.shutdown()

if __name__ == '__main__':
    main()