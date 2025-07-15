from transitions import Machine
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus, HybridAutomatonEvents
from rclpy.publisher import Publisher
from rclpy.impl.rcutils_logger import RcutilsLogger
from builtin_interfaces.msg import Time
import time

class StatusFSM:
    state_name_map = {
        "ACTIVE": HybridAutomatonStatus.ACTIVE,
        "TRANSITIONING": HybridAutomatonStatus.TRANSITIONING,
        "WARNING": HybridAutomatonStatus.WARNING,
        "ERROR": HybridAutomatonStatus.ERROR,
        "RECOVERING": HybridAutomatonStatus.RECOVERING,
        "FATAL": HybridAutomatonStatus.FATAL,
        "MISSION_COMPLETE": HybridAutomatonStatus.MISSION_COMPLETE,
    }
    states = list(state_name_map.keys())

    event_triggers = {
        HybridAutomatonEvents.TRANSITION_GUARD_ENABLED: "transition_guard_enabled",
        HybridAutomatonEvents.TRANSITION_FAILURE: "transition_failure",
        HybridAutomatonEvents.TRANSITION_COMPLETE: "transition_complete",
        HybridAutomatonEvents.NON_BLOCKING_ANOMALY: "non_blocking_anomoly",
        HybridAutomatonEvents.ANOMALY_RESOLVED_OR_TIMEOUT: "anomoly_resolved_or_timeout",
        HybridAutomatonEvents.RECOVERABLE_ERROR: "recoverable_error",
        HybridAutomatonEvents.ATTEMPT_FIX: "attempt_fix",
        HybridAutomatonEvents.RECOVERED: "recovered",
        HybridAutomatonEvents.CRITICAL_FAILURE: "critical_failure",
        HybridAutomatonEvents.MISSION_COMPLETE: "mission_complete",
        HybridAutomatonEvents.RECOVERY_FAILED: "recovery_failed",
        HybridAutomatonEvents.SHUTDOWN: "shutdown"
    }

    def __init__(self, status_publisher: Publisher, logger: RcutilsLogger):
        self.machine = Machine(
            model=self,
            states=StatusFSM.states,
            initial="ACTIVE",
            after_state_change=self.publish_status
        )
        self.status_publisher = status_publisher
        self.logger = logger

        # Normal operational flow
        self.machine.add_transition("transition_guard_enabled", "ACTIVE", "TRANSITIONING")
        self.machine.add_transition("transition_complete", "TRANSITIONING", "ACTIVE")
        self.machine.add_transition("mission_complete", "ACTIVE", "MISSION_COMPLETE") 

        # Error handling
        self.machine.add_transition("recoverable_error", "ACTIVE", "ERROR")
        self.machine.add_transition("transition_failure", "TRANSITIONING", "ERROR")
        self.machine.add_transition("attempt_fix", "ERROR", "RECOVERING")
        self.machine.add_transition("recovered", "RECOVERING", "ACTIVE")
        self.machine.add_transition("recovery_failed", "RECOVERING", "ERROR")
        self.machine.add_transition("critical_failure", "ERROR", "FATAL")
        self.machine.add_transition("shutdown", "FATAL", None)  # Terminal

        # Warning branch
        self.machine.add_transition("non_blocking_anomoly", "ACTIVE", "WARNING")
        self.machine.add_transition("anomoly_resolved_or_timeout", "WARNING", "ACTIVE")

    def publish_status(self):
        ros_enum = StatusFSM.state_name_map.get(self.state, HybridAutomatonStatus.FATAL)
        self.logger.info(f"Publishing status: {self.state} ({ros_enum})")
        self.status_publisher.publish(HybridAutomatonStatus(
            type=ros_enum,
            message=f"Transitioned to {self.state}",
            stamp=Time()
        ))

    def perform_event_driven_transition(self, event_msg: HybridAutomatonEvents):
        event_type = event_msg.type
        trigger_name = self.event_triggers.get(event_type, None)

        if trigger_name is None:
            self.logger.error(f"Unknown event type: {event_type}")
            return

        self.logger.info(f"Event received: {event_type}, invoking trigger: {trigger_name}")

        try:
            getattr(self, trigger_name)()
        except Exception as e:
            self.logger.error(f"Transition failed on '{trigger_name}' from '{self.state}': {e}")

import rclpy
from rclpy.node import Node
from hybrid_automaton_interfaces.msg import HybridAutomatonEvents

if __name__ == '__main__':
    rclpy.init()
    mock_node = Node('test_node')
    status_publisher = mock_node.create_publisher(
        HybridAutomatonStatus,
        '/hybrid_automaton/fsm/status',
        qos_profile=10
    )

    status_fsm = StatusFSM(
        status_publisher=status_publisher,
        logger=mock_node.get_logger()
    )

    # Simulate transitions
    def trigger(event_type):
        status_fsm.perform_event_driven_transition(
            HybridAutomatonEvents(type=event_type, message="")
        )
        time.sleep(0.1)

    trigger(HybridAutomatonEvents.TRANSITION_GUARD_ENABLED)
    trigger(HybridAutomatonEvents.TRANSITION_COMPLETE)
    trigger(HybridAutomatonEvents.NON_BLOCKING_ANOMALY)
    trigger(HybridAutomatonEvents.ANOMALY_RESOLVED_OR_TIMEOUT)
    trigger(HybridAutomatonEvents.RECOVERABLE_ERROR)
    trigger(HybridAutomatonEvents.ATTEMPT_FIX)
    trigger(HybridAutomatonEvents.RECOVERED)
    trigger(HybridAutomatonEvents.MISSION_COMPLETE)

    rclpy.shutdown()