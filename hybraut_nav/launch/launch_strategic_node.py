import os
import rclpy
from rclpy.executors import MultiThreadedExecutor
from hybraut_nav_strategy import StrategyNode

def main():
    rclpy.init()

    node = StrategyNode()
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())

    try:
        executor.spin()
    except Exception as e: 
        raise e
    except KeyboardInterrupt: 
        print (f'Keyboard interrupt.')


    rclpy.shutdown()

if __name__ == '__main__':
    main()