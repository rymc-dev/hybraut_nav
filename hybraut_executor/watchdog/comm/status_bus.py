from dataclasses import dataclass, field
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default
from typing import Type, Callable, Optional, Any
from hybraut_interfaces.msg import AutomatonStatus
from enum import Enum

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

from constants import StatusEnum


@dataclass
class StatusBus:
    """
    StatusBus is a class that manages the state of the watchdog fsm.
    It provides methods to publish and subscribe to state changes.
    """

    node: Node = field(init=True)
    status_callback: Callable = field(init=True)

    topic: str = field(default="/automaton/status", init=True)
    msg_type: type = field(default=AutomatonStatus, init=True)
    qos: QoSProfile = field(default=qos_profile_system_default, init=True)
    cb_group: CallbackGroup = field(default=ReentrantCallbackGroup(), init=True)

    subscription: Subscription = field(default=None, init=False)
    publisher: Publisher = field(default=None, init=False)

    def __post_init__(self):
        self.publisher = self.node.create_publisher(
            self.msg_type, self.topic, self.qos, callback_group=self.cb_group
        )
        self.subscription = self.node.create_subscription(
            self.msg_type,
            self.topic,
            self.event_callback,
            self.qos,
            callback_group=self.cb_group,
        )

    def publish(self, status: StatusEnum, message: str = ""):
        """
        Publish an event to the event bus.
        """
        self.publisher.publish(
            AutomatonStatus(
                type=status.value,
                message=message,
                stamp=self.node.get_clock().now().to_msg(),
            )
        )

    def destroy(self):
        """
        Destroy the event bus, cleaning up subscriptions and publishers.
        """
        if self.subscription:
            self.node.destroy_subscription(self.subscription)
            self.subscription = None
        if self.publisher:
            self.node.destroy_publisher(self.publisher)
            self.publisher = None
        self.node = None


def main():
    """
    Main function to demonstrate the usage of EventBus.
    This is just a placeholder and should be replaced with actual usage.
    """
    import rclpy
    from rclpy.executors import MultiThreadedExecutor, Executor
    import os
    import threading

    rclpy.init()
    executor: Executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    node = Node("mock_node")
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    try:
        status_bus: StatusBus = StatusBus(
            node=node,
            event_callback=lambda msg: print(
                f"Received status: {msg.type}, Message: {msg.message}"
            ),
        )
        status_bus.publish(StatusEnum.ACTIVE, "hybraut is active")
        import time

        time.sleep(0.01)
        status_bus.publish(StatusEnum.TRANSITIONING, "hybraut is transitioning")
        time.sleep(0.01)

        status_bus.publish(StatusEnum.FATAL, "hybraut is in a fatal state")
        time.sleep(0.01)
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    finally:
        executor.shutdown()
        thread.join()
        node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
