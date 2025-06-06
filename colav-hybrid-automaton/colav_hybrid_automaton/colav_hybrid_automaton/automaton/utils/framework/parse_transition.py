from rclpy.node import Node

def parse_transition(node: Node, transition_name: str) -> str:
    """
    Publishes the transition when no reset is needed.
    """
    _, _, transition_to_raw = transition_name.partition("to_")

    # Split at the last underscore
    base, _, maybe_num = transition_to_raw.rpartition('_')

    if maybe_num.isdigit() and base in list(node._configuration['modes'].keys()):
        transition_to = base
    else:
        transition_to = transition_to_raw

    return transition_to