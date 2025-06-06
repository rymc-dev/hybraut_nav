import numpy as np
from colav_interfaces.msg import Waypoints, Waypoint, AgentUpdate, ObstaclesUpdate, UnsafeSet
from geometry_msgs.msg import Point
from builtin_interfaces.msg import Duration
from shapely import Polygon, LineString
from colav_hybrid_automaton.automaton.utils import is_timestamps_within_tolerance, get_current_ros_time, quaternion_to_heading
from typing import Tuple

VW_ACCEPTANCE_RADIUS = 10.0


def remove_first_waypoint(waypoints: Waypoints) -> Tuple[Waypoints]:
    """pops the first item in the queue of waypoints"""
    # validate arg
    if not isinstance(waypoints, Waypoints):
        raise ValueError(
            'exception occured: waypoints arg passed in invalid type, should be type: "colav_interfaces.msg.waypoints'
        )

    if len(waypoints.waypoints) < 2:
        raise ValueError(
            'waypoints list size less than 1, something has went wrong is guard condition')
    
    waypoints.waypoints = waypoints.waypoints[1:]
    return [waypoints]


def create_virtual_waypoint(
        agent_state: AgentUpdate,
        obstacles_update: ObstaclesUpdate,
        unsafe_set: UnsafeSet,
        waypoints: Waypoints,
        tolerance: Duration = Duration(sec=1)) -> Tuple[Waypoints]:

    # Validate inputs (same as your code)

    agent_x = agent_state.pose.position.x
    agent_y = agent_state.pose.position.y
    agent_heading = quaternion_to_heading(qx=agent_state.pose.orientation.x, qy=agent_state.pose.orientation.y, qz=agent_state.pose.orientation.z, qw=agent_state.pose.orientation.w)  

    vertices = np.array(unsafe_set.vertices.data)
    if vertices.size == 0:
        raise ValueError(
            'Unsafe set does not contain any vertices, Guard with reset should not have occurred.')

    vertices_reshaped = vertices.reshape(-1, 2)
    polygon = Polygon(vertices_reshaped)
    if not polygon.is_valid:
        raise ValueError('Unsafe set polygon is invalid.')

    visible_vertices = []

    for vx, vy in vertices_reshaped:
        ray = LineString([(agent_x, agent_y), (vx, vy)])
        if polygon.exterior.crosses(ray):
            continue
        visible_vertices.append((vx, vy))

    if not visible_vertices:
        raise ValueError(
            "No visible vertices from agent's position to unsafe set.")

    visible_vertices_np = np.array(visible_vertices)
    vx_arr = visible_vertices_np[:, 0]
    vy_arr = visible_vertices_np[:, 1]

    # Compute angle relative to agent heading
    global_angles = np.arctan2(vy_arr - agent_y, vx_arr - agent_x)
    relative_angles = global_angles - agent_heading

    # Normalize to [-pi, pi]
    relative_angles = (relative_angles + np.pi) % (2 * np.pi) - np.pi

    # Right side = negative angles, pick minimum angle (most right)
    idx_rightmost = int(np.argmin(relative_angles))
    rightmost_x = vx_arr[idx_rightmost]
    rightmost_y = vy_arr[idx_rightmost]

    # Vector from agent to rightmost vertex
    vec = np.array([rightmost_x - agent_x, rightmost_y - agent_y])
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise ValueError(
            "Agent position coincides with the rightmost vertex; cannot compute offset direction.")
    direction = vec / norm

    # Compute right perpendicular vector to 'direction' (for right offset)
    # If forward vector is (dx, dy), right vector is (dy, -dx)
    right_perp = np.array([direction[1], -direction[0]])

    # Offset: 50 meters to the right + small forward offset (optional)
    offset_right = 50.0
    offset_forward = 10.0  # you can adjust this if you want some forward offset too

    adjusted_x = rightmost_x + offset_forward * direction[0] + offset_right * right_perp[0]
    adjusted_y = rightmost_y + offset_forward * direction[1] + offset_right * right_perp[1]

    # Create new virtual waypoint
    new_waypoint = Waypoint(
        position=Point(x=adjusted_x, y=adjusted_y, z=0.0),
        acceptance_radius=VW_ACCEPTANCE_RADIUS
    )

    waypoints.waypoints.insert(0, new_waypoint)
    return [waypoints]
