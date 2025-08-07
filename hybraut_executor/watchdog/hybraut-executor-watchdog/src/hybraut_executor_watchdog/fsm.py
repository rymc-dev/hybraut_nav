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

QOS = QoSProfile(depth=10, reliability=qos_profile_system_default.reliability)


class FSM:
    """
    Finite State Machine for Hybraut watchdog.
    Separates trigger names from callbacks to avoid name collisions.
    """

    # Define all states
    states = [status for status in StatusEnum]

    # Map incoming EventEnum to trigger method names
    transition_function_map = {
        EventEnum.VALID_MISSION_REQUEST: "activate_mission",
        EventEnum.TRANSITION_GUARD_ENABLED: "enable_guard",
        EventEnum.TRANSITION_COMPLETE: "complete_transition",
        EventEnum.RECOVERABLE_ERROR: "handle_recoverable_error",
        EventEnum.ATTEMPT_FIX: "attempt_fix_process",
        EventEnum.RECOVERED: "complete_recovery",
        EventEnum.RECOVERY_FAILED: "fail_recovery",
        EventEnum.CRITICAL_FAILURE: "handle_critical_failure",
        EventEnum.MISSION_COMPLETE: "finish_mission",
        EventEnum.SHUTDOWN: "shutdown_system",
    }

    def __init__(
        self,
        node: Node,
        cb_group: CallbackGroup = None,
        qos: QoSProfile = None,
        initial_state: StatusEnum = StatusEnum.ACTIVE,
    ):
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if qos is None:
            qos = qos_profile_system_default

        # Initialize state machine, after hook will publish status
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=initial_state,
            after_state_change=lambda event: self.publish_status(event),
            ignore_invalid_triggers=True,
        )
        self._add_transitions()
        self.__post_init__(node=node, cb_group=cb_group, qos=qos)

    def _add_transitions(self):
        # Normal operational flow
        self.machine.add_transition(
            trigger="enable_guard",
            source=StatusEnum.ACTIVE,
            dest=StatusEnum.TRANSITIONING,
            after="on_guard_enabled"
        )
        self.machine.add_transition(
            trigger="complete_transition",
            source=StatusEnum.TRANSITIONING,
            dest=StatusEnum.ACTIVE,
            after="on_transition_complete"
        )
        self.machine.add_transition(
            trigger="finish_mission",
            source=StatusEnum.ACTIVE,
            dest=StatusEnum.MISSION_COMPLETE,
            after="on_mission_complete"
        )

        # Error handling
        self.machine.add_transition(
            trigger="handle_recoverable_error",
            source=[StatusEnum.ACTIVE, StatusEnum.TRANSITIONING],
            dest=StatusEnum.ERROR,
            after="on_recoverable_error"
        )
        self.machine.add_transition(
            trigger="attempt_fix_process",
            source=StatusEnum.ERROR,
            dest=StatusEnum.RECOVERING,
            after="on_attempt_fix"
        )
        self.machine.add_transition(
            trigger="complete_recovery",
            source=StatusEnum.RECOVERING,
            dest=StatusEnum.ACTIVE,
            after="on_recovered"
        )
        self.machine.add_transition(
            trigger="fail_recovery",
            source=StatusEnum.RECOVERING,
            dest=StatusEnum.ERROR,
            after="on_recovery_failed"
        )
        self.machine.add_transition(
            trigger="handle_critical_failure",
            source=[StatusEnum.ERROR, StatusEnum.RECOVERING],
            dest=StatusEnum.FATAL,
            after="on_critical_failure"
        )

        # Shutdown from any non-fatal state
        for state in StatusEnum:
            if state != StatusEnum.FATAL:
                self.machine.add_transition(
                    trigger="shutdown_system",
                    source=state,
                    dest=StatusEnum.FATAL,
                    after="on_shutdown"
                )

    def __post_init__(
        self,
        node: Node,
        cb_group: CallbackGroup = None,
        qos: QoSProfile = None
    ):
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if qos is None:
            qos = qos_profile_system_default

        self.node = node
        self.cb_group = cb_group
        self.qos = qos

        self.status_bus: StatusBus = StatusBus(
            node=self.node,
            status_callback=self.status_callback,
            cb_group=self.cb_group,
            qos=self.qos
        )
        self.event_bus: EventBus = EventBus(
            node=node,
            event_callback=self.trigger_transition,
            cb_group=cb_group,
            qos=qos,
        )

    def status_callback(self, msg: any) -> None:
        self.node.get_logger().info(f"Status received: {msg}")

    def publish_status(self, event: any):
        try:
            self.status_bus.publish(
                data=self.get_current_state(),
                message=f"State changed to {self.get_current_state()}",
            )
            self.node.get_logger().info(f"Published status: {self.get_current_state()}")
        except Exception as e:
            self.node.get_logger().error(f"Failed to publish status: {e}")

    def trigger_transition(self, event: AutomatonEvents):
        if not isinstance(event, AutomatonEvents):
            self.node.get_logger().error(f"Invalid event type: {type(event)}")
            return
        enum_dict = {enum.value: enum for enum in EventEnum}
        if event.type not in enum_dict:
            self.node.get_logger().warn(f"Unknown event: {event.type}")
            return
        event_enum = enum_dict[event.type]
        self.node.get_logger().info(f"Processing event: {event_enum}")
        self.perform_event_driven_transition(event_enum)

    def perform_event_driven_transition(self, event: EventEnum):
        trigger = self.transition_function_map.get(event)
        if not trigger:
            raise ValueError(f"No trigger mapped for event {event}")
        if not hasattr(self, trigger):
            raise AttributeError(f"Trigger method {trigger} not found")
        getattr(self, trigger)(event)
        self.node.get_logger().info(f"Fired trigger: {trigger}")

    # Callback handlers (after transitions)
    def on_guard_enabled(self, event):
        self.node.get_logger().info(
            # f"Guard enabled: {event.transition.source} → {event.transition.dest}"
            f"Guard enabled, transitioning: {event}"
        )

    def on_transition_complete(self, event):
        self.node.get_logger().info(
            f"Guard enabled, transitioning: {event}"
        )

    def on_mission_complete(self, event):
        self.node.get_logger().info("Mission completed successfully")

    def on_recoverable_error(self, event):
        self.node.get_logger().warning("Entered ERROR state")

    def on_attempt_fix(self, event):
        self.node.get_logger().info("Attempting to recover from error")

    def on_recovered(self, event):
        self.node.get_logger().info("Recovery successful, back to ACTIVE")

    def on_recovery_failed(self, event):
        self.node.get_logger().error("Recovery attempt failed, back in ERROR")

    def on_critical_failure(self, event):
        self.node.get_logger().fatal("Critical failure: entering FATAL state")

    def on_shutdown(self, event):
        self.node.get_logger().info("Shutdown initiated: entering FATAL state")

    # Utilities
    def get_current_state(self) -> StatusEnum:
        return self.state

    def get_valid_transitions(self) -> list:
        return self.machine.get_triggers(self.state)

    def is_terminal_state(self) -> bool:
        return self.state == StatusEnum.FATAL

