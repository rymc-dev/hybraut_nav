"""
    Resets for the colav hybrid automaton
    bui
"""


import numpy as np
from colav_interfaces.msg import WaypointsState, Waypoint, AgentState, ObstaclesState, UnsafeSetState
from geometry_msgs.msg import Point
from builtin_interfaces.msg import Duration
from shapely import Polygon, LineString
from colav_hybrid_automaton.automaton.utils import is_timestamps_within_tolerance, get_current_ros_time, quaternion_to_heading
from typing import Tuple
from .reset_abstract import HybridAutomatonReset

class RemoveFirstWaypoint(HybridAutomatonReset):
    """
    Reset utilized on the transition from waypoint reached back to cruise
    this reset removes the current virtual waypoint in the list and assigns the 
    new current waypoint as the next value in the virtual waypoints list or the
    goal waypoint.
    """

    def __init__(self, **kwargs):
        # Call parent constructor to properly initialize the reset
        super().__init__(**kwargs)
    
    def __call__(
        self,
        waypoints_state: WaypointsState
    ) -> Tuple[WaypointsState]:
        """Pops the first virtual waypoint and sets the new current waypoint in waypoints state"""
        # Validate input - this calls the parent's validation method
        self._validate_state_inputs(waypoints_state)
        
        # Remove the first virtual waypoint
        waypoints_state.virtual_waypoints = waypoints_state.virtual_waypoints[1:]
        
        # Update current waypoint
        if len(waypoints_state.virtual_waypoints) > 0:
            waypoints_state.current_waypoint = waypoints_state.virtual_waypoints[0]
        else:
            waypoints_state.current_waypoint = waypoints_state.goal_waypoint
        
        # Return as tuple as required by the abstract class
        return (waypoints_state,)
    
    def _validate_state_inputs(self, *state_inputs) -> None:
        """Validate the state inputs for the callback"""
        # Call parent validation first
        super()._validate_state_inputs(*state_inputs)
        
        # Assuming single waypoints_state input
        if len(state_inputs) != 1:
            raise ValueError("RemoveFirstWaypoint expects exactly one state input")
        
        waypoints_state = state_inputs[0]
        
        if not isinstance(waypoints_state, WaypointsState):
            raise TypeError(
                'Exception occurred: waypoints arg passed invalid type, should be type: "colav_interfaces.msg.WaypointsState"'
            )
        
        if len(waypoints_state.virtual_waypoints) < 1:
            raise ValueError(
                'Waypoints list size less than 1, something has gone wrong in guard condition'
            )
        

