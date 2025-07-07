from rclpy.node import Node
from std_msgs.msg import String
from hybrid_automaton_interfaces.msg import HybridAutomatonGuardEvaluations as GuardsEvaluation
from colav_hybrid_automaton.automaton._internal.constants import HybridAutomatonStatusEnum
from colav_hybrid_automaton.automaton._internal.utils import validate_mode, parse_transition
from threading import Lock
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher
from typing import List, Dict, Any
from rclpy.guard_condition import GuardCondition
from rclpy.node import Node
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus
from colav_hybrid_automaton.automaton._internal.factory.famd_factory import HybridAutomatonFactory
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton

def combined_transition_evaluation_callback(
    lock: Lock,
    automaton: HybridAutomaton,
    stamp: Time,
    mode_publisher: Publisher,
    status_publisher: Publisher,
    waypoints_publisher: Publisher,
    guards_evaluation_publisher: Publisher,
    logger: RcutilsLogger
):
    """
    Combined callback that evaluates guards and performs transitions in a single operation.
    This ensures guard evaluation happens at the right time during transition processing.
    """
    try:
        with lock:
            # Skip if already transitioning
            if automaton.current_state == HybridAutomatonStatusEnum.TRANSITIONING.value:
                return
            
            # Initialize guard evaluation message
            eval_msg: GuardsEvaluation = GuardsEvaluation(stamp=stamp)
            # eval_msg.mode = validate_mode(available_modes, current_mode)
            eval_msg.success = True
            # eval_msg.transition_names = []
            # eval_msg.guard_evaluations = []
            # eval_msg.guard_priority = []
            
            # Evaluate all guards for current mode
            pending_transitions = []
            error_messages = []

            current_mode_configuration = automaton.modes[automaton.current_mode]
            current_mode_transitions = current_mode_configuration.transitions

            for transition in current_mode_transitions:
                print ('hello world')
                transition_name = transition.name
                
                # try:
                #     # Get state inputs for guard evaluation
                #     guard_config = transition_config['guard']
                #     state_inputs = [automaton_states[s] for s in guard_config['state_inputs']]
                    
                #     # Evaluate the guard
                #     guard_result = bool(guard_config['function'](*state_inputs))
                    
                #     # Store evaluation results
                #     eval_msg.transition_names.append(transition_key)
                #     eval_msg.guard_evaluations.append(guard_result)
                #     eval_msg.guard_priority.append(transition_config['priority'])
                    
                #     # If guard is true, add to pending transitions
                #     if guard_result:
                #         pending_transitions.append(transition_key)
                        
                # except Exception as e:
                #     error_messages.append(f"{transition_key}: {str(e)}")
                #     eval_msg.success = False
            
            # Handle any evaluation errors
            if error_messages:
                eval_msg.success = False
                eval_msg.message = f"guard evaluation exceptions: \n- " + "\n- ".join(error_messages)
                guards_evaluation_publisher.publish(eval_msg)
                status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ERROR))
                return
            
            # Publish guard evaluation results
            guards_evaluation_publisher.publish(eval_msg)
            
            # If no transitions are pending, stay in current mode
            if not pending_transitions:
                status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ACTIVE_MODE))
                return
            
            # Select highest priority transition
            selected_transition_key = _select_highest_priority_transition(
                current_mode_transitions, 
                pending_transitions
            )
            
            if selected_transition_key is None:
                status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ACTIVE_MODE))
                return
            
            # Publish transitioning status
            status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.TRANSITIONING))
            
            # Execute the selected transition
            transition_config = current_mode_transitions[selected_transition_key]
            
            # Handle reset if configured
            reset_config = transition_config.get('reset')
            if reset_config is not None:
                logger.info(f"Executing reset: {reset_config['name']}")
                reset_func = reset_config['function']
                state_inputs = _get_reset_inputs(automaton_states, reset_config['state_inputs'])
                reset_output = reset_func(*state_inputs)
                waypoints_publisher.publish(reset_output[0])
            
            # Publish new mode
            new_mode = parse_transition(available_modes, selected_transition_key)
            mode_publisher.publish(String(data=new_mode))
            
            logger.info(f"Transition executed: {current_mode} -> {new_mode} (via {selected_transition_key})")
            
            # Publish back to active status after transition
            status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ACTIVE_MODE))
            
    except Exception as e:
        logger.error(f"Unexpected exception in combined_transition_evaluation_callback: {str(e)}")
        status_publisher.publish(HybridAutomatonStatus(status=HybridAutomatonStatusEnum.ERROR))


def _select_highest_priority_transition(transition_config: dict, pending: List[str]) -> str:
    """
    Helper function to select the highest-priority transition from a list of pending transitions.
    Lower priority values have higher priority.
    """
    if len(pending) == 1:
        return pending[0]
    
    highest_priority = float('inf')
    selected_transition = None
    
    for transition_name in pending:
        priority = transition_config[transition_name]['priority']
        if priority < highest_priority:
            highest_priority = priority
            selected_transition = transition_name
    
    return selected_transition


def _get_reset_inputs(states: dict, state_input_keys: list) -> List[Any]:
    """Retrieves the state values for the given reset's state inputs."""
    return [states[key] for key in state_input_keys]


import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from hybrid_automaton_interfaces.msg import (
    HybridAutomatonGuardEvaluations,
    HybridAutomatonMode,
    HybridAutomatonStatus
)
from colav_interfaces.msg import WaypointsState

if __name__ == '__main__':
    path = '/home/ryan/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml'
    automaton = HybridAutomatonFactory.hybrid_automaton_registry(automaton_famd_path=path, generate_mmd_diagrams=False)

    print (automaton)


    rclpy.init()
    node = Node('test_node')
    mode_publisher = node.create_publisher(
        topic='mode',
        msg_type=HybridAutomatonMode,
        qos_profile=10
    )
    status_publisher = node.create_publisher(
        topic='status',
        msg_type=HybridAutomatonStatus,
        qos_profile=10
    )
    waypoints_publisher = node.create_publisher(
        topic='waypoints_state',
        msg_type=WaypointsState,
        qos_profile=10
    )
    guard_evaluation_publisher = node.create_publisher(
        topic='guards',
        msg_type=HybridAutomatonGuardEvaluations,
        qos_profile=10
    )

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    threading.Thread(target=executor.spin).start()

    rclpy.shutdown()


    combined_transition_evaluation_callback(
        lock=threading.Lock(),
        automaton=automaton,
        stamp=node.get_clock().now().to_msg(),
        mode_publisher=mode_publisher,
        status_publisher=status_publisher,
        waypoints_publisher=waypoints_publisher,
        guards_evaluation_publisher=guard_evaluation_publisher,
        logger=node.get_logger()
    )