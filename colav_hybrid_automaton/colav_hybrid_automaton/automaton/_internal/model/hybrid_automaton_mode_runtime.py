from rclpy.node import Node
from functools import partial
from colav_hybrid_automaton.automaton._internal.constants import QOS_PROFILE
from rclpy.callback_groups import ReentrantCallbackGroup
from threading import Lock
from std_msgs.msg import String
from rclpy.publisher import Publisher
from rclpy.impl.rcutils_logger import RcutilsLogger
from typing import Tuple
from colav_hybrid_automaton.automaton._internal.constants import HybridAutomatonStatusEnum


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
    mode: HybridAutomatonStatusEnum,
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
            mode_transitions = mode_configuration[mode.type].get('transitions', {})

            for mode_transition in mode_transitions:
                mode_transitions_dict[mode_transition] = {
                    'guard':  { 
                        'instance': guard_configuration[transition_configuration[mode_transition]['guard']]['instance'],
                        'state_inputs': guard_configuration[transition_configuration[mode_transition]['guard']]['state_inputs'],
                        'name': transition_configuration[mode_transition]['guard'] 
                    },
                    'reset': None if transition_configuration[mode_transition]['reset'] is None else { 
                        'instance': reset_configuration[transition_configuration[mode_transition]['reset']]['instance'],
                        'state_inputs': reset_configuration[transition_configuration[mode_transition]['reset']]['state_inputs'],
                        'reset_targets': reset_configuration[transition_configuration[mode_transition]['reset']]['reset_targets'],
                        'name': transition_configuration[mode_transition]['reset']
                    },
                    'priority': mode_configuration[mode.type]['transitions'][mode_transition]['priority']
                }

            dynamic_function_name = mode_configuration[mode.type]['dynamics']
            mode_dynamics_dict  = {
                'instance': dynamics_configuration[dynamic_function_name]['instance'], 
                'state_inputs': dynamics_configuration[dynamic_function_name].get('state_inputs', []), 
                'dynamic_outputs': dynamics_configuration[dynamic_function_name].get('dynamic_outputs', []), 
                'name': dynamic_function_name
            }

            invariant_name = mode_configuration[mode.type]['invariants']
            mode_invariants_dict = {
                'instance': invariants_configuration[invariant_name]['instance'], 
                'state_inputs': invariants_configuration[invariant_name].get('state_inputs', []),
                'name': invariant_name    
            }

        except Exception as e: 
            raise ValueError(f'Exception occured _on_mode__received_callback, invalid mode received: {str(e)}')
            
        return (mode, mode_transitions_dict, mode_dynamics_dict, mode_invariants_dict)
    except Exception as e:
        raise ValueError(f"unexpected error occured in 'colav_hybrid_automaton.automaton.callbacks.on_mode_callback': {str(e)}")
