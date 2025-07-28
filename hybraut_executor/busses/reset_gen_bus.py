from dataclasses import dataclass, field
from rclpy.node import Node
from typing import Type
from rclpy.publisher import Publisher
from rclpy.qos import QoSProfile, qos_profile_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from typing import Optional


@dataclass 
class ResetGenBus:
    _node: Node
    _topic = str
    _msg_type: Type
    _reset_gen_publisher: Publisher

    # now all the defaults come *after*
    _qos: Optional[QoSProfile] = field(
        init=True,
        default_factory=lambda: qos_profile_default
    )
    _cb_group: Optional[CallbackGroup] = field(
        init=True,
        default_factory=ReentrantCallbackGroup()
    )

    def activate(self) -> None:
        self._publisher = self._create_reset_gen_publisher()

    def _create_reset_gen_publisher(
        self,
        node: Node,
        qos: QoSProfile,
        cb_group: CallbackGroup
    ) -> None:
        if not isinstance(node, Node):
            raise RuntimeError("Invalid node type, should be rclpy.node.Node")
        if self._state_publisher is None:
            self._state_publisher = node.create_publisher(
                msg_type=self._msg_type,
                topic=self._topic,
                qos_profile=qos,
                callback_group=cb_group()
            )
