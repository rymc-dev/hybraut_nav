import os

import rclpy
from rclpy.executors import MultiThreadedExecutor

from hybraut_nav_immediate import ImmediateNode

def main():
    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    immediate_node = ImmediateNode()
    executor.add_node(node=immediate_node)

    try:
        executor.spin()
    except Exception as e: 
        print (f'Exception occured during execution: {e}')
    except KeyboardInterrupt:
        print (f'Keyboard interrupt occured')

    executor.shutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()