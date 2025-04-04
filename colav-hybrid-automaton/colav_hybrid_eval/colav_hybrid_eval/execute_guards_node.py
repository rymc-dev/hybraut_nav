import rclpy
from colav_hybrid_eval.scripts.guards_node import HAGuardsNode

def main(args = None):
    rclpy.init()
    node = HAGuardsNode()
    rclpy.spin(node=node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()