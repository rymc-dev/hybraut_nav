from colav_interfaces.msg import Waypoint
from typing import List

def reset_5_to_1(waypoints: List[Waypoint]) -> List[Waypoint]:
    """pops the first item in the queue of waypoints"""
    return waypoints.pop(0)