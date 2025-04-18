import rclpy
from colav_hybrid_chart.scripts.colav_hybrid_chart_node import HAChart


def main(args=None):
    rclpy.init()
    node = HAChart()
    rclpy.spin(node=node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
