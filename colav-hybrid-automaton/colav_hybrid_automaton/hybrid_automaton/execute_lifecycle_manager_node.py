import rclpy
from rclpy.node import Node
from hybrid_automaton.scripts.nodes import LifeCycleManager

def main(arg=None):
    """"""
    rclpy.init()
    node = LifeCycleManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e
    
    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()