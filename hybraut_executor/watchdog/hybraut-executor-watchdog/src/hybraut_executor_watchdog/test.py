import rclpy
from rclpy.node import Node
from hybraut_interfaces.msg import AutomatonEvents
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

QOS = QoSProfile(depth=10, reliability=qos_profile_system_default.reliability)

rclpy.init(args=None)

node = Node("test_node")


def trigger_transition(msg: AutomatonEvents):
    print (f"Received event: {msg.type}, Message: {msg.message}")

node.create_subscription(
    AutomatonEvents,
    "/automaton/events",
    lambda msg:trigger_transition(msg),
    qos_profile=QOS,
    callback_group=ReentrantCallbackGroup()
)

executor: MultiThreadedExecutor = MultiThreadedExecutor(num_threads=2)
executor.add_node(node)
executor.spin()

rclpy.shutdown()


