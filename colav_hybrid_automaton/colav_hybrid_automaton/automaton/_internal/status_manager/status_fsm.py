from transitions import Machine
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus
from hybrid_automaton_interfaces.msg import HybridAutomatonEvents
from rclpy.publisher import Publisher
from rclpy.impl.rcutils_logger import RcutilsLogger
from builtin_interfaces.msg import Time
import time

class StatusFSM:
    state_name_map = {
        "STATUS_INIT": HybridAutomatonStatus.STATUS_INIT,
        "STATUS_IDLE": HybridAutomatonStatus.STATUS_IDLE,
        "STATUS_ACTIVE": HybridAutomatonStatus.STATUS_ACTIVE,
        "STATUS_TRANSITIONING": HybridAutomatonStatus.STATUS_TRANSITIONING,
        "STATUS_WARNING": HybridAutomatonStatus.STATUS_WARNING,
        "STATUS_ERROR": HybridAutomatonStatus.STATUS_ERROR,
        "STATUS_RECOVERING": HybridAutomatonStatus.STATUS_RECOVERING,
        "STATUS_FATAL": HybridAutomatonStatus.STATUS_FATAL,
        "STATUS_MISSION_COMPLETE": HybridAutomatonStatus.STATUS_MISSION_COMPLETE,
        "STATUS_TERMINATED": HybridAutomatonStatus.STATUS_TERMINATED,
    }
    states = list(state_name_map.keys())
    event_triggers = {
        HybridAutomatonEvents.EVENT_SYSTEM_BOOT: "system_boot",
        HybridAutomatonEvents.EVENT_BOOT_FAILURE: "boot_failure",
        HybridAutomatonEvents.EVENT_MISSION_RECEIVED: "mission_received",
        HybridAutomatonEvents.EVENT_INIT_MISSION_FAILURE: "init_mission_failure",
        HybridAutomatonEvents.EVENT_TRANSITION_GUARD_ENABLED: "transition_guard_enabled",
        HybridAutomatonEvents.EVENT_TRANSITION_FAILURE: "transition_failure",
        HybridAutomatonEvents.EVENT_TRANSITION_COMPLETE: "transition_complete",
        HybridAutomatonEvents.EVENT_NON_BLOCKING_ANOMALY: "non_blocking_anomoly",
        HybridAutomatonEvents.EVENT_ANOMALY_RESOLVED_OR_TIMEOUT: "anomoly_resolved_or_timeout",
        HybridAutomatonEvents.EVENT_RECOVERABLE_ERROR: "recoverable_error",
        HybridAutomatonEvents.EVENT_ATTEMPT_FIX: "attempt_fix",
        HybridAutomatonEvents.EVENT_RECOVERED: "recovered",
        HybridAutomatonEvents.EVENT_CRITICAL_FAILURE: "critical_failure",
        HybridAutomatonEvents.EVENT_MISSION_COMPLETE: "mission_complete"
    }   

    def __init__(
            self,
            status_publisher: Publisher,
            logger: RcutilsLogger
    ):
        self.machine = Machine(
            model=self, 
            states=StatusFSM.states, 
            initial="STATUS_INIT",
            after_state_change=self.publish_status
        )
        self.status_publisher = status_publisher
        self.logger = logger

        # Boot sequence
        self.machine.add_transition(trigger="system_boot", source="STATUS_INIT", dest="STATUS_IDLE")
        self.machine.add_transition(trigger="boot_failure", source="STATUS_INIT", dest="STATUS_FATAL")

        # IDLE transitions
        self.machine.add_transition(trigger="mission_received", source="STATUS_IDLE", dest="STATUS_ACTIVE")
        self.machine.add_transition(trigger="init_mission_failure", source="STATUS_IDLE", dest="STATUS_FATAL")

        # ACTIVE normal path
        self.machine.add_transition(trigger="transition_guard_enabled", source="STATUS_ACTIVE", dest="STATUS_TRANSITIONING")
        self.machine.add_transition(trigger="transition_failure", source="STATUS_TRANSITIONING", dest="STATUS_ERROR")
        self.machine.add_transition(trigger="transition_complete", source="STATUS_TRANSITIONING", dest="STATUS_ACTIVE")

        # ACTIVE with anomaly
        self.machine.add_transition(trigger="non_blocking_anomaly", source="STATUS_ACTIVE", dest="STATUS_WARNING")
        self.machine.add_transition(trigger="anomoly_resolved_or_timeout", source="STATUS_WARNING", dest="STATUS_ACTIVE")

        # ACTIVE with recoverable error
        self.machine.add_transition(trigger="recoverable_error", source="STATUS_ACTIVE", dest="STATUS_ERROR")
        self.machine.add_transition(trigger="attempt_fix", source="STATUS_ERROR", dest="STATUS_RECOVERING")
        self.machine.add_transition(trigger="recovered", source="STATUS_RECOVERING", dest="STATUS_ACTIVE")

        # Escalated error
        self.machine.add_transition(trigger="critical_failure", source="STATUS_ERROR", dest="STATUS_ERROR")

        # Terminal mission states
        self.machine.add_transition(trigger="mission_complete", source="STATUS_ACTIVE", dest="STATUS_MISSION_COMPLETE")
        self.machine.add_transition(trigger="auto_trigger", source="STATUS_MISSION_COMPLETE", dest="STATUS_IDLE")

        # Shutdown from FATAL
        self.machine.add_transition(trigger="auto_trigger", source="STATUS_FATAL", dest="STATUS_TERMINATED")  # Terminal
    
    def publish_status(self):
         print (self.state)
         self.status_publisher.publish(
              HybridAutomatonStatus(
                type=StatusFSM.state_name_map[self.state],
                message="",
                stamp=Time()
              )
         )

    def perform_event_driven_transition(self, event_msg: HybridAutomatonEvents):
            """Performs a transition based on an incoming HybridAutomatonEvents message."""
            event_type = event_msg.type
            trigger_name = self.event_triggers.get(event_type, None)

            if trigger_name is None:
                self.logger.error(f"Unknown event type: {event_type}")
                return

            self.logger.info(f"Event received: {event_type}, caused by: {event_msg.message}, invoking trigger: {trigger_name}")

            try:
                getattr(self, trigger_name)()
            except Exception as e:
                self.logger.error(f"Transition failed for trigger '{trigger_name}' from state '{self.state}': {e}")

import rclpy
from rclpy.node import Node

if __name__ == '__main__':
     rclpy.init()
     mock_node = Node('test_node')
     status_publisher = mock_node.create_publisher(
          msg_type=HybridAutomatonStatus,
          topic='/hybrid_automaton/fsm/status',
          qos_profile=10
     )
     
     status_fsm = StatusFSM(
        status_publisher=status_publisher,
        logger=mock_node.get_logger()    
     )
     status_fsm.perform_event_driven_transition(
          event_msg=HybridAutomatonEvents(
               type=HybridAutomatonEvents.EVENT_SYSTEM_BOOT
          )
     )

     time.sleep(0.2)
     status_fsm.perform_event_driven_transition(
          event_msg=HybridAutomatonEvents(
               type=HybridAutomatonEvents.EVENT_INIT_COMPLETED
          )
     )
     time.sleep(0.2)
     status_fsm.perform_event_driven_transition(
          event_msg=HybridAutomatonStatus(
               type=HybridAutomatonEvents.EVENT_MISSION_RECEIVED
          )
     )

     rclpy.shutdown()