from transitions import Machine
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus

class StatusFSM:
    states = [
        HybridAutomatonStatus.STATUS_INIT, HybridAutomatonStatus.STATUS_IDLE,
        HybridAutomatonStatus.STATUS_ACTIVE, HybridAutomatonStatus.STATUS_TRANSITIONING,
        HybridAutomatonStatus.STATUS_WARNING, HybridAutomatonStatus.STATUS_ERROR,
        HybridAutomatonStatus.STATUS_RECOVERING, HybridAutomatonStatus.STATUS_FATAL,
        HybridAutomatonStatus.STATUS_GOAL_REACHED
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=StatusFSM.states, initial=HybridAutomatonStatus.STATUS_INIT)

        # Boot sequence
        self.machine.add_transition(trigger="boot_complete", source=HybridAutomatonStatus.STATUS_INIT, dest=HybridAutomatonStatus.STATUS_IDLE)
        self.machine.add_transition(trigger="boot_failure", source=HybridAutomatonStatus.STATUS_INIT, dest=HybridAutomatonStatus.STATUS_FATAL)

        # IDLE transitions
        self.machine.add_transition(trigger="mission_received", source=HybridAutomatonStatus.STATUS_IDLE, dest=HybridAutomatonStatus.STATUS_ACTIVE)
        self.machine.add_transition(trigger="init_failure", source=HybridAutomatonStatus.STATUS_IDLE, dest=HybridAutomatonStatus.STATUS_FATAL)

        # ACTIVE normal path
        self.machine.add_transition(trigger="transition_guard", source=HybridAutomatonStatus.STATUS_ACTIVE, dest=HybridAutomatonStatus.STATUS_TRANSITIONING)
        self.machine.add_transition(trigger="transition_complete", source=HybridAutomatonStatus.STATUS_TRANSITIONING, dest=HybridAutomatonStatus.STATUS_ACTIVE)

        # ACTIVE with anomaly
        self.machine.add_transition(trigger="non_blocking_anomaly", source=HybridAutomatonStatus.STATUS_ACTIVE, dest=HybridAutomatonStatus.STATUS_WARNING)
        self.machine.add_transition(trigger="anomaly_resolved", source=HybridAutomatonStatus.STATUS_WARNING, dest=HybridAutomatonStatus.STATUS_ACTIVE)

        # ACTIVE with recoverable error
        self.machine.add_transition(trigger="recoverable_error", source=HybridAutomatonStatus.STATUS_ACTIVE, dest=HybridAutomatonStatus.STATUS_ERROR)
        self.machine.add_transition(trigger="attempt_fix", source=HybridAutomatonStatus.STATUS_ERROR, dest=HybridAutomatonStatus.STATUS_RECOVERING)
        self.machine.add_transition(trigger="recovered", source=HybridAutomatonStatus.STATUS_RECOVERING, dest=HybridAutomatonStatus.STATUS_ACTIVE)

        # Escalated error
        self.machine.add_transition(trigger="critical_failure", source=HybridAutomatonStatus.STATUS_ERROR, dest=HybridAutomatonStatus.STATUS_ERROR)

        # Terminal mission states
        self.machine.add_transition(trigger="goal_reached", source=HybridAutomatonStatus.STATUS_ACTIVE, dest=HybridAutomatonStatus.STATUS_GOAL_REACHED)
        self.machine.add_transition(trigger="mission_complete", source=HybridAutomatonStatus.STATUS_GOAL_REACHED, dest=HybridAutomatonStatus.STATUS_TERMINATED)

        # Shutdown from FATAL
        self.machine.add_transition(trigger="shutdown", source=HybridAutomatonStatus.STATUS_FATAL, dest=HybridAutomatonStatus.STATUS_TERMINATED)  # Terminal