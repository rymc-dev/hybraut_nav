from nodes.guards import GuardABC
from nodes._internal.types import InputSpec

from colav_interfaces.msg import (
    AgentState as ROSAgentState,
    ObstaclesState as ROSObstaclesState,
    UnsafeSetState as ROSUnsafeSetState
)
from shapely.geometry import Polygon, Point

class UnsafeConditionsGuard(GuardABC):
    """
    A guard condition for a hybrid automaton that evaluates whether the agent's safety radius 
    is within the unsafe set

    When called, returns True if the safety radius intersect unsafe set polygon.
    """

    _state_input_spec = [
        InputSpec(name='agent_state', type=ROSAgentState),
        InputSpec(name='unsafe_set_state', type=ROSUnsafeSetState)
    ]

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
    
if __name__ == '__main__':
    from geometry_msgs.msg import Point as ROSPoint 
    init_kwarg_names = UnsafeConditionsGuard.init_input_names()
    init_kwargs = {}
    guard: GuardABC = UnsafeConditionsGuard(**init_kwargs)

    state_kwarg_names = UnsafeConditionsGuard.state_input_names()
    state_kwargs = {
        state_kwarg_names[0]: ROSAgentState(),
        state_kwarg_names[1]: ROSUnsafeSetState()
    } 
    guard_evaluation: bool = guard.__call__(**state_kwargs)
    print (guard_evaluation)
