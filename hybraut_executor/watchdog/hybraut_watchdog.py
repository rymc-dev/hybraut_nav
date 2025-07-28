from transitions import Machine
from rclpy.publisher import Publisher
from rclpy.impl.rcutils_logger import RcutilsLogger
from builtin_interfaces.msg import Time
import time
from .constants import StatusEnum
from .comm import StatusBus, EventBus

class HybrautWatchdogFSM:
    states = [status for status in StatusEnum]


    def __init__(self, node: Node):
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=StatusEnum.ACTIVE,
            after_state_change=self.publish_status
        )
        self.status_publisher = status_publisher
        self.logger = node.get_logger()

        status_bus: StatusBus = StatusBus()
        event_bus: EventBus = EventBus()

        # Normal operational flow
        self.machine.add_transition("transition_guard_enabled", StatusEnum.ACTIVE, StatusEnum.TRANSITIONING)
        self.machine.add_transition("transition_complete", StatusEnum.TRANSITIONING, StatusEnum.ACTIVE)
        self.machine.add_transition("mission_complete", StatusEnum.ACTIVE, StatusEnum.MISSION_COMPLETE) 

        # Error handling
        self.machine.add_transition("recoverable_error", StatusEnum.ACTIVE, StatusEnum.ERROR)
        self.machine.add_transition("transition_failure", StatusEnum.TRANSITIONING, StatusEnum.ERROR)
        self.machine.add_transition("attempt_fix", StatusEnum.ERROR, StatusEnum.RECOVERING)
        self.machine.add_transition("recovered", StatusEnum.RECOVERING, StatusEnum.ACTIVE)
        self.machine.add_transition("recovery_failed", "RECOVERING", StatusEnum.ERROR)
        self.machine.add_transition("critical_failure", StatusEnum.ERROR, StatusEnum.FATAL)
        self.machine.add_transition("shutdown", "FATAL", None)  # Terminal

    def publish_status(self):
        ros_enum = WatchdogFSM.state_name_map.get(self.state, HybridAutomatonStatus.FATAL)
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
from automaton_interfaces.msg import HybridAutomatonEvents

if __name__ == '__main__':
    rclpy.init()
    mock_node = Node('test_node')
    status_publisher = mock_node.create_publisher(
        HybridAutomatonStatus,
        '/hybrid_automaton/fsm/status',
        qos_profile=10
    )

    status_fsm = WatchdogFSM(
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