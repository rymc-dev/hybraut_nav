from rclpy.node import Node
import rclpy
from std_msgs.msg import String

class ListenerNode(Node):
    def __init__(self):
        super().__init__('listener')

        self.declare_parameter('topic', value='topic_name')

        topic_name = self.get_parameter('topic').get_parameter_value().string_value

        self._talker_pub = self.create_subscription(
            String,
            topic_name,
            self.listener_callback,
            10
        )

    def listener_callback(self, msg: String):
        """
        pubs a message on callback
        """
        self.get_logger().info(f'Received: {msg.data}!')
    

def main():
    rclpy.init()
    node = ListenerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print (f'Exception occured: {e}')
    finally:
        node.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()