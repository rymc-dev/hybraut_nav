from automaton.core_interfaces.reset_abc import ResetABC
from .generate_virtual_waypoint_reset import GenerateVirtualWaypointReset
from .remove_virtual_waypoint import RemoveVirtualWaypointReset

__all__ = [
    'ResetABC',
    'DummyReset',
    'GenerateVirtualWaypointReset',
    'RemoveVirtualWaypointReset'
]