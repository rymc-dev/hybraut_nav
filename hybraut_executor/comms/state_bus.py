from rclpy.node import Node
from typing import Any, Type, Callable
from dataclasses import dataclass, field
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default


@dataclass
class StateBus:
    node: Node
    topic: str
    msg_type: Type[Any]
    state_callback: Callable[[Any], None]
    qos: QoSProfile = field(default_factory=lambda: qos_profile_system_default)
    cb_group: CallbackGroup = field(default_factory=ReentrantCallbackGroup)

    def __post_init__(self):
        self.node.create_subscription(
            msg_type=self.msg_type,
            topic=self.topic,
            callback=lambda msg: self.state_callback(msg),
            qos_profile=self.qos,
            callback_group=self.cb_group
        )

    @classmethod
    def create(
        cls,
        node: Node,
        topic: str,
        msg_type: Type[Any],
        state_callback: Callable[[Any], None],
        qos: QoSProfile = None,
        cb_group: CallbackGroup = None
    ) -> "StateBus":
        return cls(
            node=node,
            topic=topic,
            msg_type=msg_type,
            state_callback=state_callback,
            qos=qos if qos else qos_profile_system_default,
            cb_group=cb_group if cb_group else ReentrantCallbackGroup()
        )
