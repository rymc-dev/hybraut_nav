import os

import rclpy
from rclpy.executors import MultiThreadedExecutor

from hybraut_nav_tactical import TacticalNode

def main():
    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    tactical_node = TacticalNode()
    executor.add_node(node=tactical_node)

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

if __name__ == '__main__':
    main()