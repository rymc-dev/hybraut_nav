# !/usr/bin/python

""" 
TransitionHandler implements a subscription 
for transition events, when a transition is activated
we publish transitioning status, when transitioning is finished
move back to active
"""

import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher

class TransitionHandler:

    def __init__(self, node: Node, event_publisher: Publisher):
        self.node: Node = node

    def _create_subscription(self):
        self.node.create_subscription(

        )

    def transition_engine():
        ...

    def __call__(self, *args, **kwds):
        pass


""" below is test code not for production use. """

def main():
    ...

if __name__ == '__main__':
    main()