from enum import Enum, auto

class ModeConnectivity(Enum):
    STRONG = auto()
    WEAK = auto()
    UNILATERAL = auto()
    INCOMING = auto()
    OUTGOING = auto()
    ISOLATED_OK = auto()
    REACHABLE_FROM_START = auto()
    REACHABLE_TO_GOAL = auto()

    @staticmethod
    def description(connectivity):
        """Return a human-readable description of the connectivity type."""
        descriptions = {
            ModeConnectivity.STRONG: "Every mode can reach every other mode via directed edges.",
            ModeConnectivity.WEAK: "If directions are ignored, every mode is reachable from every other mode.",
            ModeConnectivity.UNILATERAL: "For every pair of modes, at least one can reach the other directly.",
            ModeConnectivity.INCOMING: "All modes have at least one inbound connection.",
            ModeConnectivity.OUTGOING: "All modes have at least one outbound connection.",
            ModeConnectivity.ISOLATED_OK: "Modes can be completely disconnected; no connectivity enforced.",
            ModeConnectivity.REACHABLE_FROM_START: "Every mode must be reachable from a designated start mode.",
            ModeConnectivity.REACHABLE_TO_GOAL: "Every mode must be able to reach a designated goal mode."
        }
        return descriptions.get(connectivity, "Unknown connectivity type.")
