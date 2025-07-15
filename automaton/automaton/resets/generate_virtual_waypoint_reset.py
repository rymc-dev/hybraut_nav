from automaton.resets import ResetABC
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from shapely import LineString, Polygon, Point  
import numpy as np
from colav_hybrid_automaton.automaton._internal.utils import quaternion_to_heading
from colav_hybrid_automaton.automaton._internal.types import InputSpec
from std_msgs.msg import Float64MultiArray

class GenerateVirtualWaypointReset(ResetABC):
    """
    Reset utilized in reset from cruise to t2los 1. 
    This function resets the waypoints state by generating 
    a virtual waypoint which is at an offset of the unsafe set 
    to the left or right depending on colregs.
    """

    _init_input_spec = [
        InputSpec(name="longitudinal_offset_distance", type=float),
        InputSpec(name="lateral_offset_distance", type=float), 
        InputSpec(name="virtual_waypoint_acceptance_radius", type=float)
    ]

    _state_input_spec = [
        InputSpec(name="agent_state", type=ROSAgentState),
        InputSpec(name="obstacles_state", type=ROSObstaclesState),
        InputSpec(name="unsafe_set_state", type=ROSUnsafeSetState),
        InputSpec(name="waypoints_state", type=ROSWaypointsState)
    ]

    _reset_targets_spec = [
        InputSpec(name="waypoints_state", type=ROSWaypointsState)
    ]

    def __call__(self, **state_kwargs) -> dict[str, ROSWaypointsState]:
        """Create a new virtual waypoint"""
        # Validate inputs first
        super()._validate_states(**state_kwargs)

        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        obstacles_state: ROSObstaclesState = state_kwargs.get('obstacles_state')
        unsafe_set_state: ROSUnsafeSetState = state_kwargs.get('unsafe_set_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')
        
        agent_x = agent_state.pose.position.x
        agent_y = agent_state.pose.position.y
        agent_heading = quaternion_to_heading(
            qx=agent_state.pose.orientation.x, 
            qy=agent_state.pose.orientation.y, 
            qz=agent_state.pose.orientation.z, 
            qw=agent_state.pose.orientation.w
        )  

        vertices = np.array(unsafe_set_state.convex_hull_vertices.data)
        if vertices.size == 0:
            raise RuntimeError(
                'Unsafe set does not contain any vertices, Guard must have activated invalidely.')

        vertices_reshaped = vertices.reshape(-1, 2)
        polygon = Polygon(vertices_reshaped)
        if not polygon.is_valid:
            raise RuntimeError('Unsafe set polygon is invalid.')

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

        adjusted_x = float(rightmost_x + self.__getattribute__('longitudinal_offset_distance') * direction[0] + self.__getattribute__('lateral_offset_distance') * right_perp[0])
        adjusted_y = float(rightmost_y + self.__getattribute__('longitudinal_offset_distance') * direction[1] + self.__getattribute__('lateral_offset_distance') * right_perp[1])

        # Create new virtual waypoint
        new_waypoint = ROSWaypoint(
            position=Point(adjusted_x, adjusted_y, 0.0),
            acceptance_radius=self.__getattribute__('virtual_waypoint_acceptance_radius')
        )

        # Log the waypoint creation
        self.logger.info(f"Generated virtual waypoint at ({adjusted_x:.2f}, {adjusted_y:.2f}) "
                        f"with acceptance radius {self.__getattribute__('virtual_waypoint_acceptance_radius')}")

        waypoints_state.virtual_waypoints.insert(0, new_waypoint)
        reset_output = {'waypoints_state': waypoints_state}
        self._validate_reset_output(reset_output)
        return reset_output

    def _validate_initialization(self, **init_kwargs) -> None:
        """Validate initialization params"""
        
        super()._validate_initialization(**init_kwargs)
        
        # Additional validation - ensure positive values where appropriate
        if init_kwargs['virtual_waypoint_acceptance_radius'] <= 0:
            raise ValueError("virtual_waypoint_acceptance_radius must be positive")

       
        # Calculate the total offset distance (Euclidean distance from origin)
        total_offset_distance = (init_kwargs['longitudinal_offset_distance']**2 + init_kwargs['lateral_offset_distance']**2)**0.5
        
        # Ensure acceptance radius is not greater than the offset distance
        if total_offset_distance > 0 and init_kwargs['virtual_waypoint_acceptance_radius'] > total_offset_distance:
            raise ValueError(
                f"virtual_waypoint_acceptance_radius ({init_kwargs['virtual_waypoint_acceptance_radius']}) "
                f"cannot be greater than the total offset distance ({total_offset_distance:.2f}). "
                f"This would make the waypoint acceptance zone overlap with the origin point."
            )
        
    def validate_states(self, **state_kwargs) -> None:
        """Validate state inputs with comprehensive error checking."""
        # Parent class validates that states exist and are of correct types
        super()._validate_states(**state_kwargs)
        
        # Additional domain-specific validations
        self._validate_unsafe_set_state(state_kwargs['unsafe_set_state'])
        self._validate_waypoints_state(state_kwargs['waypoints_state'])

    def _validate_unsafe_set_state(self, unsafe_set_state) -> None:
        """Validate unsafe_set_state has required attributes and data."""
        if not hasattr(unsafe_set_state, 'vertices') or unsafe_set_state.vertices is None:
            raise ValueError("unsafe_set_state must have 'vertices' attribute that is not None")
        
        if not hasattr(unsafe_set_state, 'convex_hull_vertices'):
            raise ValueError("unsafe_set_state must have 'convex_hull_vertices' attribute")
        
        convex_hull = unsafe_set_state.convex_hull_vertices
        if not hasattr(convex_hull, 'data') or len(convex_hull.data) == 0:
            raise ValueError("unsafe_set_state.convex_hull_vertices.data must exist and not be empty")

    def _validate_waypoints_state(self, waypoints_state) -> None:
        """Validate waypoints_state has required current_waypoint."""
        if not hasattr(waypoints_state, 'current_waypoint'):
            raise ValueError("waypoints_state must have 'current_waypoint' attribute")
        
        current_waypoint = waypoints_state.current_waypoint
        if current_waypoint is None:
            raise ValueError("waypoints_state.current_waypoint cannot be None")
        
        if not isinstance(current_waypoint, ROSWaypoint):
            raise TypeError(
                f"waypoints_state.current_waypoint must be of type ROSWaypoint, "
                f"got {type(current_waypoint).__name__}"
            )
        
if __name__ == '__main__':
    init_kwargs = {
        "longitudinal_offset_distance": 10.0, 
        "lateral_offset_distance": 10.0, 
        "virtual_waypoint_acceptance_radius":5.0
    }

    reset:ResetABC = GenerateVirtualWaypointReset(**init_kwargs)
    vertices = [120.0, 100.0, 110.0, 117.32, 90.0, 117.32, 80.0, 100.0, 90.0, 82.68, 110.0, 82.68]

    # Create Float64MultiArray with your chosen vertices
    convex_hull_array = Float64MultiArray()
    convex_hull_array.data = vertices  # or square_vertices or triangle_vertices

    state_kwargs = {
        "agent_state": ROSAgentState(),
        "obstacles_state": ROSObstaclesState(),
        "unsafe_set_state":ROSUnsafeSetState(convex_hull_vertices=convex_hull_array),
        "waypoints_state": ROSWaypointsState()
    }
    reset_output = reset.__call__(**state_kwargs)

    print (reset_output)