#!/usr/bin/python3
"""
script for running the colav_hybrid_eval DynamicsNode

Version: 0.0.1
Author: Ryan McKee
Date: April 17, 2025
"""

import rclpy
from hybrid_automaton.scripts.nodes import DynamicFeedbackLifecycleNode
from rclpy.executors import MultiThreadedExecutor


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DynamicFeedbackLifecycleNode('dynamics_node', 'hybrid_automaton')
        executor = MultiThreadedExecutor(num_threads=4)  # Create a multi-threaded executor
        executor.add_node(node)  # Add your node to the executor
        executor.spin()  # Spin the executor instead of rclpy.spin
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Exception occurred: {str(e)}')
    finally:
        if node:
            node.destroy_node()  # Ensure the node is properly destroyed after spinning
        rclpy.shutdown()


if __name__ == '__main__':
    main()
