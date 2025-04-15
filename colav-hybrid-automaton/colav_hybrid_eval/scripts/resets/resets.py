from typing import List
import numpy as np
from colav_interfaces.msg import Waypoint, AgentUpdate, ObstaclesUpdate, UnsafeSet
from geometry_msgs.msg import Point32
from shapely import Polygon, Point, LineString

VW_ACCEPTANCE_RADIUS = 10

def reset_WAYPOINT_REACHED_to_CRUISE(waypoints: List[Waypoint]) -> List[Waypoint]:
    """pops the first item in the queue of waypoints"""
    if len(waypoints) < 1:
        raise ValueError('waypoints list size less than 1, something has went wrong is guard condition')
    
    return waypoints.pop(0)

def reset_CRUISE_to_T2LOS(agent_state: AgentUpdate, obstacles_update: ObstaclesUpdate, unsafe_set: UnsafeSet, waypoints: List[Waypoint]) -> List[Waypoint]:
    """
    Reset from CRUISE to T2LOS when the guard condition is triggered.
    This function finds the rightmost visible vertex on the unsafe set from the agent's perspective,
    applies an offset to it, and creates a new virtual waypoint for the hybrid automaton to steer toward.
    """
    # 1. Get the agent's current position
    agent_x = agent_state.pose.position.x
    agent_y = agent_state.pose.position.y

    vertices = np.array(unsafe_set.vertices)
    if vertices.size == 0:
        raise ValueError('Unsafe set does not contain any vertices, Guard with reset should not have occurred.')

    # Convert vertices to shapely Polygon
    polygon = Polygon(vertices)
    if not polygon.is_valid:
        raise ValueError('Unsafe set polygon is invalid.')

    visible_vertices = []

    # 2. Check visibility of each vertex using raycasting
    for vx, vy in vertices:
        ray = LineString([(agent_x, agent_y), (vx, vy)])
        # The ray must not cross the polygon boundary (except possibly touching at the vertex)
        if polygon.exterior.crosses(ray):
            continue
        visible_vertices.append((vx, vy))

    if not visible_vertices:
        raise ValueError("No visible vertices from agent's position to unsafe set.")

    # 3. Compute angles to visible vertices
    visible_vertices_np = np.array(visible_vertices)
    vx_arr = visible_vertices_np[:, 0]
    vy_arr = visible_vertices_np[:, 1]
    angles = np.arctan2(vy_arr - agent_y, vx_arr - agent_x)

    # 4. Select the rightmost visible vertex (largest angle)
    idx_rightmost = int(np.argmax(angles))
    rightmost_x = vx_arr[idx_rightmost]
    rightmost_y = vy_arr[idx_rightmost]

    # 5. Compute the offset in the direction from the agent to the selected vertex
    # The offset value is half the VW_ACCEPTANCE_RADIUS plus 5.
    offset_distance = VW_ACCEPTANCE_RADIUS / 2 + 5
    # Create a vector from the agent to the rightmost vertex
    vec = np.array([rightmost_x - agent_x, rightmost_y - agent_y])
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise ValueError("Agent position coincides with the rightmost vertex; cannot compute offset direction.")
    direction = vec / norm
    # Apply offset
    adjusted_x = rightmost_x + offset_distance * direction[0]
    adjusted_y = rightmost_y + offset_distance * direction[1]

    # 6. Create new virtual waypoint with the adjusted position
    new_waypoint = Waypoint(
        position=Point32(x=adjusted_x, y=adjusted_y, z=0.0),
        acceptance_radius=VW_ACCEPTANCE_RADIUS
    )

    # 7. Insert the new waypoint at the beginning of the waypoint list
    waypoints.insert(0, new_waypoint)
    return waypoints