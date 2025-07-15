from threading import Lock
from builtin_interfaces.msg import Time
from rclpy.publisher import Publisher
from hybrid_automaton_interfaces.msg import HybridAutomatonMode 
from automaton._internal.model import HybridAutomaton
from hybrid_automaton_interfaces.msg import HybridAutomatonDynamicsEvaluation, HybridAutomatonStatus


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