from colav_interfaces.msg import Waypoints

def is_at_final_waypoint(waypoints: Waypoints) -> bool:
    if not isinstance(waypoints, Waypoints):
        raise ValueError("invalid input to invariant 'is_at_final_waypoint'")

    if len(waypoints.waypoints) == 1:
        return False
    
    return True

def trivial_invariant() -> bool:
    return True

def failing_invariant() -> bool:
    return False