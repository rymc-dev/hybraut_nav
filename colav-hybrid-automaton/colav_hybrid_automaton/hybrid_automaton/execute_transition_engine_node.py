#!/usr/bin/python3
"""
script for running the hybrid_automaton chart node

version 0.0.1
Author: Ryan McKee
Date: April 24, 2025
"""

import rclpy
from hybrid_automaton.scripts.nodes import TransitionEngineManagedNode
from rclpy.executors import MultiThreadedExecutor


def main(args=None):
    rclpy.init()
    node = TransitionEngineManagedNode(name='transition_engine', namespace='hybrid_automaton')
    executor = MultiThreadedExecutor(num_threads=4)

    try: 
        executor.add_node(node)
        executor.spin()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down node.")
    except Exception as e:
        print (f"Exception occured: {e}")
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
