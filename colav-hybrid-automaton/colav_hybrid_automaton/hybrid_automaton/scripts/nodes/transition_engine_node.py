

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
    # output
)
from unique_identifier_msgs.msg import UUID
from colav_interfaces.msg import GuardsStatus, Waypoints, Waypoint, ControllerFeedback
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
import threading
from hybrid_automaton.utils import create_state_subscriptions
from hybrid_automaton.config import HybridAutomatonStatus

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
        self.status_publisher = self.create_publisher(
            String,
            '/hybrid_automaton/status',
            qos_profile=QOS_PROFILE
        )
        self.transition_pending_pub = self.create_publisher(
            TransitionPending,
            '/hybrid_automaton/transition_pending',
            qos_profile=QOS_PROFILE
        )
        self.create_subscription(
            topic="/hybrid_automaton/mode",
            msg_type=String,
            callback=lambda msg: self.__setattr__('mode', msg.data.lower()),
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
        self.create_subscription(
            topic='/hybrid_automaton/status',
            msg_type=String,
            callback=lambda msg: self.__setattr__('status', msg.data),
            qos_profile=QOS_PROFILE
        )
        create_state_subscriptions(node=self)

        self.mode = None
        self.status = None
        self.transition_pending = None
        self.transition_eval = None
        self._waiting_after_reset = False
        self._reset_complete_time = None
        self.current_transition_uuid = None
        self.current_invariant_status = None
        
        self.reset_event = threading.Event()

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

    def transition_check_callback(self):
        """
        Evaluates transitions between different modes based on guard conditions,
        performs resets on transitions requiring them, and waits for state updates.
        """

        # If a reset is in progress, skip all transition logic
        if self.reset_event.is_set():
            self.status_publisher.publish(String(data=HybridAutomatonStatus.TRANSITIONING.name))
            self.get_logger().info(f'Transition reset in progress for transition: {self.current_transition_uuid}')
            return

        if self.mode is None:
            self.status_publisher.publish(String(data=HybridAutomatonStatus.AWAITING_MODE.name))
            self.get_logger().error('self.mode has not been received by this node')
            return

        # Get invariant
        invariant = self.config['modes'][self.mode].get('invariants')
        if not invariant:
            return  # No invariant found

        inv_func = self.config['invariants'][invariant]['function']
        state_inputs_raw = self.config['invariants'][invariant].get('state_inputs', [])
        state_inputs = [
            self.config['states'][state_input]['state']
            for state_input in state_inputs_raw if state_input in self.config['states']
        ]
        try:
            invariant_output = inv_func(*state_inputs)
        except Exception as e:
            self.get_logger().error(str(e))
            self.status_publisher.publish(String(data=HybridAutomatonStatus.FAILED.name))
            return

        # If no transition is pending, re-publish current mode
        if isinstance(self.transition_pending, TransitionPending) and self.transition_pending.transition_pending and isinstance(self.transition_eval, Transition):
            # Transition evaluation
            if not self.transition_eval.success:
                self.get_logger().error(f"Transition evaluation failed: {self.transition_eval.error_message}")
                self.status_publisher.publish(String(data=HybridAutomatonStatus.FAILED.name))
                return

            self.current_transition_uuid = self.transition_eval.transition_uuid
            pending = [
                name for idx, name in enumerate(self.transition_eval.transition_names)
                if self.transition_eval.transition_values[idx]
            ]
        else:
            # No transitions pending: finalize or return based on invariant output
            if invariant_output is False:
                self.status_publisher.publish(String(data=HybridAutomatonStatus.COMPLETED.name))
                return
            
            self.status_publisher.publish(String(data=HybridAutomatonStatus.ACTIVE.name))
            return

        # Select the highest-priority transition
        transition = self._select_highest_priority_transition(pending)
        # no transitions and invariants is still true therefore we still active
        if transition is None:
            self.status_publisher.publish(String(data=HybridAutomatonStatus.ACTIVE.name))
            return

        # Handle reset if required
        reset_name = self.config['transitions'][transition].get('reset')
        if reset_name and reset_name in self.config['resets']:
            self._handle_reset(transition)
        else:
            self._publish_transition(transition)

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

    def _handle_reset(self, transition):
        """
        Handles the reset logic for a transition that requires it.
        """
        self.reset_event.set()
        client = self.create_client(Reset, '/hybrid_automaton/reset_states')
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Reset service not available')
            self.reset_event.clear()
            return

        req = Reset.Request()
        req.transition_uuid = self.current_transition_uuid
        req.reset_name = self.config['transitions'][transition].get('reset')
        future = client.call_async(req)

        # Timeout watchdog
        def _on_reset_timeout():
            if not future.done():
                self.get_logger().warn("Reset service call timed out.")
                self.reset_event.clear()

        timeout_timer = threading.Timer(30.0, _on_reset_timeout)
        timeout_timer.start()

        # Reset response callback
        def _on_reset_response(fut):
            timeout_timer.cancel()
            try:
                resp = fut.result()
                if resp.success:
                    self.get_logger().info(f"Reset succeeded: {resp.message}")
                    self._publish_transition(transition)
                else:
                    self.get_logger().error(f"Reset failed: {resp.message}")
            except Exception as e:
                self.get_logger().error(f"Reset service exception: {e}")
            finally:
                self.reset_event.clear()

        future.add_done_callback(_on_reset_response)

    def _publish_transition(self, transition):
        """
        Publishes the transition when no reset is needed.
        """
        self.parse_and_publish_transition(transition)
        tp = TransitionPending(
            stamp=self.transition_eval.stamp,
            transition_uuid=self.transition_eval.transition_uuid,
            transition_pending=False
        )
        self.status_publisher.publish(String(data=HybridAutomatonStatus.TRANSITIONING.name))
        self.transition_pending_pub.publish(tp)

    def parse_and_publish_transition(self, transition):
        _, _, transition_to_raw = transition.partition("to_")

        # Split at the last underscore
        base, _, maybe_num = transition_to_raw.rpartition('_')

        if maybe_num.isdigit() and base in list(self.config['modes'].keys()):
            transition_to = base
        else:
            transition_to = transition_to_raw

        self.mode_publisher.publish(String(data=transition_to))
        self.mode = transition_to

    def publish_transition_status(self, transition_pending: bool):
        self.transition_pending_pub 

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
                self.reset_event.clear()
            else:
                self.reset_event.clear()
                raise Exception('error occured')
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