class GenerateVirtualWaypoint(HybridAutomatonReset):
    """
    Reset utilized in reset from cruise to t2los 1. 
    This function resets the waypoints state by generating 
    a virtual waypoint which is at an offset of the unsafe set 
    to the left or right depending on colregs.
    """

    def __init__(self, longitudinal_offset_distance: float, lateral_offset_distance: float, virtual_waypoint_acceptance_radius: float, *args, **kwargs):
        """
        This initializes the static params of this reset. 
        longitudinal offset distance is in meters the position forwards/backwards of the 
        virtual right most vertex we should set the virtual waypoint from the unsafe set
        lateral_offset distance is the position in meters left/right for the virtual waypoint to be set.
        and virtual waypoint acceptance radius is the radius which the virtual waypoint should be considered entered
        by the agent.
        """
        # Store parameters before calling super().__init__()
        self.longitudinal_offset_distance = longitudinal_offset_distance
        self.lateral_offset_distance = lateral_offset_distance
        self.virtual_waypoint_acceptance_radius = virtual_waypoint_acceptance_radius

        # Call parent constructor - this will trigger validation
        super().__init__(*args, **kwargs)

    def __call__(
        self,
        agent_state: AgentState,
        obstacles_state: ObstaclesState,
        unsafe_set_state: UnsafeSetState,
        waypoints_state: WaypointsState,
    ) -> Tuple[WaypointsState]:
        """Create a new virtual waypoint"""
        # Validate inputs first
        self._validate_state_inputs(agent_state, obstacles_state, unsafe_set_state, waypoints_state)

        agent_x = agent_state.pose.position.x
        agent_y = agent_state.pose.position.y
        agent_heading = quaternion_to_heading(
            qx=agent_state.pose.orientation.x, 
            qy=agent_state.pose.orientation.y, 
            qz=agent_state.pose.orientation.z, 
            qw=agent_state.pose.orientation.w
        )  

        vertices = np.array(unsafe_set_state.vertices.data)
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
        new_waypoint = Waypoint(
            position=Point(x=adjusted_x, y=adjusted_y, z=0.0),
            acceptance_radius=self.virtual_waypoint_acceptance_radius
        )

        # Log the waypoint creation
        self.logger.info(f"Generated virtual waypoint at ({adjusted_x:.2f}, {adjusted_y:.2f}) "
                        f"with acceptance radius {self.virtual_waypoint_acceptance_radius}")

        waypoints_state.virtual_waypoints.insert(0, new_waypoint)
        return (waypoints_state,)

    def _validate_initialization(self, *args, **kwargs) -> None:
        """Validate initialization params"""
        
        super()._validate_initialization(*args, **kwargs)

        # Validate longitudinal_offset_distance
        if not isinstance(self.longitudinal_offset_distance, (int, float)):
            raise TypeError(f"longitudinal_offset_distance must be a number, got {type(self.longitudinal_offset_distance)}")
        
        # Validate lateral_offset_distance  
        if not isinstance(self.lateral_offset_distance, (int, float)):
            raise TypeError(f"lateral_offset_distance must be a number, got {type(self.lateral_offset_distance)}")
        
        # Validate virtual_waypoint_acceptance_radius
        if not isinstance(self.virtual_waypoint_acceptance_radius, (int, float)):
            raise TypeError(f"virtual_waypoint_acceptance_radius must be a number, got {type(self.virtual_waypoint_acceptance_radius)}")
        
        # Additional validation - ensure positive values where appropriate
        if self.virtual_waypoint_acceptance_radius <= 0:
            raise ValueError("virtual_waypoint_acceptance_radius must be positive")

        # Calculate the total offset distance (Euclidean distance from origin)
        total_offset_distance = (self.longitudinal_offset_distance**2 + self.lateral_offset_distance**2)**0.5
        
        # Ensure acceptance radius is not greater than the offset distance
        if total_offset_distance > 0 and self.virtual_waypoint_acceptance_radius > total_offset_distance:
            raise ValueError(
                f"virtual_waypoint_acceptance_radius ({self.virtual_waypoint_acceptance_radius}) "
                f"cannot be greater than the total offset distance ({total_offset_distance:.2f}). "
                f"This would make the waypoint acceptance zone overlap with the origin point."
            )
        
    def _validate_state_inputs(self, *state_inputs) -> None:
        """Validate state inputs"""

        super()._validate_state_inputs(*state_inputs)
    
        # Check correct number of inputs
        if len(state_inputs) != 4: 
            raise ValueError(f'Expected exactly 4 state inputs, got {len(state_inputs)}')
        
        agent_state = state_inputs[0]
        obstacles_state = state_inputs[1]
        unsafe_set_state = state_inputs[2]
        waypoints_state = state_inputs[3]

        # Type validation with descriptive error messages
        if not isinstance(agent_state, AgentState):
            raise TypeError(f"First input must be AgentState, got {type(agent_state)}")
        if not isinstance(obstacles_state, ObstaclesState):
            raise TypeError(f"Second input must be ObstaclesState, got {type(obstacles_state)}")
        if not isinstance(unsafe_set_state, UnsafeSetState):
            raise TypeError(f"Third input must be UnsafeSet, got {type(unsafe_set_state)}")
        if not isinstance(waypoints_state, WaypointsState):
            raise TypeError(f"Fourth input must be WaypointsState, got {type(waypoints_state)}")
        
        # Validate current waypoint is set
        if not hasattr(waypoints_state, 'current_waypoint') or waypoints_state.current_waypoint is None:
            raise ValueError('current_waypoint is not set in waypoints_state')
        
        if not isinstance(waypoints_state.current_waypoint, Waypoint):
            raise TypeError(f'current_waypoint must be of type Waypoint, got {type(waypoints_state.current_waypoint)}')
        
        # Validate agent pose is set
        if not hasattr(agent_state, 'pose') or agent_state.pose is None:
            raise ValueError('agent pose is not set in agent_state')
        
        # Validate unsafe set has vertices
        if not hasattr(unsafe_set_state, 'vertices') or unsafe_set_state.vertices is None:
            raise ValueError('vertices are not set in unsafe_set_state')
        
        if not hasattr(unsafe_set_state.vertices, 'data') or len(unsafe_set_state.vertices.data) == 0:
            raise ValueError('unsafe_set_state.vertices.data is empty')




