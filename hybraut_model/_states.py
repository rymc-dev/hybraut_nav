# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines the State class for managing ROS2 state topics,
including lifecycle management, message handling, and error tracking.
It also provides a StateRegistry for managing multiple states.
"""


import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from rclpy.node import Node

from hybraut_model.automaton_types.msg_type import MsgType
from hybraut_model.component_interfaces.registry_interface import ComponentRegistry

# Set up module-level logger
logger = logging.getLogger(__name__)


class State:
    """
    Represents a state in the ROS2 system, managing a specific topic and message type.
    This class handles the lifecycle of the state, including activation, deactivation,
    and error management.
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
        # stash everything you need
        self._name = name
        self._topic = topic
        self._msg_type = msg_type
        self._update_hz = update_hz
        self._timeout_sec = timeout_sec
        self._max_errors = max_errors

        # build the bus
        self._current_state = None
        self._error_count = 0
        self._last_update = None
        # set up your logger
        self._logger = logging.getLogger(f"{__name__}.State.{self._name}")

    def __post_init__(self):
        """Initialize the logger after dataclass creation."""
        self._logger = logging.getLogger(f"{__name__}.State.{self._name}")

    def is_synced(self, expected_hz: float, timeout_sec: float) -> bool:
        """Check if the state has been updated recently enough."""
        if not self._is_active:
            raise RuntimeError("can't check is_synced if states are not active")

        return True
        # now = time.time()
        # time_since_update = now - self.timestamp
        # min_expected_interval = 1.0 / expected_hz
        # return time_since_update <= timeout_sec and time_since_update <= 2 * min_expected_interval

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
            self._logger.debug(
                f"Successfully processed message for state '{self._name}'"
            )
        except Exception as e:
            self.increment_error_count()
            self._logger.error(
                f"Error processing message for state '{self._name}': {e}"
            )

    def reset_error_count(self) -> None:
        """Reset the error counter to zero."""
        if self._error_count > 0:
            self._logger.debug(f"Resetting error count for state '{self._name}'")
        self._error_count = 0

    def increment_error_count(self) -> None:
        """Increment the error counter and log warnings if threshold exceeded."""
        self._error_count += 1
        self._logger.warning(
            f"Error count for state '{self._name}': {self._error_count}"
        )

        if self._error_count >= self._max_errors:
            self._logger.error(
                f"State '{self._name}' has exceeded maximum error count ({self._max_errors})"
            )

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"<State '{self._name}' on topic '{self._topic}'>"

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return (
            f"State(_name={self._name!r}, _topic={self._topic!r}, "
            f"_msg_type={self._msg_type!r}"
            f"_update_hz={self._update_hz}, _timeout_sec={self._timeout_sec}, "
            f"_error_count={self._error_count})"
        )

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

    @property
    def current_state(self) -> Any:
        """Get the current state message (read-only property)."""
        return self._current_state

    @property
    def is_active(self) -> bool:
        """Check if the state is currently active (read-only property)."""
        return self._is_active

    @classmethod
    def load_state_from_amdl(
        cls, state_name: str, state_dict: Dict[str, Any]
    ) -> "State":
        """
        Create a State instance from FAMD (Formal Automaton Model Description) configuration.

        This factory method enables creation of State objects from configuration
        dictionaries, typically loaded from YAML or JSON files.

        Args:
            name (str): Unique name for the state
            state_dict (Dict[str, Any]): Configuration dictionary containing:
                - topic (str): ROS2 topic name
                - type (dict): Message type specification with 'pkg' and 'msg'
                - params (dict): Optional parameters like 'update_hz', 'timeout_sec'

        Returns:
            State: Configured State instance

        Raises:
            KeyError: If required configuration keys are missing
            ImportError: If message type cannot be imported

        Example:
            >>> config = {
            ...     "topic": "/robot/pose",
            ...     "type": {"pkg": "geometry_msgs.msg", "msg": "Pose"},
            ...     "params": {"update_hz": 10.0, "timeout_sec": 0.5}
            ... }
            >>> state = State.load_state_from_famd("pose_state", config)
        """
        try:
            # Extract and validate message type
            msg_type_info = MsgType(**state_dict["type"])
            msg_type = msg_type_info.import_msg_type()

            # Extract optional parameters
            params = state_dict.get("params", {})
            update_hz = params.get("update_hz")
            timeout_sec = params.get("timeout_sec")
            max_errors = params.get("max_errors", 10)

            logger.info(f"Loading state '{state_name}' from FAMD configuration")

            return State(
                name=state_name,
                topic=state_dict["topic"],
                msg_type=msg_type,
                update_hz=update_hz,
                timeout_sec=timeout_sec,
                max_errors=None,
            )

        except KeyError as e:
            error_msg = (
                f"Missing required key in state configuration for '{state_name}': {e}"
            )
            logger.error(error_msg)
            raise KeyError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load state '{state_name}' from FAMD: {e}"
            logger.error(error_msg)
            raise


@dataclass
class StateRegistry(ComponentRegistry["State"]):
    """Registry specialized for managing State components."""

    def __post_init__(self):
        self._component_type_name = "State"
        super().__post_init__()

    def get_current_states(self, state_names: List[str]) -> Dict[str, Any]:
        components = self.get_components_by_names(state_names)
        current_states = {}
        for component_name, component_val in components.items():
            current_states[component_name] = component_val.current_state

        return current_states

    @classmethod
    def _component_class(cls) -> Type[State]:
        return State

    @classmethod
    def register(
        cls: Type["ComponentRegistry"], config_dict: Dict[str, Any]
    ) -> Dict[str, State]:
        """
        Create and return component instances from configuration dict.
        Subclasses must implement `_component_class()` returning their component class.
        """
        components = {}

        for name, conf in config_dict.items():
            try:
                component_cls = cls._component_class()
                component = component_cls.load_state_from_amdl(
                    state_name=name, state_dict=conf
                )
                components[name] = component
            except Exception as e:
                logging.getLogger(__name__).error(
                    f"Failed to load component '{name}': {e}"
                )
                raise
        return components

    @classmethod
    def load_state_registry_from_amdl(
        cls, states_dict: Dict[str, Any]
    ) -> "StateRegistry":
        logger.info("Loading StateRegistry from 'amdl' configuration")
        states = cls.register(config_dict=states_dict)
        registry = cls(_components=states)
        logger.info(f"Created StateRegistry with {len(states)} states")
        return registry


"""main function for testing the State and StateRegistry classes. not for production use."""


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

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

        logger.info(f"Registry status before activation: {_state_registry}")
        _state_registry.activate_components(node)

        import time

        time.sleep(2.0)

        state_names = _state_registry.get_component_names()
        current_states = _state_registry.get_current_states(state_names)

        logger.info(f"Registry status: {_state_registry.get_registry_status()}")

        _state_registry.deactivate_components(node)
        logger.info(f"Registry status after deactivation: {_state_registry}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        rclpy.shutdown()
        thread.join()


if __name__ == "__main__":
    main()
