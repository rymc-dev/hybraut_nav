from hybrid_automaton.scripts.nodes import HybridAutomatonLifecycleNode
from rclpy.executors import MultiThreadedExecutor
import rclpy
import os

def main():
    rclpy.init()
    node = HybridAutomatonLifecycleNode(name='lifecycle', namespace='colav/hybrid_automaton')
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())

    try:
        executor.add_node(node)
        executor.spin()
    except Exception as e:
        executor.shutdown()
        node.destroy_node()
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()