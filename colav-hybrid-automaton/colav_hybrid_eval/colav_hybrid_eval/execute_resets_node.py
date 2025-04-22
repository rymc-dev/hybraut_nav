

import rclpy
from colav_hybrid_eval.scripts.nodes.resets_node import ResetNode

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ResetNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Exception occured: {str(e)}')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
