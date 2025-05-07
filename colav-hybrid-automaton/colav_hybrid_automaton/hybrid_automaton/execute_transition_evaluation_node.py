#!/usr/bin/python3
"""
script for running the colav_hybrid_eval GuardsNode

Version: 0.0.1
Author: Ryan McKee
Date: April 17, 2025
"""

import rclpy
from hybrid_automaton.scripts.nodes import TransitionEvaluatorNode


def main(args=None):
    rclpy.init()
    node = TransitionEvaluatorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down node.")
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
