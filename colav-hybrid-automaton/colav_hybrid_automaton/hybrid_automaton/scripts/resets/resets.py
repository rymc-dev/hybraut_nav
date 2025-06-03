import numpy as np
from colav_interfaces.msg import Waypoints, Waypoint, AgentUpdate, ObstaclesUpdate, UnsafeSet
from geometry_msgs.msg import Point
from builtin_interfaces.msg import Duration
from shapely import Polygon, LineString
from hybrid_automaton.utils import is_timestamps_within_tolerance, get_current_ros_time
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
    """
    Reset from CRUISE to T2LOS when the guard condition is triggered.
    This function finds the rightmost visible vertex on the unsafe set from the agent's perspective,
    applies an offset to it, and creates a new virtual waypoint for the hybrid automaton to steer toward.
    """
    # TODO: validate values
    if not isinstance(agent_state, AgentUpdate) or \
        not isinstance(obstacles_update, ObstaclesUpdate) or \
        not isinstance(unsafe_set, UnsafeSet) or \
        not isinstance(waypoints, Waypoints):
        raise ValueError(
            'exception occured: input args to function have incorrect types')

    # TODO: validate timestamps
    # try:
    #     sys_stamp = get_current_ros_time()
    #     validate_timestamps_within_tolerance(agent_state.header.stamp, sys_stamp, tolerance)
    #     validate_timestamps_within_tolerance(obstacles_update.header.stamp, sys_stamp, tolerance)
    #     validate_timestamps_within_tolerance(unsafe_set.header.stamp, sys_stamp, tolerance)
    # except TimeoutError as e:
    #     raise TimeoutError(f'Timeour error at reset_CRUISE_to_T2LOS during timestamp validation: {e}')
    
    # TODO: check if unsafe set is valid polyshape

    # TODO: check if any static obstacles exist in environment

    # 1. Get the agent's current position
    agent_x = agent_state.pose.position.x
    agent_y = agent_state.pose.position.y

    vertices = np.array(unsafe_set.vertices.data)
    if vertices.size == 0:
        raise ValueError(
            'Unsafe set does not contain any vertices, Guard with reset should not have occurred.')

    vertices_reshaped = vertices.reshape(-1, 2)
    # Convert vertices to shapely Polygon
    polygon = Polygon(vertices_reshaped)
    if not polygon.is_valid:
        raise ValueError('Unsafe set polygon is invalid.')

    visible_vertices = []

    # 2. Check visibility of each vertex using raycasting
    for vx, vy in vertices_reshaped:
        ray = LineString([(agent_x, agent_y), (vx, vy)])
        # The ray must not cross the polygon boundary (except possibly touching
        # at the vertex)
        if polygon.exterior.crosses(ray):
            continue
        visible_vertices.append((vx, vy))

    if not visible_vertices:
        raise ValueError(
            "No visible vertices from agent's position to unsafe set.")

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
        raise ValueError(
            "Agent position coincides with the rightmost vertex; cannot compute offset direction.")
    direction = vec / norm
    # Apply offset
    adjusted_x = rightmost_x + offset_distance * direction[0]
    adjusted_y = rightmost_y + offset_distance * direction[1]

    # 6. Create new virtual waypoint with the adjusted position
    new_waypoint = Waypoint(
        position=Point(x=adjusted_x, y=adjusted_y, z=0.0),
        acceptance_radius=VW_ACCEPTANCE_RADIUS
    )

    # 7. Insert the new waypoint at the beginning of the waypoint list
    waypoints.waypoints.insert(0, new_waypoint)
    return [waypoints]
