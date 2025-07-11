from rclpy.node import Node
from std_msgs.msg import String
from colav_hybrid_automaton.automaton._internal.constants import HybridAutomatonStatusEnum
from colav_hybrid_automaton.automaton._internal.utils import validate_mode, parse_transition
from threading import Lock
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher
from typing import List, Dict, Any, Optional, Tuple
from rclpy.guard_condition import GuardCondition
from rclpy.node import Node
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus, HybridAutomatonMode
from std_msgs.msg import String
from colav_hybrid_automaton.automaton._internal.factory.famd_factory import HybridAutomatonFactory
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton
from colav_interfaces.msg import Waypoint

from hybrid_automaton_interfaces.msg import (
    HybridAutomatonReset, 
    HybridAutomatonTransitionAndGuardEvaluation, 
    HybridAutomatonTransitionEvaluations
)


class TransitionEvaluationResult:
    """Container for transition evaluation results"""
    def __init__(self):
        self.has_transition = False
        self.selected_transition_name = ''
        self.selected_transition_priority = -1
        self.transitions_and_guard_evaluations = []
        self.guard_errors = []


def _validate_current_mode(automaton_model: HybridAutomaton) -> None:
    """Validate that the current mode exists in the automaton"""
    current_mode = automaton_model.current_mode
    if current_mode not in automaton_model.modes:
        raise ValueError(f"Invalid mode type: {current_mode}")


def _should_skip_evaluation(automaton_model: HybridAutomaton) -> bool:
    """Check if transition evaluation should be skipped"""
    return automaton_model.current_state == HybridAutomatonStatus.STATUS_TRANSITIONING


def _evaluate_guard(transition, automaton_model: HybridAutomaton) -> Tuple[bool, str]:
    """
    Evaluate a single guard condition
    
    Returns:
        Tuple of (guard_evaluation_result, guard_name)
    """
    guard_name = transition.guard.get_guard_info()['class_name']
    state_input_keys = transition.guard.state_input_spec_names()
    state_kwargs = {
        state_key: automaton_model.states[state_key].current_state
        for state_key in state_input_keys
    }
    guard_evaluation = transition.guard.__call__(**state_kwargs)
    return guard_evaluation, guard_name


def _select_highest_priority_transition(result: TransitionEvaluationResult, transition_name: str, transition_priority: int) -> None:
    """Update the selected transition if this one has higher priority"""
    if not result.has_transition:
        result.has_transition = True
        result.selected_transition_name = transition_name
        result.selected_transition_priority = transition_priority
    elif transition_priority < result.selected_transition_priority:
        result.selected_transition_name = transition_name
        result.selected_transition_priority = transition_priority


def _evaluate_all_transitions(automaton_model: HybridAutomaton, stamp: Time) -> TransitionEvaluationResult:
    """Evaluate all transitions for the current mode"""
    result = TransitionEvaluationResult()
    current_mode = automaton_model.current_mode
    current_mode_transitions = automaton_model.modes[current_mode].transitions

    for transition in current_mode_transitions:
        try:
            transition_name = transition.name
            transition_priority = transition.priority
            
            guard_evaluation, guard_name = _evaluate_guard(transition, automaton_model)
            
            if guard_evaluation:
                _select_highest_priority_transition(result, transition_name, transition_priority)

            result.transitions_and_guard_evaluations.append(
                HybridAutomatonTransitionAndGuardEvaluation(
                    transition_name=transition_name,
                    transition_mode_target=HybridAutomatonMode(type=transition.target_mode, stamp=stamp),
                    transition_priority=transition_priority,
                    guard_name=guard_name,
                    guard_description=transition.guard.get_guard_info()['description'],
                    guard_evaluation=guard_evaluation
                )
            )
        except Exception as e:
            error_msg = f"Exception occurred during transition '{transition_name}', evaluating guard '{guard_name}': {str(e)}"
            result.guard_errors.append(error_msg)
            continue

    return result


def _execute_reset(transition, automaton_model: HybridAutomaton) -> List[HybridAutomatonReset]:
    """Execute reset operations for a transition"""
    resets = []
    
    if transition.reset is not None:
        reset_name = transition.reset.get_reset_info()['class_name']
        reset_description = transition.reset.get_reset_info()['description']
        reset_state_target_keys = transition.reset.reset_target_spec_names()
        state_input_keys = transition.reset.state_input_spec_names()
        
        state_kwargs = {
            state_key: automaton_model.states[state_key].current_state
            for state_key in state_input_keys
        }
        
        # TODO: Replace with actual reset call when ready
        # reset_outputs = transition.reset.__call__(**state_kwargs)
        reset_outputs = [Waypoint()]  # Temporary placeholder
        
        reset_target_outputs = {
            target: output for target, output in zip(reset_state_target_keys, reset_outputs)
        }
        
        # Publish reset outputs to state topics
        for key, val in reset_target_outputs.items():
            automaton_model.states[key].publisher.publish(val)

        resets.append(HybridAutomatonReset(
            name=reset_name,
            description=reset_description,
            state_targets=list(reset_target_outputs.keys())
        ))
    
    return resets


