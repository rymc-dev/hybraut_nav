from hybraut_interfaces.msg import AutomatonEvents
from dataclasses import dataclass, field
from typing import Callable

from rclpy.node import Node
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup

from hybraut_executor.watchdog.constants import EventEnum


@dataclass
class EventBus:
    """
    EventBus is a class that manages events for the watchdog fsm.
    It provides methods to publish and subscribe to events.
    """

    node: Node = field(init=True)
    event_callback: Callable = field(init=True)

    topic: str = field(default="/automaton/events", init=True)
    msg_type: type = field(default=AutomatonEvents, init=True)
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

    def publish(self, event: EventEnum, message: str = ""):
        """
        Publish an event to the event bus.
        """
        self.publisher.publish(
            AutomatonEvents(
                type=event.value,
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
        event_bus: EventBus = EventBus(
            node=node,
            event_callback=lambda msg: print(
                f"Received event: {msg.type}, Message: {msg.message}"
            ),
        )
        event_bus.publish(EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated")
        import time

        time.sleep(0.01)
        event_bus.publish(EventEnum.TRANSITION_COMPLETE, "transition completed")
        time.sleep(0.01)

        event_bus.publish(EventEnum.RECOVERY_FAILED, "mode guard deactivated")
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
