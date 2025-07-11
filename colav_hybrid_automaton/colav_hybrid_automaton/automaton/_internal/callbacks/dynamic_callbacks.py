from rclpy.node import Node
from typing import List, Any, Dict, Callable
from threading import Lock
from colav_hybrid_automaton.automaton._internal.utils import validate_mode
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher
from hybrid_automaton_interfaces.msg import HybridAutomatonMode 
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton
from hybrid_automaton_interfaces.msg import HybridAutomatonDynamicsEvaluation, HybridAutomatonStatus
import threading

from colav_interfaces.msg import AgentState, WaypointsState

def _validate_current_mode(automaton_model: HybridAutomaton) -> None:
    """Validate that the current mode exists in the automaton"""
    current_mode = automaton_model.current_mode
    if current_mode not in automaton_model.modes:
        raise ValueError(f"Invalid mode type: {current_mode}")

def _evaluate_dynamics(automaton_model: HybridAutomaton, stamp: Time) -> HybridAutomatonDynamicsEvaluation:
    """evaluates the dynamics for the current automaton mode"""
    msg = HybridAutomatonDynamicsEvaluation(
        mode=HybridAutomatonMode(type=automaton_model.current_mode, stamp=stamp),
        stamp=stamp
    )
    
    try:
        dynamics_class = automaton_model.modes[automaton_model.current_mode].dynamics.instance
        dynamic_name = dynamics_class.get_dynamics_info()['class_name']
        dynamics_description = dynamics_class.get_dynamics_info()['description']
        dynamics_state_input_keys = dynamics_class.state_input_spec_names()
        dynamic_output_spec_names = dynamics_class.dynamic_output_spec_names()
        dynamic_output_spec_units = dynamics_class.dynamic_output_spec_units()

        state_kwargs = {
            state_key: automaton_model.states[state_key].current_state
            for state_key in dynamics_state_input_keys
        }
        dynamic_outputs = dynamics_class.__call__(**state_kwargs)
        msg.dynamic_name = dynamic_name
        msg.dynamic_description = dynamics_description
        msg.dynamic_parameter_names=dynamic_output_spec_names
        msg.dynamic_parameter_values = [getattr(dynamic_outputs, name) for name in dynamic_output_spec_names]
        msg.dynamics_parameter_units = dynamic_output_spec_units
    except Exception as e:
        msg.error = True
        msg.message = f"exception occured: {str(e)}"

    return msg


def dynamics_evaluation_callback(
        lock: Lock,
        automaton_model: HybridAutomaton,
        stamp: Time,
        dynamics_evaluation_publisher: Publisher,
        status_publisher: Publisher
):
    """
    Callback for evaluating dynamics in the hybrid automaton on a timer.

    At regular time intervals, this function evaluates the dynamics associated with the 
    current mode of the hybrid automaton.

    We publish dynamics based on agent_state and other states assigend to the dynamic controllers
    in the hybrid automaton dynamics module, we publish the dynamics updates to '/hybrid_automaton/dynamics
    and at the same time if anything goes wrong we publish status updates to '/hybrid_automaton/status
    """
    try:
        with lock:
            _validate_current_mode(automaton_model)
            
            evaluation_result:HybridAutomatonDynamicsEvaluation = _evaluate_dynamics(automaton_model, stamp)

            dynamics_evaluation_publisher.publish(evaluation_result)
    except Exception as e:
        status_publisher.publish(HybridAutomatonStatus(
            type=HybridAutomatonStatus.STATUS_ERROR, 
            meesage=f"exception occured during dynamics evaluation: {str(e)}",
            stamp=stamp
        ))


import rclpy
from rclpy.qos import QoSProfile
from rclpy.executors import MultiThreadedExecutor
from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory

if __name__ == '__main__':
    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=2)
    mock_node = Node('mock_node')
    executor.add_node(mock_node)

    lock = threading.Lock()
    automaton_model:HybridAutomaton = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path='/home/ryan/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
        generate_mmd_diagrams=False
    )
    automaton_model.create_state_publishers(node=mock_node)
    automaton_model.create_state_subscriptions(node=mock_node)
    stamp = Time()
    dynamics_evaluation_publisher = mock_node.create_publisher(
        topic = '/hybrid_automaton/dynamics',
        msg_type = HybridAutomatonDynamicsEvaluation,
        qos_profile = QoSProfile(depth=10)
    ) 
    status_publisher = mock_node.create_publisher(
        topic = '/hybrid_automaton/status',
        msg_type = HybridAutomatonStatus,
        qos_profile = QoSProfile(depth=10)
    )

    threading.Thread(target=executor.spin).start()
    
    dynamics_evaluation_callback(
        lock=lock,
        automaton_model=automaton_model,
        stamp=stamp,
        dynamics_evaluation_publisher=dynamics_evaluation_publisher,
        status_publisher=status_publisher
    )

    rclpy.shutdown()

# def evaluate_dynamics_timer_callback(
#     lock: Lock,
#     mode: HybridAutomatonMode,
#     available_modes: Dict[int, str],
#     mode_dynamics: Dict[str, Callable[..., Any]],
#     states: Dict[str, dict],
#     stamp: Time,
#     dynamic_publisher: Publisher,
#     logger: RcutilsLogger
# ):
#     """
#     Evaluate and publish dynamics based on the current mode and system state.
#     """
#     try:
#         with lock:
#             msg = HybridAutomatonDynamics(stamp=stamp)
#             try:
#                 validate_mode(available_modes, mode)
                
#                 # msg.mode = validated_mode

#                 # Extract the dynamic function key (e.g., 'cruise')
#                 msg.dynamic_parameters.controller_name = mode_dynamics['name']
#                 dynamics_instance = mode_dynamics['instance']
#                 state_input_keys = mode_dynamics['state_inputs']
#                 state_inputs = _get_dynamic_inputs(state_input_keys, states)

#                 msg.dynamic_parameters.dynamic_name = mode_dynamics['dynamic_outputs']['dynamic_parameter_names']
#                 msg.dynamic_parameters.dynamic_units = mode_dynamics['dynamic_outputs']['dynamic_parameter_metrics']
#                 msg.dynamic_parameters.dynamic_value = dynamics_instance.__call__(**state_inputs)
#                 msg.success = True
            
#             except Exception as e:
#                 msg.success = False
#                 msg.message = f"exception occured during '{mode}' dynamic evaluation: '{str(e)}'"

#             dynamic_publisher.publish(msg)
#     except Exception as e:
#         logger.error(f"unexpected exception occured during 'colav_hybrid_automaton.automaton.callbacks.dynamic_callbacks.evaluate_dynamics_timer_callback': '{str(e)}'")

# def _get_dynamic_inputs(state_input_keys: str, states: dict) -> List[Any]:
#     """
#     Extract inputs for the dynamic function from the states dictionary.
#     """

#     return {k: states[k] for k in state_input_keys}
