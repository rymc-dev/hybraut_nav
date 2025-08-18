from hybraut_executor_watchdog.fsm import FSM
from rclpy.node import Node
from hybraut_model import HybridAutomaton
from hybraut_interfaces.msg import AutomatonStatus
from hybraut_interfaces.msg import AutomatonEvents
from hyb


class RuntimeWatchdog(FSM):
    def __init__(self, node: Node, hybraut_model: HybridAutomaton):

        self.state = ExectorState.INACTIVE
        self.node = node
        self.hybraut_model = hybraut_model

        super().__init__(node=node, cb_group=CB_GROUP, qos=QOS, auto_activate=False)
