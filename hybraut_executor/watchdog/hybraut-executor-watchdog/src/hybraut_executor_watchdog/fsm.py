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
from hybraut_executor_watchdog.hybraut_consts import StatusEnum, EventEnum
from hybraut_executor_watchdog.hybraut_bus import StatusBus, EventBus


class FSM:
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

    def status_callback(self, msg: any) -> None:
        # TODO: placeholder for when status are recieved.
        print (f"status received: {msg}")

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
            node=node,
            event_callback=self.trigger_transition,
            cb_group=cb_group,
            qos=qos,
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
        """ 
        publishes the current state of the FSM to the status bus.
        """
        self.status_bus.publish(
            data=self.state, 
            message=f"State changed to {self.state}",
        )

    def perform_event_driven_transition(self, event: EventEnum):
        """
        performs a transition based on the enum value for event msg
        """
        if not isinstance(event, EventEnum):
            raise ValueError(
                f"HybrautWathdog::perform_event_driven_transition: invalid envent type, "
                f"got: `{type(event)}`, expected: `wathdog.constants.EventEnum`"
            )

        transition_func_name = self.transition_function_map.get(event)

        if transition_func_name is None:
            raise ValueError(
                f"HybrautWatchdog::perform_event_driven_transition: event not mapped to transition function"
            )

        try:
            transition_func = self.__getattribute__(transition_func_name)
            transition_func()
        except Exception as e:
            self.handle_transition_failure(e)

    def handle_transition_failure(self, error: Exception): 
        self.logger.error(
            f"HybrautWatchdog::handle_transition_failure: Transition failed with error: {error}"
        )
        self.event_bus.publish(
            data=AutomatonEvents.RECOVERABLE_ERROR,
            message=str(error)
        )


    def trigger_transition(self, event: AutomatonEvents):
        """triggers a watchdog fsm transition utilizing a AutomatonEvents msg published
        via ros2 topic `/automaton/events`

        Args:
            event (AutomatonEvents): ros2 interface from `hybraut_interfaces.msg` pkg

        Raises:
            TypeError: if event is invalid type
            Exception: if event driven transitions exception thrown
        """
        if not isinstance(event, AutomatonEvents):
            raise TypeError(
                f"HybrautWathdog::trigger_transition: event received invalid type: got: {type(event)}"
                "exepcted watchdog.contstants.event.EventEnum"
            )

        from typing import Dict

        enum_dict: Dict[int, EventEnum] = {enum.value: enum for enum in EventEnum}
        if not event.type in enum_dict.keys():
            raise AttributeError(
                f"HybrautWatchdog::trigger_transition: event type received: `{event.type}`"
                "invalid, not within event options for watchdog fsm"
            )
        try:
            self.perform_event_driven_transition(enum_dict.get(event.type))
            import time
            time.sleep(0.02)
        except Exception as e:
            raise Exception(f"HybrautWatchdog::trigger_transition: {str(e)}")



if __name__ == "__main__":
    rclpy.init()
    mock_node = Node("test_node")
    event_publisher = mock_node.create_publisher(
        AutomatonEvents, "/automaton/event", qos_profile=qos_profile_system_default
    )

    def status_callback(msg):
        mock_node.get_logger().info(f"new status received: {msg}")

    status_subscription = mock_node.create_subscription(
        msg_type=AutomatonStatus,
        topic="/automaton/status",
        qos_profile=qos_profile_system_default,
        callback_group=ReentrantCallbackGroup(),
        callback=lambda msg: status_callback(msg),
    )

    status_fsm = FSM(node=mock_node)
    status_fsm.trigger_transition(
        AutomatonEvents(
            type=AutomatonEvents.TRANSITION_GUARD_ENABLED,
            stamp=mock_node.get_clock().now().to_msg(),
        )
    )

    import time

    time.sleep(0.1)

    status_fsm.trigger_transition(
        AutomatonEvents(
            type=AutomatonEvents.TRANSITION_COMPLETE
        )
    )

    time.sleep(0.1)
    status_fsm.trigger_transition(
        AutomatonEvents(
            type=AutomatonEvents.MISSION_COMPLETE
        )
    )

    # status_fsm.trigger_transition(
    #     AutomatonEvents(
    #         type=AutomatonEvents.TRANSITION_COMPLETE,
    #         stamp=mock_node.get_clock().now().to_msg(),
    #     )
    # )

    rclpy.shutdown()
