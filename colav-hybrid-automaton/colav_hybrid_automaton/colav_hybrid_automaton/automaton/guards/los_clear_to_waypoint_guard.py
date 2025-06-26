from .guard import Guard
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState,
    WaypointsState as ROSWaypointsState,
    Waypoint as ROSWaypoint
)
from colav_hybrid_automaton.automaton.utils import euclidean_distance
from shapely.geometry import Polygon, LineString


class LOSClearToWaypointGuard(Guard):
    """
    A guard condition for a hybrid automaton that evaluates whether the agent's line of 
    sight to the current waypoint is clear and not obstructed within a specified threshold.
    
    This class is typically used in a state machine or behavior tree context to determine 
    whether a transition condition is met clear line of sight (LOS) to goal waypoint

    When called with the agent state, waypoints state, unsafe set state obstacles state
    this class checks based on the los_distance_threshold if we intercept unsafe set 
    which is a safety region determined in real time for dynamic obstacles and if we intercept
    any static obstacles individually.

    Args:
        los_distance_threshold (float, optional): 
            The distance threshold for los of the agent not being clear.

    Raises:
        TypeError: If 'los_distance_threshold' is not a float.
        ValueError: If 'los_distance_threshold' is less than 0.01.
    """
    def __init__(self, **kwargs):
        """
            los_distance_threshold: float: represents the distance which we analyse los 
                                           to determine if los is clear to the waypoint
        """
        super().__init__(**kwargs)

        self.los_distance_threshold = kwargs.get('los_distance_threshold')
    
    def __call__(self, **state_kwargs) -> bool:
        """_summary_

        Args:
            agent_state (ROSAgentState): _description_
            obstacles_state (ROSObstaclesState): _description_
            unsafe_set_state (ROSUnsafeSetState): _description_
            waypoints_state (ROSWaypointsState): _description_

        Returns:
            _type_: _description_
        """
        super().__call__(**state_kwargs)

        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        obstacles_state: ROSObstaclesState = state_kwargs.get('obstacles_state')
        unsafe_set_state: ROSUnsafeSetState = state_kwargs.get('unsafe_set_state')
        waypoints_state: ROSWaypointsState = state_kwargs.get('waypoints_state')

        agent_position = None
        goal_position = None
        los_line = None

        current_waypoint: ROSWaypoint = waypoints_state.current_waypoint

        agent_position = (agent_state.pose.position.x, agent_state.pose.position.y)

        goal_position = (current_waypoint.position.x, current_waypoint.position.y)

        los_line = LineString([agent_position, goal_position])

        # Create unsafe polygon from vertex data (assumes [x1, y1, x2, y2, ...])
        unsafe_vertices = unsafe_set_state.convex_hull_vertices.vertices.data
        unsafe_polygon = Polygon([(unsafe_vertices[i], unsafe_vertices[i + 1])
                                for i in range(0, len(unsafe_vertices), 2)])

        # Check for LOS intersection with unsafe polygon.
        if los_line.intersects(unsafe_polygon):
            intersection = los_line.intersection(unsafe_polygon)

            if intersection.is_empty:
                return False

            # If the intersection is a LineString, take a midpoint.
            if isinstance(intersection, LineString):
                intersection = intersection.interpolate(0.5, normalized=True)

            # Calculate distance from the agent to the intersection point.
            intersection_distance = euclidean_distance(
                agent_position, (intersection.x, intersection.y))
            if intersection_distance <= self.los_distance_threshold:
                return True

        return False
    
    def _validate_initialization(self, **init_kwargs):
        """_summary_

        Raises:
            TypeError: _description_
            ValueError: _description_

        Returns:
            _type_: _description_
        """

        super()._validate_initialization(**init_kwargs)
        try:
            if not isinstance(init_kwargs.get('los_distance_threshold'), float):
                raise TypeError('los distance threshold must be type float')
            
            if init_kwargs.get('los_distance_threshold') < 0.0: 
                raise ValueError('los_distance_threshold can not be a negative number')
        except Exception as e:
            raise e


    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)

        try: 
            if not isinstance(state_kwargs.get('agent_state'), ROSAgentState):
                raise ValueError('agent state given not current type')
        except Exception as e:
            raise e 

        try:
            if not isinstance(state_kwargs.get('waypoints_state', ROSWaypointsState)):
                raise ValueError('waypoints state given not correct type.')
        except Exception as e:
            pass

        try: 
            if not isinstance(state_kwargs.get('unsafe_set_state'), ROSUnsafeSetState):
                raise ValueError('unsafe set input not of correct type ROSUnsafeSet')
        except Exception as e:
            raise e
        
        try:
            if not isinstance(state_kwargs.get('obstacles_state', ROSObstaclesState)):
                raise ValueError('obstacles state not of the correct type ROSObstaclesState')
        except Exception as e:
            raise e
    