def _find_transition_by_name(transitions, transition_name: str):
    """Find a transition by name"""
    for transition in transitions:
        if transition.name == transition_name:
            return transition
    return None


def _execute_transition(
    automaton_model: HybridAutomaton, 
    selected_transition_name: str, 
    stamp: Time,
    mode_publisher: Publisher,
    status_publisher: Publisher
) -> Tuple[List[HybridAutomatonReset], str]:
    """
    Execute the selected transition
    
    Returns:
        Tuple of (resets_performed, target_mode)
    """
    current_mode = automaton_model.current_mode
    current_mode_transitions = automaton_model.modes[current_mode].transitions
    
    # Publish transitioning status
    status_publisher.publish(HybridAutomatonStatus(
        type=HybridAutomatonStatus.STATUS_TRANSITIONING,
        message=f"Performing {selected_transition_name} transition",
        stamp=stamp
    ))
    
    # Find and execute the selected transition
    selected_transition = _find_transition_by_name(current_mode_transitions, selected_transition_name)
    if not selected_transition:
        raise ValueError(f"Selected transition '{selected_transition_name}' not found")
    
    # Execute reset operations
    resets_performed = _execute_reset(selected_transition, automaton_model)
    
    # Get target mode
    target_mode = selected_transition.target_mode
    
    # Publish mode change
    mode_publisher.publish(HybridAutomatonMode(type=target_mode, stamp=stamp))
    
    # Publish success status
    previous_mode_name = automaton_model.modes[current_mode].name
    target_mode_name = automaton_model.modes[target_mode].name
    
    status_publisher.publish(HybridAutomatonStatus(
        type=HybridAutomatonStatus.STATUS_ACTIVE_MODE,
        message=f"Transitioned from {current_mode}.{previous_mode_name} -> {target_mode}.{target_mode_name}. Automaton executing.",
        stamp=stamp
    ))
    
    return resets_performed, target_mode


def transition_evaluation_callback(
    lock: Lock,
    automaton_model: HybridAutomaton,
    stamp: Time,
    mode_publisher: Publisher,
    transition_evaluation_publisher: Publisher,
    status_publisher: Publisher,
):
    """
    Callback for evaluating transitions in the hybrid automaton on a timer.

    At regular time intervals, this function evaluates the transitions associated with the 
    current mode of the hybrid automaton. If any guard conditions are triggered, it selects 
    the highest priority guard and attempts a mode transition.

    If a transition requires a reset, the reset is executed and the updated state is 
    published to the relevant ROS2 topic. Upon a successful reset, the target mode is 
    published to the `/hybrid_automaton/mode` topic. This mode update is then processed 
    by the mode callback, which validates the new mode and updates the automaton's status 
    to 'active' again, allowing other asynchronous callback groups to proceed.

    If the automaton's current status indicates that a transition is already in progress, 
    the evaluation is skipped.

    If a guard is activated but the reset fails, a fatal status message is published, 
    signaling that the automaton may be in an unsafe state and should be shut down.

    If guard evaluations fail entirely, an error status is published with details about 
    which guards failed and why. In this case, the automaton continues running, but the 
    client system is notified of the issue, this will allow the end user to determine if 
    they want to cancel the mission for the current automaton.
    """
    try:
        with lock:
            # Skip evaluation if already transitioning
            if _should_skip_evaluation(automaton_model):
                return

            # Validate current mode
            _validate_current_mode(automaton_model)
            
            # Evaluate all transitions
            evaluation_result = _evaluate_all_transitions(automaton_model, stamp)
            
            # Create transition evaluation message
            transition_evaluation_msg = HybridAutomatonTransitionEvaluations(
                current_mode=HybridAutomatonMode(type=automaton_model.current_mode, stamp=stamp),
                stamp=stamp,
                transitions_and_guards_evaluations=evaluation_result.transitions_and_guard_evaluations,
                selected_transition_name=evaluation_result.selected_transition_name
            )
            
            # Execute transition if one was selected
            if evaluation_result.selected_transition_name:
                resets_performed, target_mode = _execute_transition(
                    automaton_model,
                    evaluation_result.selected_transition_name,
                    stamp,
                    mode_publisher,
                    status_publisher
                )
                transition_evaluation_msg.selected_transition_resets.extend(resets_performed)
            
            # Handle guard errors if any occurred
            if evaluation_result.guard_errors:
                error_message = "; ".join(evaluation_result.guard_errors)
                status_publisher.publish(HybridAutomatonStatus(
                    type=HybridAutomatonStatus.STATUS_ERROR,
                    message=f"Guard evaluation errors: {error_message}",
                    stamp=stamp
                ))
            
            # Publish evaluation results
            transition_evaluation_publisher.publish(transition_evaluation_msg)
            
    except Exception as e:
        # Log the exception and publish error status
        error_message = f"Critical error in transition evaluation: {str(e)}"
        status_publisher.publish(HybridAutomatonStatus(
            type=HybridAutomatonStatus.STATUS_FATAL,
            message=error_message,
            stamp=stamp
        ))
        # Consider logging the full traceback for debugging
        import traceback
        print(f"Transition evaluation error: {traceback.format_exc()}")



