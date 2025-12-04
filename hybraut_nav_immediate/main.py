import time
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from hybraut_nav_controller import ControllerNode

from nav_msgs.msg import Odometry
import math
from threading import Thread


from rclpy.qos import qos_profile_system_default
from rclpy.callback_groups import ReentrantCallbackGroup
from hybraut_interfaces.msg import ContinousDynamics
from std_srvs.srv import Trigger
import numpy as np



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


def main(args=None):
    rclpy.init(args=args)
    
    executor = MultiThreadedExecutor()

    # ✅ Start your actual controller node
    node = ControllerNode()

    # ✅ CLI node for publishing commands, toggling controller, and listening to odometry
    cli_node = Node('controller_cli_node')

    # ✅ Subscribe to /odom on CLI node
    cli_node.create_subscription(
        Odometry,
        '/odom',
        odom_callback,
        qos_profile=qos_profile_system_default,
        callback_group=ReentrantCallbackGroup()
    )

    executor.add_node(node)
    executor.add_node(cli_node)
    
    # Spin executor in a background thread
    thread = Thread(target=executor.spin, daemon=True)

    try: 
        thread.start()

        # === Publishers ===
        continous_dynamics_pub = cli_node.create_publisher(
            ContinousDynamics,
            '/hybraut_nav/tactical_node/continuous_dynamics',
            qos_profile=qos_profile_system_default,
        )

        # === Create Trigger client for toggling controller ===
        toggle_cli = cli_node.create_client(
            Trigger,
            'hybraut_nav/controller_node/toggle'
        )
        toggle_cli.wait_for_service(timeout_sec=10.0)
        req = Trigger.Request()

        # === ACTIVATE controller ===
        print("[CLI] Activating controller node...")
        future = toggle_cli.call_async(req)
        rclpy.spin_until_future_complete(cli_node, future, timeout_sec=5.0)
        if future.result() is not None:
            print(f"[CLI] Activation succeeded: {future.result().message}")

        # === Publish first heading ===
        desired_heading_1 = np.pi
        continous_dynamics_msg = ContinousDynamics(desired_heading=desired_heading_1)
        continous_dynamics_pub.publish(continous_dynamics_msg)
        print(f'[CLI] Published desired heading: {desired_heading_1:.2f} rad')

        # === Wait and publish more headings ===
        time.sleep(30)
        new_desired_heading_2 = np.pi / 2
        continous_dynamics_msg.desired_heading = new_desired_heading_2
        continous_dynamics_pub.publish(continous_dynamics_msg)
        print(f'[CLI] Published new desired heading: {new_desired_heading_2:.2f} rad')

        time.sleep(30)
        new_desired_heading_3 = np.pi * 1.5
        continous_dynamics_msg.desired_heading = new_desired_heading_3
        continous_dynamics_pub.publish(continous_dynamics_msg)
        print(f'[CLI] Published new desired heading: {new_desired_heading_3:.2f} rad')

        # === DEACTIVATE controller ===
        print("[CLI] Deactivating controller node...")
        future = toggle_cli.call_async(req)
        rclpy.spin_until_future_complete(cli_node, future, timeout_sec=5.0)
        if future.result() is not None:
            print(f"[CLI] Deactivation succeeded: {future.result().message}")

        print('[CLI] Mission complete.')

    except Exception as e: 
        print(f"[ERROR] {e}")

    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()