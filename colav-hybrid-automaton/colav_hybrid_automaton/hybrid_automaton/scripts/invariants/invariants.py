from colav_interfaces.msg import Waypoints

def is_goal_waypoints(waypoints: Waypoints) -> bool:
    if isinstance(waypoints, Waypoints):
        raise ValueError("invalid input to invariant 'is_goal_waypoints'")

    if len(waypoints.waypoints) == 1:
        return True
    
    return False

def trivial_invariant() -> bool:
    return True

def failing_invariant() -> bool:
    return False