import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading

if __name__ == '__main__':
    rclpy.init()
    
    mock_automaton_node = Node('mock_automaton_node')

    automaton_model = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path='/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
        generate_mmd_diagrams=False
    )
    mock_automaton_node.__setattr__('automaton_model', automaton_model)
    
    mode_publisher = mock_automaton_node.create_publisher(
        topic='hybrid_automaton/mode',
        msg_type=HybridAutomatonMode,
        qos_profile=10
    )
    transition_evaluation_publisher = mock_automaton_node.create_publisher(
        topic='hybrid_automaton/transition_evalaution',
        msg_type=String, # TODO: Add new ros2 interface for TransitionEvaluation information
        qos_profile=10
    )
    status_publisher = mock_automaton_node.create_publisher(
        topic='hybrid_automaton/status',
        msg_type=HybridAutomatonStatus,
        qos_profile=10
    )
    
    status_list = []

    # FIX 1: Convert message to string for logging
    def status_callback(msg):
        mock_automaton_node.get_logger().info(f"Status received - Type: {msg.type}, Message: {msg.message}")
        status_list.append(msg)  # Also append to list for testing

    mock_automaton_node.create_subscription(
        topic='hybrid_automaton/status',
        msg_type=HybridAutomatonStatus,
        callback=status_callback,
        qos_profile=10
    )

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(mock_automaton_node)

    executor_thread = threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    transition_evaluation_callback(
        lock=Lock(),
        automaton_model=mock_automaton_node.__getattribute__('automaton_model'),
        stamp=mock_automaton_node.get_clock().now().to_msg(),
        mode_publisher=mode_publisher,
        transition_evaluation_publisher=transition_evaluation_publisher,
        status_publisher=status_callback
    )

    executor.shutdown()
    mock_automaton_node.destroy_node()
    rclpy.shutdown()
            
    #         # Initialize guard evaluation message
    #         eval_msg: GuardsEvaluation = GuardsEvaluation(stamp=stamp)
    #         # eval_msg.mode = validate_mode(available_modes, current_mode)
    #         eval_msg.success = True
    #         # eval_msg.transition_names = []
    #         # eval_msg.guard_evaluations = []
    #         # eval_msg.guard_priority = []
            
    #         # Evaluate all guards for current mode
    #         pending_transitions = []
    #         error_messages = []

    #         current_mode_configuration = automaton.modes[automaton.current_mode]
    #         current_mode_transitions = current_mode_configuration.transitions

    #         for transition in current_mode_transitions:
    #             print ('hello world')
    #             transition_name = transition.name
                
    #             # try:
    #             #     # Get state inputs for guard evaluation
    #             #     guard_config = transition_config['guard']
    #             #     state_inputs = [automaton_states[s] for s in guard_config['state_inputs']]
                    
    #             #     # Evaluate the guard
    #             #     guard_result = bool(guard_config['function'](*state_inputs))
                    
    #             #     # Store evaluation results
    #             #     eval_msg.transition_names.append(transition_key)
    #             #     eval_msg.guard_evaluations.append(guard_result)
    #             #     eval_msg.guard_priority.append(transition_config['priority'])
                    
    #             #     # If guard is true, add to pending transitions
    #             #     if guard_result:
    #             #         pending_transitions.append(transition_key)
                        
    #             # except Exception as e:
    #             #     error_messages.append(f"{transition_key}: {str(e)}")
    #             #     eval_msg.success = False
            
    #         # Handle any evaluation errors
    #         if error_messages:
    #             eval_msg.success = False
    #             eval_msg.message = f"guard evaluation exceptions: \n- " + "\n- ".join(error_messages)
    #             guards_evaluation_publisher.publish(eval_msg)
    #             status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ERROR))
    #             return
            
    #         # Publish guard evaluation results
    #         guards_evaluation_publisher.publish(eval_msg)
            
    #         # If no transitions are pending, stay in current mode
    #         if not pending_transitions:
    #             status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ACTIVE_MODE))
    #             return
            
    #         # Select highest priority transition
    #         selected_transition_key = _select_highest_priority_transition(
    #             current_mode_transitions, 
    #             pending_transitions
    #         )
            
    #         if selected_transition_key is None:
    #             status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ACTIVE_MODE))
    #             return
            
    #         # Publish transitioning status
    #         status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.TRANSITIONING))
            
    #         # Execute the selected transition
    #         transition_config = current_mode_transitions[selected_transition_key]
            
    #         # Handle reset if configured
    #         reset_config = transition_config.get('reset')
    #         if reset_config is not None:
    #             logger.info(f"Executing reset: {reset_config['name']}")
    #             reset_func = reset_config['function']
    #             state_inputs = _get_reset_inputs(automaton_states, reset_config['state_inputs'])
    #             reset_output = reset_func(*state_inputs)
    #             waypoints_publisher.publish(reset_output[0])
            
    #         # Publish new mode
    #         new_mode = parse_transition(available_modes, selected_transition_key)
    #         mode_publisher.publish(String(data=new_mode))
            
    #         logger.info(f"Transition executed: {current_mode} -> {new_mode} (via {selected_transition_key})")
            
    #         # Publish back to active status after transition
    #         status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ACTIVE_MODE))
            
    # except Exception as e:
    #     logger.error(f"Unexpected exception in combined_transition_evaluation_callback: {str(e)}")
    #     status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ERROR))


