import rclpy
from colav_hybrid_eval.scripts.nodes.dynamics_node import DynamicsNode

def main(args = None):
    rclpy.init()
    node = DynamicsNode()

    try: 
        rclpy.spin(node=node)   
    except KeyboardInterrupt:
        pass
    except Exception as e: 
        print (f'Exception occured: {e}')

    rclpy.shutdown()

if __name__ == '__main__':
    main()