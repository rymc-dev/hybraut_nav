#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from unique_identifier_msgs.msg import UUID
from hybrid_automaton_interfaces.srv import Reset

def make_zero_uuid() -> UUID:
    u = UUID()
    u.uuid = [0]*16
    return u

def main():
    rclpy.init()
    node = Node('reset_states_client')
    client = node.create_client(Reset, '/hybrid_automaton/reset_states')

    if not client.wait_for_service(timeout_sec=5.0):
        node.get_logger().error('Service /hybrid_automaton/reset_states not available')
        return

    req = Reset.Request()
    req.transition_uuid = make_zero_uuid()
    req.reset_name = 'remove_first_waypoint'

    node.get_logger().info(f"Calling reset_states with reset_name='{req.reset_name}'…")
    future = client.call_async(req)

    # block here until the response comes back (or times out)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)

    if future.done():
        resp = future.result()
        node.get_logger().info(f"Response: success={resp.success}, message=\"{resp.message}\"")
    else:
        node.get_logger().error('Service call did not complete within 5 seconds')

    rclpy.shutdown()

if __name__ == '__main__':
    main()