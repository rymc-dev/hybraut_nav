# -*- coding: utf-8  -*-
# !/usr/bin/env python3
""" 
class defines a composite `StateBus` bus for the ros2 
events topic utilized by the watchdog FSM, provides utilities to 
simplify event publishing and subscription 
for the base FSM class.
"""

from dataclasses import dataclass
from rclpy.node import Node
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default
from typing import Type, Callable, Any
from hybraut_interfaces.msg import State
from enum import Enum

from hybraut_execution_engine.watchdog.hybraut_consts import StateEnum
from hybraut_execution_engine.watchdog.hybraut_bus.ros_bus import BaseBus
from typing import Union

@dataclass
class StateBus(BaseBus):
    """
    StateBus implementation using the base bus functionality.
    Manages the state of the watchdog FSM.
    """
    
    def __init__(self, node: Node, status_callback: Callable,
                 topic: str = "/automaton/status",
                 msg_type: Type = State,
                 qos: QoSProfile = None,
                 cb_group: CallbackGroup = None):
        
        if qos is None:
            qos = qos_profile_system_default
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if msg_type is None:
            msg_type = State
            
        super().__init__(
            node=node,
            callback=status_callback,
            topic_name=topic,
            msg_type=msg_type,
            qos=qos,
            cb_group=cb_group
        )
    
    def _create_message(self, status: Union[Enum, Any], message: str) -> Any:
        """Create an State message."""
        if State:
            return State(
                type=status.value if isinstance(status, Enum) else status,
                message=message,
                stamp=self.node.get_clock().now().to_msg(),
            )
        return None
    
    def publish_status(self, status: Union[Enum, Any], message: str = "") -> None:
        """Publish a status with more explicit naming."""
        self.publish(status, message)

    @classmethod
    def create_status_bus(node: Node, status_callback: Callable, **kwargs) -> 'StateBus':
        """Factory function to create a StateBus."""
        return StateBus(node=node, status_callback=status_callback, **kwargs)


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
        status_bus: StateBus = StateBus(
            node=node,
            status_callback=lambda msg: print(
                f"Received state: {msg.type}, Message: {msg.message}"
            ),
        )
        status_bus.publish(StateEnum.ACTIVE, "watchdog state: ACTIVE")
        import time

        time.sleep(0.01)
        status_bus.publish(StateEnum.TRANSITIONING, "watchdog state: TRANSITIONING")
        time.sleep(0.01)

        time.sleep(0.01)
        status_bus.publish(StateEnum.FATAL, "watchdog state: FATAL")
        time.sleep(0.01)
        
        status_bus.publish(StateEnum.SYSTEM_SHUTDOWN, "watchdog state: SYSTEM_SHUTDOWN")
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    finally:
        executor.shutdown()
        thread.join()
        node.destroy_node()

    rclpy.shutdown()

if __name__ == "__main__":
    main()
