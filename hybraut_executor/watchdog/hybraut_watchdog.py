#!/usr/bin/python3
# -*- coding: utf-8  -*-
"""
Hybraut Watchdog Finite State Machine (FSM)
This module implements a finite state machine (FSM) for the Hybraut system,
which acts as a watchdog to monitor and manage the system's operational states.
It uses the `transitions` library to define states and transitions, and integrates
with ROS 2 for status publishing and event handling.
It includes error handling and recovery mechanisms to ensure the system can
recover from various operational anomalies.
It is designed to be used within a ROS 2 node, allowing for real-time monitoring
and control of the Hybraut system's state.
It is intended to be run as part of a ROS 2 application, where it can respond
to events and publish status updates to a topic.
"""

# Standard library imports
import time

# Third-party imports
from transitions import Machine

# ROS 2 imports
import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup
from builtin_interfaces.msg import Time

# Message imports
from hybraut_interfaces.msg import AutomatonEvents, AutomatonStatus

# Local imports
from .constants import StatusEnum, EventEnum
from .comm import StatusBus, EventBus


class HybrautWatchdogFSM:
    """
    an implementation of a finate state machine (fsm) which
    acts as a watchdog for hybraut system.
    """

    states = [status for status in StatusEnum]

    transition_function_map = {
        EventEnum.VALID_MISSION_REQUEST: "transition_to_active",
        EventEnum.TRANSITION_GUARD_ENABLED: "transition_guard_enabled",
        EventEnum.TRANSITION_COMPLETE: "transition_complete",
        EventEnum.RECOVERABLE_ERROR: "recoverable_error",
        EventEnum.ATTEMPT_FIX: "attempt_fix",
        EventEnum.RECOVERED: "recovered",
        EventEnum.RECOVERY_FAILED: "recovery_failed",
        EventEnum.CRITICAL_FAILURE: "critical_failure",
        EventEnum.MISSION_COMPLETE: "mission_complete",
        EventEnum.SHUTDOWN: "shutdown",
    }

    def status_callback():
        # TODO: placeholder for when status are recieved.
        ...

    def event_callback():
        # TODO: placehold for when events are received.
        ...

    def __init__(
        self,
        node: Node,
        cb_group: CallbackGroup = ReentrantCallbackGroup(),
        qos: QoSProfile = qos_profile_system_default,
    ):
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=StatusEnum.ACTIVE,
            after_state_change=self.publish_status,
        )
        self.node = node
        self.logger = node.get_logger()

        self.status_bus: StatusBus = StatusBus(
            node=node, status_callback=None, cb_group=cb_group, qos=qos
        )
        self.event_bus: EventBus = EventBus(
            node=node, event_callback=None, cb_group=cb_group, qos=qos
        )

        # Normal operational flow
        self.machine.add_transition(
            "transition_guard_enabled", StatusEnum.ACTIVE, StatusEnum.TRANSITIONING
        )
        self.machine.add_transition(
            "transition_complete", StatusEnum.TRANSITIONING, StatusEnum.ACTIVE
        )
        self.machine.add_transition(
            "mission_complete", StatusEnum.ACTIVE, StatusEnum.MISSION_COMPLETE
        )

        # Error handling
        self.machine.add_transition(
            "recoverable_error", StatusEnum.ACTIVE, StatusEnum.ERROR
        )
        self.machine.add_transition(
            "transition_failure", StatusEnum.TRANSITIONING, StatusEnum.ERROR
        )
        self.machine.add_transition(
            "attempt_fix", StatusEnum.ERROR, StatusEnum.RECOVERING
        )
        self.machine.add_transition(
            "recovered", StatusEnum.RECOVERING, StatusEnum.ACTIVE
        )
        self.machine.add_transition("recovery_failed", "RECOVERING", StatusEnum.ERROR)
        self.machine.add_transition(
            "critical_failure", StatusEnum.ERROR, StatusEnum.FATAL
        )
        self.machine.add_transition("shutdown", "FATAL", None)  # Terminal

    def publish_status(self):
        self.logger.info(f"Publishing status: {self.state}")
        # TODO: Implement status publishing logic

    def perform_event_driven_transition(self, event_msg: AutomatonEvents):
        event_type = event_msg.type
        trigger_name = self.event_triggers.get(event_type, None)

        if trigger_name is None:
            self.logger.error(f"Unknown event type: {event_type}")
            return

        self.logger.info(
            f"Event received: {event_type}, invoking trigger: {trigger_name}"
        )

        try:
            getattr(self, trigger_name)()
        except Exception as e:
            self.logger.error(
                f"Transition failed on '{trigger_name}' from '{self.state}': {e}"
            )


if __name__ == "__main__":
    rclpy.init()
    mock_node = Node("test_node")
    status_publisher = mock_node.create_publisher(
        AutomatonStatus, "/automaton/status", qos_profile=10
    )

    status_fsm = HybrautWatchdogFSM(node=mock_node)

    # Simulate transitions
    def trigger(event_type):
        status_fsm.perform_event_driven_transition(
            AutomatonEvents(type=event_type, message="")
        )
        time.sleep(0.1)

    # Example event triggers using EventEnum values
    from .constants import EventEnum

    trigger(EventEnum.TRANSITION_GUARD_ENABLED.value)
    trigger(EventEnum.TRANSITION_COMPLETE.value)
    trigger(EventEnum.RECOVERABLE_ERROR.value)
    trigger(EventEnum.ATTEMPT_FIX.value)
    trigger(EventEnum.RECOVERED.value)
    trigger(EventEnum.MISSION_COMPLETE.value)

    rclpy.shutdown()
