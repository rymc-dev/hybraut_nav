from .guard import Guard
from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState
)
from shapely.geometry import Polygon, Point

class UnsafeConditionsGuard(Guard):
    """
    A guard condition for a hybrid automaton that evaluates whether the agent's safety radius 
    is within the unsafe set

    When called, returns True if the safety radius intersect unsafe set polygon.
    """

    def __call__(self, **state_kwargs):
        """
        this call function will return True if the agent_state safety_radius has
        intercepted the unsafe set
        """
        super().__call__(**state_kwargs)
        
        agent_state: ROSAgentState = state_kwargs.get('agent_state')
        unsafe_set_state: ROSUnsafeSetState = state_kwargs.get('unsafe_set_state')

        agent_safety_radius = agent_state.safety_radius
        agent_position = [agent_state.pose.position.x, agent_state.pose.position.y]
        agent_circle = Point(agent_position).buffer(agent_safety_radius)


        unsafe_vertices = unsafe_set_state.convex_hull_vertices.data
        unsafe_polygon = Polygon([(unsafe_vertices[i], unsafe_vertices[i + 1])
                                for i in range(0, len(unsafe_vertices), 2)])
        
        return agent_circle.intersects(unsafe_polygon)
    
    def _validate_states(self, **state_kwargs):
        super()._validate_states(**state_kwargs)
        
        try:
            try:
                if not isinstance(state_kwargs['agent_state'], ROSAgentState):
                    raise TypeError('')
                if not isinstance(state_kwargs['obstacles_state'], ROSObstaclesState):
                    raise TypeError('')
                if not isinstance(state_kwargs['unsafe_set_state'], ROSUnsafeSetState):
                    raise TypeError('')
            except KeyError:
                raise KeyError('')
        except Exception as e:
            raise e