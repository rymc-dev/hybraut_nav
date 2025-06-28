from .reset import Reset
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

class GenerateVirtualWaypointReset(Reset):
    """
    Reset utilized in reset from cruise to t2los 1. 
    This function resets the waypoints state by generating 
    a virtual waypoint which is at an offset of the unsafe set 
    to the left or right depending on colregs.
    """

    RESET_TARGETS = {
        'waypoints_state': ROSWaypointsState
    }



    def __init__(self, **init_kwargs):
        """
        This initializes the static params of this reset. 
        longitudinal offset distance is in meters the position forwards/backwards of the 
        virtual right most vertex we should set the virtual waypoint from the unsafe set
        lateral_offset distance is the position in meters left/right for the virtual waypoint to be set.
        and virtual waypoint acceptance radius is the radius which the virtual waypoint should be considered entered
        by the agent.
        """

        super().__init__(self.RESET_TARGETS, **init_kwargs)

        self.longitudinal_offset_distance: float = init_kwargs.get("longitudinal_offset_distance")
        self.lateral_offset_distance: float = init_kwargs.get("lateral_offset_distance")
        self.virtual_waypoint_acceptance_radius: float = init_kwargs.get('virtual_waypoint_acceptance_radius')

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

        adjusted_x = rightmost_x + self.longitudinal_offset_distance * direction[0] + self.lateral_offset_distance * right_perp[0]
        adjusted_y = rightmost_y + self.longitudinal_offset_distance * direction[1] + self.lateral_offset_distance * right_perp[1]

        # Create new virtual waypoint
        new_waypoint = ROSWaypoint(
            position=Point(x=adjusted_x, y=adjusted_y, z=0.0),
            acceptance_radius=self.virtual_waypoint_acceptance_radius
        )

        # Log the waypoint creation
        self.logger.info(f"Generated virtual waypoint at ({adjusted_x:.2f}, {adjusted_y:.2f}) "
                        f"with acceptance radius {self.virtual_waypoint_acceptance_radius}")

        waypoints_state.virtual_waypoints.insert(0, new_waypoint)
        
        return self._validate_reset_output(reset_output={'waypoints_state': waypoints_state})

    def _validate_initialization(self, **init_kwargs) -> None:
        """Validate initialization params"""
        
        super()._validate_initialization(**init_kwargs)
        
        try: 
            # Validate longitudinal_offset_distance
            if not isinstance(init_kwargs['longitudinal_offset_distance'], (int, float)):
                raise TypeError(f"longitudinal_offset_distance must be a number, got {type(self.longitudinal_offset_distance)}")
        except KeyError:
            raise KeyError()

        # Validate lateral_offset_distance
        try:   
            if not isinstance(init_kwargs['lateral_offset_distance'], (int, float)):
                raise TypeError(f"lateral_offset_distance must be a number, got {type(self.lateral_offset_distance)}")
        except KeyError:
            raise KeyError()

        # Validate virtual_waypoint_acceptance_radius
        try: 
            if not isinstance(init_kwargs['virtual_waypoint_acceptance_radius'], (int, float)):
                raise TypeError(f"virtual_waypoint_acceptance_radius must be a number, got {type(self.virtual_waypoint_acceptance_radius)}")
            # Additional validation - ensure positive values where appropriate
            if init_kwargs['virtual_waypoint_acceptance_radius'] <= 0:
                raise ValueError("virtual_waypoint_acceptance_radius must be positive")

        except KeyError:
            raise KeyError() 
    
       
        # Calculate the total offset distance (Euclidean distance from origin)
        total_offset_distance = (init_kwargs['longitudinal_offset_distance']**2 + init_kwargs['lateral_offset_distance']**2)**0.5
        
        # Ensure acceptance radius is not greater than the offset distance
        if total_offset_distance > 0 and self.virtual_waypoint_acceptance_radius > total_offset_distance:
            raise ValueError(
                f"virtual_waypoint_acceptance_radius ({self.virtual_waypoint_acceptance_radius}) "
                f"cannot be greater than the total offset distance ({total_offset_distance:.2f}). "
                f"This would make the waypoint acceptance zone overlap with the origin point."
            )
        
    def _validate_states(self, **state_kwargs) -> None:
        """Validate state inputs"""
        super()._validate_states(**state_kwargs)
    

        # Type validation with descriptive error messages
        try:
            if not isinstance(state_kwargs['agent_state'], ROSAgentState):
                raise TypeError(f"First input must be AgentState, got {type()}")
        except KeyError:
            raise KeyError()
        
        try:
            if not isinstance(state_kwargs['obstacles_state'], ROSObstaclesState):
                raise TypeError(f"Second input must be ObstaclesState, got {type()}")
        except KeyError:
            raise KeyError()
        
        try:
            if not isinstance(state_kwargs['unsafe_set_state'], ROSUnsafeSetState):
                raise TypeError(f"Third input must be UnsafeSet, got {type()}")
            
                    # Validate unsafe set has vertices
            if not hasattr(state_kwargs['unsafe_set_state'], 'vertices') or state_kwargs['unsafe_set_state'].vertices is None:
                raise ValueError('vertices are not set in unsafe_set_state')
            
            if not hasattr(state_kwargs['unsafe_set_state'].convex_hull_vertices, 'data') or len(state_kwargs['unsafe_set_state'].convex_hull_vertices.data) == 0:
                raise ValueError('unsafe_set_state.vertices.data is empty')
        except KeyError:
            raise KeyError()
        
        try:
            if not isinstance(state_kwargs['waypoints_state'], ROSWaypointsState):
                raise TypeError(f"Fourth input must be WaypointsState, got {type()}")
            
            if not hasattr(state_kwargs['waypoints_state'], 'current_waypoint') or state_kwargs['waypoints_state'].current_waypoint is None:
                raise ValueError('current_waypoint is not set in waypoints_state')
            
            if not isinstance(state_kwargs['waypoints_state'].current_waypoint, ROSWaypoint):
                raise TypeError(f'current_waypoint must be of type Waypoint, got {type(waypoints_state.current_waypoint)}')
        
        except KeyError:
            raise KeyError()