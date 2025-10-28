from colav_interfaces.msg import AgentState, UnsafeSetState
from shapely.geometry import Polygon, Point
import inspect
from typing import List, Tuple


def extract_polygon_vertices(
        unsafe_set: UnsafeSetState) -> List[Tuple[float, float]]:
    """
      extract_polygon_vertices
      This function extracts the vertices of the unsafe_set

      returns: List[Tuple[float, float]] a list of tuple vertices, x,y coordinates
    """
    data = unsafe_set._vertices.data  # or unsafe_set.vertices.data if that's the proper attribute
    unsafe_set_vertices_x = [data[i] for i in range(0, len(data), 2)]
    unsafe_set_vertices_y = [data[i] for i in range(1, len(data), 2)]
    return list(zip(unsafe_set_vertices_x, unsafe_set_vertices_y))


def is_inside_unsafe_set(
        agent_state: AgentState,
        unsafe_set: UnsafeSetState) -> bool:
    """
    Checks if the agent is within the unsafe set based on its safety radius.

    Parameters:
      agent_state: The current state of the agent.
      unsafe_set: The unsafe set data.
      tolerance: A Duration object representing acceptable timestamp skew.
      agent_safety_radius: The safety radius for the agent.

    Returns:
      True if the agent's safety zone (a circle) intersects with the unsafe set polygon.

    Raises:
      ValueError: If the agent safety radius is invalid.
      TimeoutError: If the timestamps are not updated within the given tolerance.
    """

    # Check if there is any unsafe set defined.
    if not unsafe_set._vertices.data:
        return False

    # Validate the agent safety radius.
    if agent_state.safety_radius <= 0:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(
            f"{__file__}::{func_name}: "
            f"agent_state:AgentUpdate.safety_radius invalid: current safety radius: {agent_state.safety_radius} "
            f"expected safety radius to be > 0")

    # Create the agent's safety circle.
    agent_center = Point(
        agent_state.pose.position.x,
        agent_state.pose.position.y)
    agent_circle = agent_center.buffer(agent_state.safety_radius)

    # Create the unsafe set polygon.
    unsafe_set_vertices = extract_polygon_vertices(unsafe_set)
    unsafe_set_polygon = Polygon(unsafe_set_vertices)

    # Return whether the agent's safety circle intersects the unsafe set.
    return agent_circle.intersects(unsafe_set_polygon)


def is_imminent_collision(
        agent_state: AgentState,
        unsafe_set: UnsafeSetState) -> bool:
    """
    is_imminent_collision
    checks if a collision with unsafe set inevitable given the constraints of the agent_vessel

    returns: boolean; True is imminet_collision otherwise false
    """
    # TODO:
    return False