# def _select_highest_priority_transition(transition_config: dict, pending: List[str]) -> str:
#     """
#     Helper function to select the highest-priority transition from a list of pending transitions.
#     Lower priority values have higher priority.
#     """
#     if len(pending) == 1:
#         return pending[0]
    
#     highest_priority = float('inf')
#     selected_transition = None
    
#     for transition_name in pending:
#         priority = transition_config[transition_name]['priority']
#         if priority < highest_priority:
#             highest_priority = priority
#             selected_transition = transition_name
    
#     return selected_transition


# def _get_reset_inputs(states: dict, state_input_keys: list) -> List[Any]:
#     """Retrieves the state values for the given reset's state inputs."""
#     return [states[key] for key in state_input_keys]


# import threading
# import rclpy
# from rclpy.node import Node
# from rclpy.executors import MultiThreadedExecutor
# from hybrid_automaton_interfaces.msg import (
#     HybridAutomatonGuardEvaluations,
#     HybridAutomatonMode,
#     HybridAutomatonStatus
# )
# from colav_interfaces.msg import WaypointsState

# if __name__ == '__main__':
#     path = '/home/ryan/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml'
#     automaton = HybridAutomatonFactory.hybrid_automaton_registry(automaton_famd_path=path, generate_mmd_diagrams=False)

#     print (automaton)


#     rclpy.init()
#     node = Node('test_node')
#     mode_publisher = node.create_publisher(
#         topic='mode',
#         msg_type=HybridAutomatonMode,
#         qos_profile=10
#     )
#     status_publisher = node.create_publisher(
#         topic='status',
#         msg_type=HybridAutomatonStatus,
#         qos_profile=10
#     )
#     waypoints_publisher = node.create_publisher(
#         topic='waypoints_state',
#         msg_type=WaypointsState,
#         qos_profile=10
#     )
#     guard_evaluation_publisher = node.create_publisher(
#         topic='guards',
#         msg_type=HybridAutomatonGuardEvaluations,
#         qos_profile=10
#     )

#     executor = MultiThreadedExecutor(num_threads=2)
#     executor.add_node(node)
#     threading.Thread(target=executor.spin).start()

#     rclpy.shutdown()


#     combined_transition_evaluation_callback(
#         lock=threading.Lock(),
#         automaton=automaton,
#         stamp=node.get_clock().now().to_msg(),
#         mode_publisher=mode_publisher,
#         status_publisher=status_publisher,
#         waypoints_publisher=waypoints_publisher,
#         guards_evaluation_publisher=guard_evaluation_publisher,
#         logger=node.get_logger()
#     )