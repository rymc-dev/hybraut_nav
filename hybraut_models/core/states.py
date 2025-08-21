# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the State class for managing ROS2 state topics,
including lifecycle management, message handling, and error tracking.
It also provides a StateRegistry for managing multiple states.
"""


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from hybraut_models.core.component_interfaces.registry_interface import (
    ComponentRegistry,
)


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

    """ === access modifiers === """

    def get_name(self) -> str:
        return self._name

    def get_topic(self) -> str:
        return self._topic

    def get_msg_type(self) -> Type:
        return self._msg_type

    def get_update_hz(self) -> int:
        return self._update_hz

    def get_timeout_sec(self) -> float:
        return self._timeout_sec

    def get_max_errors(self) -> int:
        return self._max_errors

    def get_current_state(self) -> Any:
        """Get the current state message (read-only property)."""
        return self._current_state

    def get_error_count(self) -> int:
        return self._error_count

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
            if not isinstance(current_state, self._msg_type):
                raise TypeError(
                    f"Expected message type {self._msg_type}, "
                    f"but got {type(self._current_state)}"
                )

            # Update state data
            self._current_state = current_state

            # Reset error count on successful reception
            self.reset_error_count()
        except Exception as e:
            self.increment_error_count()
            raise e

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

    def get_state_names(self):
        return self.get_component_names()

    def get_states_by_name(self, state_names: List[str]) -> Dict[str, State]:
        return self.get_components_by_names(state_names)

    def update_state(self, state_name: str, current_state: Any) -> None:

        if not isinstance(current_state, self._components[state_name].get_msg_type()):
            raise TypeError(f"invalid current state type for state '{state_name}'")

        self._components[state_name].update_state(current_state)

    def update_states(self, state_name_and_current_state: Dict[str, Any]) -> None:
        """
        Update multiple states with their current state messages.

        Args:
            state_names (List[str]): List of state names to update.
            current_states (Dict[str, Any]): Dictionary of current states keyed by state names.
        """
        for state_name, current_state in state_name_and_current_state.items():
            if state_name in self._components:
                self.update_state(state_name, current_state)

    def get_current_state_by_state_name(self, state_name: str) -> Any:
        if state_name in self._components:
            return self._components[state_name].get_current_state()
        return None

    def get_current_states_by_state_names(
        self, state_names: List[str]
    ) -> Dict[str, Any]:
        components = self.get_components_by_names(state_names)
        current_states = {}
        for component_name, component_val in components.items():
            current_states[component_name] = component_val._current_state

        return current_states

    @classmethod
    def _component_class(cls) -> Type[State]:
        return State

    """ === string representations === """

    def __str__(self) -> str:
        """Return a concise, human-readable representation of the registry."""
        state_names = self.get_state_names()
        return (
            f"StateRegistry with {len(state_names)} states: "
            f"{', '.join(state_names) if state_names else 'No states registered'}"
        )

    def __repr__(self) -> str:
        """Return a detailed representation for debugging."""
        state_names = self.get_state_names()
        return (
            f"{self.__class__.__name__}("
            f"num_states={len(state_names)}, "
            f"state_names={state_names})"
        )


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
