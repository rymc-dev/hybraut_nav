import rclpy
from rclpy.node import Node

from rcl_interfaces.msg import Parameter
from std_msgs.msg import String

class TalkerNode(Node):
    def __init__(
        self,
        timer_period:float = float(1)
    ):
        super().__init__('talker')

        self.declare_parameter("topic", value="talker_topic")
        topic_name = self.get_parameter("topic").get_parameter_value().string_value

        self._talker_pub = self.create_publisher(
            String,
            topic_name,
            10
        )
        self.create_timer(timer_period, self.talker_callback)
        self.count = 0

    def talker_callback(self):
        """
        pubs a message on callback
        """
        msg = String()
        msg.data = str(f"Hello Everyone {self.count}")
        self._talker_pub.publish(msg)
        self.count += 1
        self.get_logger().info(f'publishing message: {msg}')


def main():
    rclpy.init()
    node = TalkerNode()
    
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