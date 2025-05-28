

"""
ROS2 Hybrid Automaton node. performs lifecycle managements of the hybrid automaton 
starting and stopping the mode based on requests while managing control mode of the hybrid automaton
as defined within the hybrid_automaton_config.yml
"""

from std_msgs.msg import String
from hybrid_automaton_interfaces.msg import (
    Transition,
    TransitionPending,
)
# from hybrid_automaton.utils import get_current_ros_time  
# from colav_hybrid_automaton.hybrid_automaton.utils.hybrid_automaton.node_utils import create_cli
from hybrid_automaton.config import QOS_PROFILE
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor
from hybrid_automaton.utils import load_yml, process_automaton_config
from hybrid_automaton_interfaces.msg import Transition, TransitionPending, TransitionTimer
from ament_index_python.packages import get_package_share_directory
from hybrid_automaton_interfaces.srv import Reset
from builtin_interfaces.msg import Duration
from rclpy.time import Time
import threading
from hybrid_automaton.utils import create_state_subscriptions
from hybrid_automaton.config import HybridAutomatonStatus

from rclpy.lifecycle import State, TransitionCallbackReturn

from hybrid_automaton.scripts.nodes.managed_node import AutomatonManagedNode

class TransitionEngineManagedNode(AutomatonManagedNode):
    """
    transition engine manages the current mode, evaluating transitions in
    real time and performing transitions and resets on states based on 
    real world evaluations.
    """

    def __init__(
        self,
        name: str = "transition_engine",
        namespace: str = "hybrid_automaton"
    ):
        """
        Initialize the COLAV Hybrid Automaton Chart node.
        """
        super().__init__(name, namespace=namespace)
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


    def on_configure(self, state):
        """"""
        super().on_configure(state)
        try:
            self.mode_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/mode',
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
            )
            self.status_publisher = self.create_publisher(
                String,
                '/hybrid_automaton/status',
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
            )
            self.transition_pending_pub = self.create_publisher(
                TransitionPending,
                '/hybrid_automaton/transition_pending',
                qos_profile=QOS_PROFILE,
                callback_group=self.topic_callback_group
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
            self._transition_eval_timer = self.create_timer(
                1/self.eval_hz, 
                self.transition_check_callback,
                callback_group=self.dynamic_feedback_callback_group
            )
        except Exception as e:
            self.get_logger().error()
            return TransitionCallbackReturn.FAILURE

        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state):
        self.mode = 'cruise'
        self.mode_publisher.publish(String(data=self.mode))
        return super().on_activate(state)

    def on_deactivate(self, state):
        return super().on_deactivate(state)

    def on_cleanup(self, state):
        return super().on_cleanup(state)

    def on_shutdown(self, state):
        return super().on_shutdown(state)    


    """callbacks"""

    def transition_check_callback(self):
        """
        Evaluates transitions between different modes based on guard conditions,
        performs resets on transitions requiring them, and waits for state updates.
        """
        if not self.activate:
            return

        # If a reset is in progress, skip all transition logic
        if self.reset_event.is_set():
            self.status_publisher.publish(String(data=HybridAutomatonStatus.TRANSITIONING.name))
            self.get_logger().info(f'Transition reset in progress for transition: {self.current_transition_uuid}')
            return

        if not isinstance(self.mode, str) or self.mode is None:
            self.status_publisher.publish(String(data=HybridAutomatonStatus.AWAITING_MODE.name))
            self.get_logger().error('self.mode has not been received by this node')
            return
        
        available_modes = list(self.config['modes'].keys())
        if self.mode not in available_modes:
            raise ValueError(
                self.mode,
                f"Published mode '{self.mode}' is not configured. Available modes: {list(available_modes)}"
            )

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
            curr_transition_eval = self.transition_eval
            if not curr_transition_eval.success:
                self.get_logger().error(f"Transition evaluation failed: {curr_transition_eval.error_message}")
                self.status_publisher.publish(String(data=HybridAutomatonStatus.FAILED.name))
                return

            self.current_transition_uuid = curr_transition_eval.transition_uuid
            pending = [
                name for idx, name in enumerate(curr_transition_eval.transition_names)
                if curr_transition_eval.transition_values[idx]
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
    node = TransitionEngineManagedNode()
    executor = MultiThreadedExecutor(num_threads=4)

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