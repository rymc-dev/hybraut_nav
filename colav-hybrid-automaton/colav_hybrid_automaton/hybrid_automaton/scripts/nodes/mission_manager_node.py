import rclpy
from rclpy.node import Node

class MissionControllerNode(Node):
    
    def __init__():
        super().__init__('mission_control', namespace='hybrid_automaton')


def main():
    node = MissionControllerNode()
    try:
        rclpy.spin(node)
    except Exception as e:
        print(e)

if __name__ == '__main__': 
    main()