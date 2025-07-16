from rclpy.node import Node 
from typing import List

def select_highest_priority_transition(self: Node, pending: List[str]):
    """
    Helper function to select the highest-priority transition from a list of pending transitions.
    """
    if len(pending) == 1:
        return pending[0]
    
    highest_priority = float('inf')
    transition = None
    for name in pending:
        prio = self._configuration['modes'][self._mode]['transitions'][name]['priority']
        if prio < highest_priority:
            highest_priority = prio
            transition = name

    return transition