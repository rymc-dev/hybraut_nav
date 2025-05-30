
from rclpy.executors import MultiThreadedExecutor
import rclpy
from hybrid_automaton.scripts.nodes import HybridAutomatonMissionControlNode
import os

def main():
    rclpy.init()
    node = HybridAutomatonMissionControlNode(name='mission_control', namespace='colav/hybrid_automaton')
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())

    try:
        executor.add_node(node)
        executor.spin()
    except Exception as e:
        pass
    executor.shutdown()
    node.destroy_node()
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()