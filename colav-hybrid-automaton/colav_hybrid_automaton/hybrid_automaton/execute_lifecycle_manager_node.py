import rclpy
from rclpy.node import Node
from hybrid_automaton.scripts.nodes.lifecycle_node import LifecycleNodeHybridAutomaton

def main(arg=None):
    """"""
    rclpy.init()
    node = LifecycleNodeHybridAutomaton('lifecycle_manager', 'hybrid_automaton')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e
    
    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()