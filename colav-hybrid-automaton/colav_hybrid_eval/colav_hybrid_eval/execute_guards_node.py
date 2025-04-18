#!/usr/bin/python3
"""
script for running the colav_hybrid_eval GuardsNode

Version: 0.0.1
Author: Ryan McKee
Date: April 17, 2025
"""


import rclpy
from colav_hybrid_eval.scripts.nodes.guards_node import GuardsNode


def main(args=None):
    rclpy.init()
    node = GuardsNode()

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
