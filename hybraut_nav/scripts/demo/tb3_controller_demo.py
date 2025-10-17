#!/usr/bin/env python3
import time
import math
import threading
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import qos_profile_system_default
from rclpy.callback_groups import ReentrantCallbackGroup
from std_srvs.srv import Trigger
from nav_msgs.msg import Odometry
from hybraut_interfaces.msg import ContinousDynamics
from hybraut_nav_controller import ControllerNode


_last_print_time = 0.0
_print_interval = 1.0  # seconds


def odom_callback(msg: Odometry):
    """Extract and periodically print yaw (heading) from odometry message."""
    global _last_print_time
    now = time.time()
    if now - _last_print_time >= _print_interval:
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        yaw_deg = math.degrees(yaw)
        print(f"[ODOM] Current yaw: {yaw:.3f} rad ({yaw_deg:.1f}°)")
        _last_print_time = now


class ControllerCLINode(Node):
    def __init__(self):
        super().__init__('controller_cli_node')

        # === Subscriptions ===
        self.create_subscription(
            Odometry,
            '/odom',
            odom_callback,
            qos_profile=qos_profile_system_default,
            callback_group=ReentrantCallbackGroup()
        )

        # === Publishers ===
        self.continous_dynamics_pub = self.create_publisher(
            ContinousDynamics,
            '/hybraut_nav/tactical_node/continuous_dynamics',
            qos_profile=qos_profile_system_default,
        )

        # === Service Client ===
        self.toggle_client = self.create_client(
            Trigger,
            'hybraut_nav/controller_node/toggle'
        )

    def toggle_controller(self, activate=True):
        """Toggle controller service."""
        if not self.toggle_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Controller toggle service not available.')
            return False

        req = Trigger.Request()
        future = self.toggle_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.result() is not None:
            res = future.result()
            self.get_logger().info(
                f"{'Activated' if activate else 'Deactivated'} controller: {res.success}, msg: {res.message}"
            )
            return res.success
        else:
            self.get_logger().error('Toggle service call failed or timed out.')
            return False

    def publish_heading(self, heading):
        msg = ContinousDynamics()
        msg.desired_heading = float(heading)
        self.continous_dynamics_pub.publish(msg)
        self.get_logger().info(f'[CLI] Published desired heading: {heading:.2f} rad')


def main(args=None):
    rclpy.init(args=args)

    # === Executor ===
    executor = MultiThreadedExecutor()

    # === Nodes ===
    controller_node = ControllerNode()
    cli_node = ControllerCLINode()

    executor.add_node(controller_node)
    executor.add_node(cli_node)

    # === Run executor in background ===
    executor_thread = threading.Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    try:
        # Activate controller
        cli_node.toggle_controller(True)
        time.sleep(0.5)

        # Publish headings
        for heading in [np.pi, np.pi / 2, np.pi * 1.5]:
            cli_node.publish_heading(heading)
            time.sleep(30)

        # Deactivate controller
        cli_node.toggle_controller(False)
        cli_node.get_logger().info('[CLI] Mission complete.')

    except KeyboardInterrupt:
        cli_node.get_logger().info('Interrupted by user.')
    finally:
        executor.shutdown()
        controller_node.destroy_node()
        cli_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
