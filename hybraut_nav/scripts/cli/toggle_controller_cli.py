#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import sys

def main():
    rclpy.init()
    node = Node("toggle_controller_cli")

    # Create client for the toggle service
    client = node.create_client(Trigger, "hybraut_nav/controller_node/toggle")

    if not client.wait_for_service(timeout_sec=5.0):
        node.get_logger().error("Controller toggle service not available.")
        return

    # Call service
    req = Trigger.Request()
    future = client.call_async(req)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)

    if future.result() is not None:
        print(f"[CLI] Success: {future.result().success}")
        print(f"[CLI] Message: {future.result().message}")
    else:
        print("[CLI] Service call failed or timed out.")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
