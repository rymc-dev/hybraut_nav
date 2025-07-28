from dataclasses import dataclass, field
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.subscription import Subscription
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_default
from typing import (
    Type,
    Callable,
    Optional,
    Any
)
from hybraut_interfaces.msg import AutomatonStatus
from enum import Enum



@dataclass
class StatusBus:
    _node: Node
    _topic: str
    _msg_type: Type
    _subscription_callback: Callable

    # now all the defaults come *after*
    _qos: Optional[QoSProfile] = field(
        init=True,
        default_factory=lambda: qos_profile_default
    )
    _cb_group: Optional[CallbackGroup] = field(
        init=True,
        default_factory=ReentrantCallbackGroup()
    )

    _state_publisher: Publisher     = field(default=None, init=False)
    _state_subscription: Subscription = field(default=None, init=False)
    _is_active: bool                 = field(default=False, init=False)

    def activate(self) -> None:
        # pass in the node, qos, and cb_group stored on self
        self._create_state_publisher(self._node, self._qos, self._cb_group)
        self._create_state_subscription(self._node, self._qos, self._cb_group)
        self._is_active = True

    def deactivate(self) -> None:
        if self._state_publisher:
            self._node.destroy_publisher(self._state_publisher)
        if self._state_subscription:
            self._node.destroy_subscription(self._state_subscription)
        self._is_active = False

    def publish_state(self, message: Any) -> None:
        if not self._is_active or not self._state_publisher:
            raise RuntimeError(f"State topic '{self._topic}' is not active for publishing")
        self._state_publisher.publish(message)

    # now each helper actually takes the things it needs:
    def _create_state_publisher(
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

    def _create_state_subscription(
        self,
        node: Node,
        qos: QoSProfile,
        cb_group: CallbackGroup
    ) -> None:
        if not isinstance(node, Node):
            raise RuntimeError("Invalid node type, should be rclpy.node.Node")
        if self._state_subscription is None:
            self._state_subscription = node.create_subscription(
                msg_type=self._msg_type,
                topic=self._topic,
                callback=lambda msg: self._subscription_callback(msg),
                qos_profile=qos,
                callback_group=cb_group()
            )

    @classmethod
    def initialize_state_bus(
        cls,
        node: Node,
        topic: str,
        msg_type: Type,
        subscription_callback: Callable,
        qos: Optional[QoSProfile] = qos_profile_default,
        cb_Group: Optional[CallbackGroup] = ReentrantCallbackGroup,
    ) -> 'StateBus':
        """generate StateBus dataclass instance

        Args:
            node (Node): _description_
            topic (str): _description_
            msg_type (Type): _description_
            subscription_callback (Callable): _description_
            qos (Optional[QoSProfile], optional): _description_. Defaults to qos_profile_default.
            cb_Group (Optional[CallbackGroup], optional): _description_. Defaults to ReentrantCallbackGroup.

        Returns:
            StateBus: _description_
        """
        return cls(
            _node = node,
            _topic=topic,
            _msg_type=msg_type,
            _subscription_callback=subscription_callback,
            _qos=qos,
            _cb_group=cb_Group
        )
    

def main():
    pass

if __name__ == '__main__':
    main()