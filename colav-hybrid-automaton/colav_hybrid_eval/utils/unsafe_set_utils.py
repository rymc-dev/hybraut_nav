from colav_interfaces.msg import AgentUpdate, UnsafeSet
from builtin_interfaces.msg import Duration
from shapely.geometry import Polygon, Point
import inspect
from .validate_timestamps import timestamps_within_tolerance

# Optional: Create a helper to build Duration
def make_duration(sec: int, nanosec: int) -> Duration:
    d = Duration()
    d.sec = sec
    d.nanosec = nanosec
    return d

def extract_polygon_vertices(unsafe_set: UnsafeSet):
    # Use a consistent attribute (e.g., _vertices) for extraction.
    data = unsafe_set._vertices.data  # or unsafe_set.vertices.data if that's the proper attribute
    unsafe_set_vertices_x = [data[i] for i in range(0, len(data), 2)]
    unsafe_set_vertices_y = [data[i] for i in range(1, len(data), 2)]
    return list(zip(unsafe_set_vertices_x, unsafe_set_vertices_y))

def is_inside_unsafe_set(agent_state: AgentUpdate, unsafe_set: UnsafeSet,
                           tolerance: Duration = None) -> bool:
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
    # Default tolerance if not provided.
    if tolerance is None:
        tolerance = make_duration(1, 1)

    # Validate the timestamps of agent_state and unsafe_set.
    # if not validate_timestamps(agent_state, unsafe_set, tolerance):
    #     func_name = inspect.currentframe().f_code.co_name
    #     raise TimeoutError(f"{__file__}::{func_name}: "
    #                        f"State variables agent_state and unsafe_set were not updated within tolerance: \n"
    #                        f"\tagent_update_timestamp: {agent_state.header.stamp}\n"s
    #                        f"\tunsafe_set_update_timestamp: {unsafe_set.header.stamp}\n"
    #                        f"\ttolerance: {tolerance}")

    # Check if there is any unsafe set defined.
    if not unsafe_set._vertices.data:
        return False

    # Validate the agent safety radius.
    if agent_state.safety_radius <= 0:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"{__file__}::{func_name}: "
                         f"agent_state:AgentUpdate.safety_radius invalid: current safety radius: {agent_state.safety_radius} "
                         f"expected safety radius to be > 0")

    # Create the agent's safety circle.
    agent_center = Point(agent_state.pose.position.x, agent_state.pose.position.y)
    agent_circle = agent_center.buffer(agent_state.safety_radius)

    # Create the unsafe set polygon.
    unsafe_set_vertices = extract_polygon_vertices(unsafe_set)
    unsafe_set_polygon = Polygon(unsafe_set_vertices)

    # Return whether the agent's safety circle intersects the unsafe set.
    return agent_circle.intersects(unsafe_set_polygon)

def is_imminent_collision(agent_state: AgentUpdate, unsafe_set: UnsafeSet,
                          tolerance: Duration = None):
    """
      checks if a collision with unsafe set inevitable given the constraints of the agent_vessel
       
    """
    # TODO: 
    return False