# !/usr/bin/env python3
""" """

from rclpy.node import Node
from typing import Any, Type, Callable
from dataclasses import dataclass, field
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default
from hybraut_model._states import State
from rclpy.subscription import Subscription


@dataclass
class WorldStateHandler:
    node: Node
    state: State
    qos: QoSProfile = field(default_factory=lambda: qos_profile_system_default)
    cb_group: CallbackGroup = field(default_factory=ReentrantCallbackGroup)

    _state_subscription: Subscription = field(init=False, default=None)

    def __post_init__(self):
        self._state_subscription = self.node.create_subscription(
            msg_type=self.state._msg_type,
            topic=self.state._topic,
            callback=lambda msg: self.state.update_state(msg),
            qos_profile=self.qos,
            callback_group=self.cb_group,
        )

    @classmethod
    def create(
        cls,
        node: Node,
        state: State,
        qos: QoSProfile = qos_profile_system_default,
        cb_group: CallbackGroup = ReentrantCallbackGroup(),
    ) -> "WorldStateHandler":
        return cls(
            node=node,
            state=state,
            qos=qos if qos else qos_profile_system_default,
            cb_group=cb_group if cb_group else ReentrantCallbackGroup(),
        )


class WorldStateHandlerHub:
    pass


def main():
    import rclpy
    from rclpy.node import Node
    from rclpy.executors import MultiThreadedExecutor
    import threading
    from geometry_msgs.msg import PoseStamped

    rclpy.init()

    node = Node("node")

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    state = State(name="pose_stamped", topic="/imu", msg_type=PoseStamped)

    world_state_handler = WorldStateHandler.create(
        node=node,
        state=state,
    )

    import time

    time.sleep(100.0)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
