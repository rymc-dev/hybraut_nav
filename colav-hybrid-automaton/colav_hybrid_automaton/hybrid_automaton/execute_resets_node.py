

import rclpy
from hybrid_automaton.scripts.nodes import ResetNode

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
