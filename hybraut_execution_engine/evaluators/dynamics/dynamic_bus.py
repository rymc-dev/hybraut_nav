# !/usr/bin/env python3

""" """

from dataclasses import dataclass, field
from rclpy.publisher import Publisher
from typing import Any, Type

from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.node import Node
from typing import Dict
from hybraut_models.core.dynamics import DynamicsRegistry


@dataclass
class DynamicsBus:
    _dynamic_name: str = field(init=True)
    _dynamic_publisher: Publisher = field(init=True)

    def publish_dynamic(self, msg: Any):
        if not isinstance(msg, self._dynamic_publisher.msg_type):
            raise RuntimeError(
                f"attempted to publish invalid msg type: {type(msg)}, expected {self._dynamic_type}"
            )

        try:
            self._dynamic_publisher.publish(msg)
        except Exception as e:
            raise Exception(f"exception occured during 'publish_dynamic': {str(e)}")

    @classmethod
    def create_dynamic_bus(
        cls,
        node: Node,
        dynamic_name: str,
        dynamic_topic: str,
        dynamic_type: Type,
        dynamic_cb_group: CallbackGroup = ReentrantCallbackGroup(),
        dynamic_qos: QoSProfile = qos_profile_system_default,
    ) -> "DynamicsBus":

        dynamic_publisher = node.create_publisher(
            msg_type=dynamic_type,
            topic=dynamic_topic,
            callback_group=dynamic_cb_group,
            qos_profile=dynamic_qos,
        )

        return cls(
            _dynamic_name=dynamic_name,
            _dynamic_publisher=dynamic_publisher,
        )


class DynamicsHub:
    """Container for multiple DynamicsBus objects."""

    def __init__(
        self,
        node: Node,
        dynamics_registry: DynamicsRegistry,
        cb_group: CallbackGroup = ReentrantCallbackGroup(),
        qos: QoSProfile = qos_profile_system_default,
    ):

        self._busses: Dict[str, DynamicsBus] = {}

        dynamic_components = dynamics_registry.get_dynamics_by_names(
            dynamics_registry.get_dynamics_names()
        )
        for dynamic_name, dynamic_wrapper in dynamic_components.items():
            self._busses[dynamic_name] = DynamicsBus.create_dynamic_bus(
                node=node,
                dynamic_name=dynamic_name,
                dynamic_topic=dynamic_wrapper.get_output_topic(),
                dynamic_type=dynamic_wrapper.get_output_msg_type(),
                dynamic_qos=qos,
                dynamic_cb_group=cb_group,
            )

    def get_bus(self, name: str) -> DynamicsBus:
        return self._busses[name]

    def publish(self, name: str, msg):
        self.get_bus(name).publish_dynamic(msg)

    def list_busses(self):
        return list(self._busses.keys())


def main():
    import rclpy
    from rclpy.node import Node
    from rclpy.executors import MultiThreadedExecutor
    import threading

    rclpy.init()

    node = Node("node")
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    dynamics_dict = {
        "pid_controller": {
            "module": "hybraut_common_behaviours.dynamics",
            "class_name": "PIDControllerDynamics",
            "configuration": {
                "control_frequency": 100,
                "max_velocity": 30.0,
                "derivative_filter_alpha": 0.1,
                "integral_max": 0.2,
                "target_velocity": 25.0,  # updated cruise speed
                "yaw_kp": 0.3,  # gentle heading proportional gain
                "yaw_ki": 0.01,  # small integral for smooth correction
                "yaw_kd": 0.05,  # small derivative gain to damp oscillations
                "vel_kp": 0.5,  # moderate velocity proportional gain
                "vel_ki": 0.05,  # small integral to avoid windup
                "vel_kd": 0.05,  # small derivative for smooth velocity changes
                "error_tolerance": 0.01,  # precision in heading error
                "max_yaw_rate": 0.1,  # limit yaw rate to gentle turns
            },
            "output": {
                "topic": "/cmd_vel",
                "type": {"pkg": "geometry_msgs.msg", "msg": "Twist"},
            },
        }
    }
    from hybraut_models.core.dynamics import DynamicsRegistry

    dynamics: DynamicsRegistry = DynamicsRegistry.load_dynamics_registry_from_amdl(
        dynamics_dict=dynamics_dict
    )

    from geometry_msgs.msg import Twist

    dynamics_hub = DynamicsHub(node=node, dynamics_registry=dynamics)
    dynamics_hub.publish("pid_controller", msg=Twist())

    rclpy.shutdown()


if __name__ == "__main__":
    main()
