#!/usr/bin/python3
"""
script for running the hybrid_automaton chart node

version 0.0.1
Author: Ryan McKee
Date: April 24, 2025
"""

import rclpy
from hybrid_automaton.scripts.nodes import ChartNode


def main(args=None):
    rclpy.init()
    node = ChartNode()

    try: 
        rclpy.spin(node=node)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down node.")
    except Exception as e:
        print (f"Exception occured: {e}")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
