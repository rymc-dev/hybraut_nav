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
    An implementation of a finite state machine (FSM) which
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
        """Handle incoming status messages."""
        self.node.get_logger().info(f"Status received: {msg}")

    def __init__(
        self,
        node: Node,
        cb_group: CallbackGroup = None,
        qos: QoSProfile = None,
        initial_state: StatusEnum = StatusEnum.ACTIVE,
    ):
        """ 
        Initializes the FSM with the given ROS 2 node context,
        once FSM structure is defined, we set up the I/O buses for the 
        fsm transitions and status updates.
        """
        # Set defaults
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if qos is None:
            qos = qos_profile_system_default
            
        # Initialize the state machine
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=initial_state,
            after_state_change=self.publish_status,
            ignore_invalid_triggers=True,  # Prevents crashes on invalid transitions
        )
        
        # Add all transitions with proper state references
        self._add_transitions()
        
        # Initialize ROS components
        self.__post_init__(node=node, cb_group=cb_group, qos=qos)

    def _add_transitions(self):
        """Add all FSM transitions with proper error handling."""
        try:
            # Normal operational flow
            self.machine.add_transition(
                self.transition_function_map[EventEnum.TRANSITION_GUARD_ENABLED], StatusEnum.ACTIVE, StatusEnum.TRANSITIONING
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.TRANSITION_COMPLETE], StatusEnum.TRANSITIONING, StatusEnum.ACTIVE
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.MISSION_COMPLETE], StatusEnum.ACTIVE, StatusEnum.MISSION_COMPLETE
            )

            # Error handling transitions
            self.machine.add_transition(
                self.transition_function_map[EventEnum.RECOVERABLE_ERROR], StatusEnum.ACTIVE, StatusEnum.ERROR
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.RECOVERABLE_ERROR], StatusEnum.TRANSITIONING, StatusEnum.ERROR
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.ATTEMPT_FIX], StatusEnum.ERROR, StatusEnum.RECOVERING
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.RECOVERED], StatusEnum.RECOVERING, StatusEnum.ACTIVE
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.RECOVERY_FAILED], StatusEnum.RECOVERING, StatusEnum.ERROR
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.CRITICAL_FAILURE], StatusEnum.ERROR, StatusEnum.FATAL
            )
            self.machine.add_transition(
                self.transition_function_map[EventEnum.CRITICAL_FAILURE], StatusEnum.RECOVERING, StatusEnum.FATAL
            )
            
            # Shutdown transitions (from any state except FATAL)
            for state in StatusEnum:
                if state != StatusEnum.FATAL:
                    self.machine.add_transition("shutdown", state, StatusEnum.FATAL)
                    
        except Exception as e:
            print(f"Error adding transitions: {e}")
            raise

    def __post_init__(
        self,
        node: Node,
        cb_group: CallbackGroup = None,
        qos: QoSProfile = None
    ):
        """ 
        Post FSM definition initialization.
        This method sets up the I/O buses for the FSM transitions and status updates.
        """
        if cb_group is None:
            cb_group = ReentrantCallbackGroup()
        if qos is None:
            qos = qos_profile_system_default
            
        self.node = node
        self.cb_group = cb_group
        self.qos = qos

        try:
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
        except Exception as e:
            self.node.get_logger().error(f"Failed to initialize buses: {e}")
            raise

    def publish_status(self):
        """ 
        Publishes the current state of the FSM to the status bus.
        """
        try:
            self.status_bus.publish(
                data=self.state, 
                message=f"State changed to {self.state}",
            )
            self.node.get_logger().info(f"Published status: {self.state}")
        except Exception as e:
            self.node.get_logger().error(f"Failed to publish status: {e}")

    def trigger_transition(self, event: AutomatonEvents):
        """
        Triggers a watchdog fsm transition utilizing an AutomatonEvents msg published
        via ros2 topic `/automaton/events`
        """
        try:
            if not isinstance(event, AutomatonEvents):
                raise TypeError(
                    f"HybrautWatchdog::trigger_transition: event received invalid type: got: {type(event)}, "
                    "expected AutomatonEvents"
                )

            # Create mapping from event type value to EventEnum
            enum_dict = {enum.value: enum for enum in EventEnum}

            if event.type not in enum_dict:
                self.node.get_logger().warn(
                    f"HybrautWatchdog::trigger_transition: event type received: `{event.type}` "
                    "invalid, not within event options for watchdog fsm"
                )
                return

            event_enum = enum_dict.get(event.type)
            self.node.get_logger().info(f"Processing event: {event_enum} with message: {event.message}")
            
            self.perform_event_driven_transition(event_enum)
            
        except Exception as e:
            self.node.get_logger().error(f"HybrautWatchdog::trigger_transition: {str(e)}")
            self.handle_transition_failure(e)

    def perform_event_driven_transition(self, event: EventEnum):
        """
        Performs a transition based on the enum value for event msg
        """
        if not isinstance(event, EventEnum):
            raise ValueError(
                f"HybrautWatchdog::perform_event_driven_transition: invalid event type, "
                f"got: `{type(event)}`, expected: `EventEnum`"
            )

        transition_func_name = self.transition_function_map.get(event)

        if transition_func_name is None:
            raise ValueError(
                f"HybrautWatchdog::perform_event_driven_transition: event {event} not mapped to transition function"
            )

        try:
            if hasattr(self, transition_func_name):
                transition_func = getattr(self, transition_func_name)
                transition_func()
                self.node.get_logger().info(f"Successfully executed transition: {transition_func_name}")
            else:
                raise AttributeError(f"Method {transition_func_name} not found")
                
        except Exception as e:
            self.node.get_logger().error(f"Transition failed: {e}")
            self.handle_transition_failure(e)

    def handle_transition_failure(self, error: Exception):
        """Handle failures during state transitions."""
        self.node.get_logger().error(f"Transition failure: {error}")
        
        # If we're not already in an error state, try to transition to error
        if self.state not in [StatusEnum.ERROR, StatusEnum.FATAL, StatusEnum.RECOVERING]:
            try:
                self.recoverable_error()
            except Exception as recovery_error:
                self.node.get_logger().fatal(f"Failed to enter error state: {recovery_error}")
                # Last resort - try critical failure
                try:
                    self.critical_failure()
                except Exception:
                    self.node.get_logger().fatal("System in unrecoverable state")

    # Transition methods with improved error handling and logging
    def transition_to_active(self):
        """Transition to active state on valid mission request."""
        self.node.get_logger().info("FSM: Transitioning to ACTIVE state")
        # Add any additional logic needed for activation

    def transition_guard_enabled(self):
        """Handle transition guard enabled event."""
        current_state = self.state
        self.node.get_logger().info(f"FSM: Transition guard enabled from state {current_state}")
        
        if current_state == StatusEnum.ACTIVE:
            # This will trigger the machine transition to TRANSITIONING
            pass
        else:
            self.node.get_logger().warn(f"Cannot enable transition guard from state {current_state}")

    def transition_complete(self):
        """Handle transition complete event."""
        current_state = self.state
        self.node.get_logger().info(f"FSM: Transition complete from state {current_state}")
        
        if current_state == StatusEnum.TRANSITIONING:
            # This will trigger the machine transition back to ACTIVE
            pass
        else:
            self.node.get_logger().warning(f"Cannot complete transition from state {current_state}")

    def recoverable_error(self):
        """Handle recoverable error event."""
        current_state = self.state
        self.node.get_logger().warning(f"FSM: Recoverable error occurred in state {current_state}")
        
        if current_state in [StatusEnum.ACTIVE, StatusEnum.TRANSITIONING]:
            # This will trigger the machine transition to ERROR
            pass
        else:
            self.node.get_logger().warning(f"Cannot handle recoverable error from state {current_state}")

    def attempt_fix(self):
        """Handle attempt fix event."""
        current_state = self.state
        self.node.get_logger().info(f"FSM: Attempting to fix error from state {current_state}")
        
        if current_state == StatusEnum.ERROR:
            # This will trigger the machine transition to RECOVERING
            pass
        else:
            self.node.get_logger().warning(f"Cannot attempt fix from state {current_state}")

    def recovered(self):
        """Handle recovered event."""
        current_state = self.state
        self.node.get_logger().info(f"FSM: Recovered from error, was in state {current_state}")
        
        if current_state == StatusEnum.RECOVERING:
            # This will trigger the machine transition back to ACTIVE
            pass
        else:
            self.node.get_logger().warning(f"Cannot recover from state {current_state}")

    def recovery_failed(self):
        """Handle recovery failed event."""
        current_state = self.state
        self.node.get_logger().error(f"FSM: Recovery failed from state {current_state}")
        
        if current_state == StatusEnum.RECOVERING:
            # This will trigger the machine transition back to ERROR
            pass
        else:
            self.node.get_logger().warn(f"Cannot fail recovery from state {current_state}")

    def critical_failure(self):
        """Handle critical failure event."""
        current_state = self.state
        self.node.get_logger().fatal(f"FSM: Critical failure occurred in state {current_state}")
        
        if current_state in [StatusEnum.ERROR, StatusEnum.RECOVERING]:
            # This will trigger the machine transition to FATAL
            pass
        else:
            self.node.get_logger().warning(f"Cannot handle critical failure from state {current_state}")

    def mission_complete(self):
        """Handle mission complete event."""
        current_state = self.state
        self.node.get_logger().info(f"FSM: Mission completed successfully from state {current_state}")
        
        if current_state == StatusEnum.ACTIVE:
            # This will trigger the machine transition to MISSION_COMPLETE
            pass
        else:
            self.node.get_logger().warn(f"Cannot complete mission from state {current_state}")

    def shutdown(self):
        """Handle shutdown event."""
        current_state = self.state
        self.node.get_logger().info(f"FSM: System shutdown initiated from state {current_state}")
        # This will trigger the machine transition to FATAL (terminal state)

    def get_current_state(self) -> StatusEnum:
        """Get the current state of the FSM."""
        return self.state

    def get_valid_transitions(self) -> list:
        """Get list of valid transitions from current state."""
        return self.machine.get_triggers(self.state)

    def is_terminal_state(self) -> bool:
        """Check if current state is terminal (FATAL)."""
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