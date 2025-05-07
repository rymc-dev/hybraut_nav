

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

# Add two directories back to sys.path: necessary for local debugging when the package isn't built with colcon,
# allowing imports to work correctly without relying on the build process.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        Evaluates transitions between different modes based on guard conditions.
        """
        # Prepare request for evaluating transitions
        if not isinstance(self.transition_pending, TransitionPending):
            return
        
        if self.transition_pending.transition_pending: # transition is pending
            mode = self.mode.lower()
            transition_eval:Transition = self.transition_eval
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

            
            transition = "cruise_to_t2los_2"
            _, _, transition_to_raw = transition.partition("to_")

            # Split at the last underscore
            base, _, maybe_num = transition_to_raw.rpartition('_')

            if maybe_num.isdigit() and base in list(self.config['modes'].keys()):
                transition_to = base
            else:
                transition_to = transition_to_raw
            # check if reset if reset then make request to reset service to update internal states
            self.mode_publisher.publish(String(data=transition_to))

        
        

        # self._ha_pubs['mode'].publish(
        #     String(data=str(self._CURRENT_MODE).upper()))
        # self._ha_pubs['waypoints'].publish(
        #     Waypoints(waypoints=self._STATES['waypoints']))

        # try:
        #     if self._guards_status is not None:
        #         guards_to_check = self._guards_status.guard_names
        #         guard_results = {}
        #         for guard_name in guards_to_check:
        #             if hasattr(self._guards_status, guard_name):
        #                 value = getattr(self._guards_status, guard_name)
        #                 guard_results[guard_name] = value
        #             else:
        #                 self.get_logger().warn(
        #                     f'Guard name: "{guard_name}" not found in guard_status fields ')
        #         active_guard = None
        #         priority = -1
        #         for guard, status in guard_results.items():
        #             if self._TRANSITIONS[self._CURRENT_MODE][guard] < priority or priority == -1:
        #                 if status:  # Means that the guard is active
        #                     priority = self._TRANSITIONS[self._CURRENT_MODE][guard]
        #                     active_guard = guard

        #         # make transition based on active guard
        #         if active_guard is not None:
        #             # TODO: first check if there is a reset for this guar
        #             # Get transition to item from guard name
        #             new_control_mode = active_guard.split('_')[2]
        #             self._CURRENT_MODE = new_control_mode
        #             # If no reset condition for this guard then change control
        #             # mode based on the transition
        #         from std_msgs.msg import Header
        #         from colav_interfaces.msg import CmdVelYaw, ControlMode, ControlStatus
        #         # need to now publish the latest dynamic updates!!!!!!
        #         controller_feedback = ControllerFeedback(
        #             header=Header(stamp=get_current_ros_time()),
        #             mission_tag="mission",  # TODO: Need to retrieve this from colav_params
        #             agent_tag='agent',  # TODO: Need to retrive this from colav_params
        #             cmd=CmdVelYaw(
        #                 velocity=self._current_dynamics.dynamics.velocity,
        #                 yaw_rate=self._current_dynamics.dynamics.yaw_rate),
        #             mode=ControlMode(
        #                 type=next(
        #                     (k for k, v in self._MODES.items() if v == self._CURRENT_MODE), None)),
        #             status=ControlStatus(type=1)
        #         )
        #         self._ha_pubs['controller_feedback'].publish(
        #             controller_feedback)

        # except Exception as e:
        #     self.get_logger().error(f'Error occured: {str(e)}')

        # request = EvaluateTransitions.Request()
        # request.transition_names = [transition[0] for transition in self._TRANSITIONS[self._CURRENT_MODE]]
        # cli = self._NODE_CLIS['evaluate_transitions']
        # future = cli.call_async(request)
        # future.add_done_callback(self._transition_evaluation_callback)

    # def _transition_evaluation_callback(self, future):
    #     """
    #     Callback function for evaluating mode transitions based on guard conditions.

    #     This function is triggered when the asynchronous transition evaluation completes.
    #     It processes the `future` response containing the result of guard evaluations for
    #     possible transitions from the current control mode.

    #     If the evaluation is successful:
    #     - It filters out the transitions with successful guard conditions.
    #     - Among the valid transitions, it selects the one with the highest priority (lowest numeric value).
    #     - Logs the name of the active transition.
    #     - (TODO) Executes any necessary reset or update actions and updates the `_CURRENT_MODE`.

    #     If the evaluation fails (`overall_success` is False), it raises a `RuntimeError`.

    #     Args:
    #         future (concurrent.futures.Future): A future object containing the result of the transition evaluation,
    #                                             which is expected to have an `overall_success` flag,
    #                                             a `results` list of evaluated transitions,
    #                                             and a `message` describing any failure.

    #     Raises:
    #         RuntimeError: If the evaluation response indicates failure.
    #         Exception: For any unexpected error encountered during processing.
    #     """

    #     try:
    #         response = future.result()
    #         if response.overall_success:
    #             # Filter active transitions (those with a successful guard
    #             # evaluation)
    #             active_transitions = [t for t in response.results if t.success]
    #             if active_transitions:
    #                 # Determine the transition with the highest priority
    #                 # (lowest numerical value)
    #                 def get_priority(transition_name):
    #                     for trans, priority in self._TRANSITIONS[self._CURRENT_MODE]:
    #                         if trans == transition_name:
    #                             return priority
    #                     return float('inf')

    #                 active_transition = min(
    #                     active_transitions,
    #                     key=lambda t: get_priority(
    #                         t.transition_name))
    #                 self.get_logger().info(
    #                     f"Active transition: {active_transition.transition_name}")

    #                 # TODO: Execute any reset/update actions,
    #                 # and update the _CURRENT_MODE based on the chosen
    #                 # transition.
    #                 pass
    #             else:
    #                 # No transition was activated: execute dynamics for the
    #                 # current mode.
    #                 pass
    #         else:
    #             raise RuntimeError(
    #                 f"Transition evaluation failed: {response.message}")
    #     except Exception as e:
    #         self.get_logger().error(str(e))
    #         raise e

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


from rclpy.executors import SingleThreadedExecutor

def main(args=None):
    rclpy.init(args=args)
    node = TransitionEngineNode()

    try:
        rclpy.spin(node)
        # executor = SingleThreadedExecutor()
        # executor.add_node(node)
        # executor.spin()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
