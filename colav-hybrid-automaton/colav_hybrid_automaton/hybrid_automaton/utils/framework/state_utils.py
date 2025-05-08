from rclpy.node import Node
from functools import partial

from hybrid_automaton.config import QOS_PROFILE

def create_state_subscriptions(node: Node) -> dict: 

    def state_callback(node: Node, msg: str, key:str): 
        node.config['states'][key].__setitem__('state', msg)

    """create ros2 state subscriptions""" # TODO: FOR STATES NEED TO ADD TIMEOUT EXCEPTIONS BASED ON PARAMS
    for key, value in node.config['states'].items():
        node.config['states'][key]['state'] = None
        state_sub = node.create_subscription(
            topic=value['topic'],
            msg_type=value['type'],
            callback = lambda msg, key=key: state_callback(node, msg, key),
            qos_profile=QOS_PROFILE
        )
        node.config['states'][key]['sub'] = state_sub

def create_state_publishers(node: Node) -> dict: 
    """create ros2 state subscriptions""" # TODO: FOR STATES NEED TO ADD TIMEOUT EXCEPTIONS BASED ON PARAMS
    for key, value in node.config['states'].items():
        node.config['states'][key]['state'] = None
        state_pub = node.create_publisher(
            topic=value['topic'],
            msg_type=value['type'],
            qos_profile=QOS_PROFILE
        )
        node.config['states'][key]['pub'] = state_pub