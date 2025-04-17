import rclpy
from colav_hybrid_eval.scripts.nodes.guards_node import GuardsNode

def main(args = None):
    rclpy.init()
    node = GuardsNode()

    try: 
        rclpy.spin(node=node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print (f'Exception occured: {str(e)}')

    rclpy.shutdown()

if __name__ == '__main__':
    main()