def main():
    """
    Main function to demonstrate the usage of the FSM.
    """
    import os
    import threading
    import time
    from rclpy.executors import MultiThreadedExecutor, Executor
    from rclpy.callback_groups import ReentrantCallbackGroup
    
    rclpy.init()
    
    try:
        executor: Executor = MultiThreadedExecutor(num_threads=os.cpu_count())
        node = Node("hybraut_watchdog_demo")
        executor.add_node(node)
        
        # Start executor in background thread
        thread = threading.Thread(target=executor.spin, daemon=True)
        thread.start()
        
        # Create FSM instance
        fsm = FSM(node=node, cb_group=ReentrantCallbackGroup(), qos=QOS)
        
        # Create event publisher for testing
        event_publisher = node.create_publisher(
            AutomatonEvents, "/automaton/events", 
            qos_profile=QOS, callback_group=ReentrantCallbackGroup()
        )
        
        # Wait for connections
        time.sleep(1.0)
        
        # Test sequence
        test_events = [
            (EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated"),
            (EventEnum.TRANSITION_COMPLETE, "transition completed"),
            (EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated"),
            (EventEnum.TRANSITION_COMPLETE, "transition completed"),
            (EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated"),
            (EventEnum.TRANSITION_COMPLETE, "transition completed"),
            (EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated"),
            (EventEnum.TRANSITION_COMPLETE, "transition completed"),
            (EventEnum.TRANSITION_GUARD_ENABLED, "mode guard activated"),
            (EventEnum.TRANSITION_COMPLETE, "transition completed"),
            # (EventEnum.RECOVERABLE_ERROR, "recoverable error occurred"),
            # (EventEnum.ATTEMPT_FIX, "attempting recovery"),
            # (EventEnum.RECOVERED, "system recovered"),
            (EventEnum.MISSION_COMPLETE, "mission has completed"),
        ]
        
        print(f"Starting FSM demo. Initial state: {fsm.get_current_state()}")
        
        for event_type, message in test_events:
            print(f"\nPublishing event: {event_type.name}")
            event_msg = AutomatonEvents(type=event_type.value, message=message)
            event_publisher.publish(event_msg)
            time.sleep(0.5)
            print(f"Current state: {fsm.get_current_state()}")
            print(f"Valid transitions: {fsm.get_valid_transitions()}")
        
        print(f"\nFinal state: {fsm.get_current_state()}")
        print(f"Is terminal state: {fsm.is_terminal_state()}")
        
        time.sleep(1.0)  # Give time for final message processing
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'executor' in locals():
            executor.shutdown()
        if 'thread' in locals():
            thread.join()
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()