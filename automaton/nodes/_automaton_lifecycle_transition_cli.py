#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition

class LifecycleClient(Node):
    def __init__(self, target_node_name):
        super().__init__('lifecycle_transition_client')
        self.target_node = target_node_name
        self.cli = self.create_client(ChangeState, f'/{self.target_node}/change_state')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'Waiting for /{self.target_node}/change_state service...')

        self.send_configure_transition()

    def send_configure_transition(self):
        req = ChangeState.Request()
        req.transition.id = Transition.TRANSITION_CONFIGURE

        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None and future.result().success:
            self.get_logger().info(f'{self.target_node} transitioned to INACTIVE (CONFIGURE successful).')
        else:
            self.get_logger().error('Failed to configure the lifecycle node.')

        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    target_node = 'hybrid_automaton' # sys.argv[1] if len(sys.argv) > 1 else 'hybrid_automaton'
    node = LifecycleClient(target_node)


if __name__ == '__main__':
    main()
