# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the State class for managing ROS2 state topics,
including lifecycle management, message handling, and error tracking.
It also provides a StateRegistry for managing multiple states.
"""


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from hybraut_models.component_interfaces.registry_interface import ComponentRegistry


class State:
    """
    Represents a state in the system, managing a specific topic and message type.
    This class handles the lifecycle of the state.
    """

    def __init__(
        self,
        name: str,
        topic: str,
        msg_type: Type,
        update_hz: Optional[int] = None,
        timeout_sec: Optional[float] = None,
        max_errors: int = 10,
    ):
        self._name = name
        self._topic = topic
        self._msg_type = msg_type
        self._update_hz = update_hz
        self._timeout_sec = timeout_sec
        self._max_errors = max_errors

        self._current_state = None
        self._error_count = 0
        self._last_update = None

    """ === util functions === """

    def update_state(self, current_state: Any):
        """
        Internal callback for processing received state messages.

        This method updates the internal state and timestamp when new
        messages are received from the subscription.

        Args:
            node (Node): ROS2 node (for clock access)
            state_msg (Any): Received ROS2 message
        """
        try:
            # Update state data
            self._current_state = current_state

            # Reset error count on successful reception
            self.reset_error_count()
        except Exception as e:
            self.increment_error_count()
            raise e

    def get_current_state(self) -> Any:
        """Get the current state message (read-only property)."""
        return self._current_state

    def reset_error_count(self) -> None:
        """Reset the error counter to zero."""
        self._error_count = 0

    def increment_error_count(self) -> None:
        """Increment the error counter and log warnings if threshold exceeded."""
        self._error_count += 1

        if self._error_count >= self._max_errors:
            raise Exception(
                f"State '{self._name}' has exceeded maximum error count ({self._max_errors})"
            )
        
    """ === state information in dict format ==="""

    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current state.

        Returns:
            Dict[str, Any]: Dictionary containing all relevant state information
        """
        return {
            "name": self._name,
            "topic": self._topic,
            "message_type": getattr(self._msg_type, "__name__", str(self._msg_type)),
            "update_hz": self._update_hz,
            "timeout_sec": self._timeout_sec,
            "error_count": self._error_count,
            "max_errors": self._max_errors,
            "last_update": str(self._last_update) if self._last_update else None,
            "has_current_state": self._current_state is not None,
            "current_state_summary": (
                str(self._current_state)[:100] if self._current_state else None
            ),
        }

    """ === string representations === """

    def __str__(self) -> str:
        """Return a concise, human-readable representation of the state."""
        return (
            f"State '{self._name}' on topic '{self._topic}', "
            f"message type: {getattr(self._msg_type, '__name__', str(self._msg_type))}, "
            f"errors: {self._error_count}/{self._max_errors}"
        )

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        current_state_repr = (
            repr(self._current_state) if self._current_state is not None else "None"
        )
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"topic={self._topic!r}, "
            f"msg_type={getattr(self._msg_type, '__name__', repr(self._msg_type))}, "
            f"update_hz={self._update_hz}, "
            f"timeout_sec={self._timeout_sec}, "
            f"error_count={self._error_count}, "
            f"max_errors={self._max_errors}, "
            f"current_state={current_state_repr})"
        )



@dataclass
class StateRegistry(ComponentRegistry["State"]):
    """Registry specialized for managing State components."""

    def __post_init__(self):
        self._component_type_name = "State"
        super().__post_init__()

    def get_num_states(self):
        return len(self._components)

    def get_current_states(self, state_names: List[str]) -> Dict[str, Any]:
        components = self.get_components_by_names(state_names)
        current_states = {}
        for component_name, component_val in components.items():
            current_states[component_name] = component_val.current_state

        return current_states

    @classmethod
    def _component_class(cls) -> Type[State]:
        return State


"""main function for testing the State and StateRegistry classes. not for production use."""


def main():
    states = {
        "pose_state": {
            "topic": "/state/pose",
            "description": "Pose of the agent including position and orientation.",
            "type": {"pkg": "geometry_msgs.msg", "msg": "Pose"},
            "params": {"update_hz": 10.0, "timeout_sec": 0.5},
        },
        "twist_state": {
            "topic": "/state/twist",
            "description": "Twist of the agent including linear and angular velocity.",
            "type": {"pkg": "geometry_msgs.msg", "msg": "Twist"},
            "params": {"update_hz": 10.0, "timeout_sec": 0.5},
        },
    }

    import rclpy
    from rclpy.node import Node
    import threading
    from rclpy.executors import MultiThreadedExecutor

    rclpy.init()

    node = Node("test_node")
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    try:
        _state_registry: StateRegistry = StateRegistry.load_state_registry_from_amdl(
            states_dict=states
        )

        import time

        time.sleep(2.0)

        state_names = _state_registry.get_component_names()
        current_states = _state_registry.get_current_states(state_names)

        print(f"Registry __str__ representation: {_state_registry}\n")
        print(f"Registry __repr__ representation: {repr(_state_registry)}")
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        rclpy.shutdown()
        thread.join()

if __name__ == "__main__":
    main()
