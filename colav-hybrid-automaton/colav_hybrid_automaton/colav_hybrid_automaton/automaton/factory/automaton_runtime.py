from rclpy.node import Node
from functools import partial
from colav_hybrid_automaton.automaton.constants import QOS_PROFILE
from rclpy.callback_groups import ReentrantCallbackGroup
from threading import Lock
from std_msgs.msg import String
from rclpy.publisher import Publisher
from rclpy.impl.rcutils_logger import RcutilsLogger
from typing import Tuple
from colav_hybrid_automaton.automaton.constants import HybridAutomatonStatus


def create_state_subscriptions(node: Node, state_configuration: dict) -> dict: 

    states = {}

    def make_state_callback(key):
        def state_callback(msg: str, key:str): 
            states[key] = msg
        return lambda msg: state_callback(msg, key)


    """create ros2 state subscriptions""" # TODO: FOR STATES NEED TO ADD TIMEOUT EXCEPTIONS BASED ON PARAMS
    for key, value in state_configuration.items():
        node.create_subscription(
            topic=value['topic'],
            msg_type=value['type'],
            callback = make_state_callback(key),
            qos_profile=QOS_PROFILE
        )
        states[key] = None

    return states

def create_state_publishers(node: Node) -> dict: 
    """create ros2 state subscriptions""" # TODO: FOR STATES NEED TO ADD TIMEOUT EXCEPTIONS BASED ON PARAMS
    for key, value in node._configuration['states'].items():
        node._configuration['states'][key]['state'] = None
        state_pub = node.create_publisher(
            topic=value['topic'],
            msg_type=value['type'],
            qos_profile=QOS_PROFILE
        )
        node._configuration['states'][key]['pub'] = state_pub

def generate_mode_profile(
    mode: String,
    mode_configuration: dict,
    transition_configuration: dict,
    dynamics_configuration: dict,
    invariants_configuration: dict,
    reset_configuration: dict,
    guard_configuration: dict,
) -> Tuple[str, dict, dict, dict]:
    """
    callback for receiving mode
    This function validates the mode received extracting transitions 
    data like the guards and resets functions assigning priority to each of them
    """
    try:
        mode_transitions_dict = {}
        mode_dynamics = {} 
        mode_invariant = {}     

        try:
            mode = mode.data.lower()

            mode_transitions = mode_configuration[mode].get('transitions', {})

            for mode_transition in mode_transitions:
                mode_transitions_dict[mode_transition] = {
                    'guard':  { 
                        **guard_configuration[transition_configuration[mode_transition]['guard']], 
                        'name': transition_configuration[mode_transition]['guard'] 
                    },
                    'reset': None if transition_configuration[mode_transition]['reset'] is None else { 
                        **reset_configuration[transition_configuration[mode_transition]['reset']],
                        'name': transition_configuration[mode_transition]['reset']
                    },
                    'priority': mode_configuration[mode]['transitions'][mode_transition]['priority']
                }

            dynamic_function_name = mode_configuration[mode]['dynamics']
            mode_dynamics[dynamic_function_name]  = {'function': dynamics_configuration[dynamic_function_name]['function'], 'state_inputs': dynamics_configuration[dynamic_function_name].get('state_inputs', [])}

            invariant_name = mode_configuration[mode]['invariants']
            mode_invariant[invariant_name] = {'function': invariants_configuration[invariant_name]['function'], 'state_inputs': invariants_configuration[invariant_name].get('state_inputs', [])}

        except Exception as e: 
            raise ValueError(f'Exception occured _on_mode__received_callback, invalid mode received: {str(e)}')
            
        return (mode, mode_transitions_dict, mode_dynamics, mode_invariant)
    except Exception as e:
        raise ValueError(f"unexpected error occured in 'colav_hybrid_automaton.automaton.callbacks.on_mode_callback': {str(e)}")
