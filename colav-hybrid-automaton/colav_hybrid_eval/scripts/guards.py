from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet
from utils.timestamp_utils import validate_timestamps
from utils.unsafe_set_utils import is_inside_unsafe_set, is_imminent_collision
from builtin_interfaces.msg import Duration 
import inspect

"""1. CRUISE Guard Functions"""
def guard_CRUISE_to_T2Theta(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet):
    """This guard checks if the agent is in a position to move from 1.cruise to 3.t2theta"""
    pass

def guard_CRUISE_to_T2LOS(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet):
    """This guard checks if the agent is in a position to move from 1.cruise to 2.t2los"""
    pass

def guard_CRUISE_to_FB(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet, tolerance: Duration = None):
    """This guard checks if the agent is in iminant danger of hitting an obstacle therefore moving from 1.cruise to 4.fallback"""
    # Condition 1: If inside the unsafe set or interception with unsafe set is immenant but agnet constriants make it impossible 
    #              to decelerate enough to avoid or navigate out of the road of the unsafe set
    if tolerance is None:
        tolerance = Duration(1,0)

    if validate_timestamps(agent_state, unsafe_set) and validate_timestamps(agent_state, obstacles_state):
        func_name = inspect.currentframe().f_code.co_name
        raise TimeoutError(f"{__file__}::{func_name}: "
                           f"State variables agent_state and unsafe_set were not updated within tolerance: \n"
                           f"\tagent_update_timestamp: {agent_state.header.stamp}\n"
                           f"\tunsafe_set_update_timestamp: {unsafe_set.header.stamp}\n"
                           f"\ttolerance: {tolerance}")

    if len(unsafe_set.vertices.data) > 0: # check if unsafe set has data
        # TODO: need to find a way to get static mission_request vessel config data to this function
        if is_inside_unsafe_set(agent_state=agent_state, unsafe_set=unsafe_set, tolerance=Duration(1, 0), agent_safety_radius=2):
            return True
        
        # Condition 2: Imminent collision with static obstacles where no feasible maneuver exists 
        # to avoid impact within the available reaction time.
        # TODO: Need to find a way to pass the agent dynamics fo this function.
        if is_imminent_collision(agent_state=agent_state, unsafe_set=unsafe_set, tolerance=tolerance, agent_safety_radius=2):
            return True
        
    return False

def guard_CRUISE_to_WAYPOINT_REACHED(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet):
    """This guard checks if the agent has reached its goal waypoint therefore moving from 1.cruise to 5.waypoint_reached"""
    pass

"""2. T2LOS Guard Functions"""
def guard_T2LOS_to_CRUISE(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet):
    """This guard checks if the agent is in a position to move from 2.t2los to 1.cruise"""
    pass

def guard_T2LOS_to_FB(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet):
    """This guard checks if the agent is in iminant danger of hitting an obstacle therefore moving from 2.t2los to 4.fallback"""
    pass

"""3. T2Theta Guard Functions"""
def guard_T2Theta_to_T2LOS(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet):
    """This guard checks if the agent is in a position to move from 3.t2theta to 2.t2los"""
    pass

def guard_T2Theta_to_FB(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet):
    """This guard checks if the agent is in iminant danger of hitting an obstacle therefore moving from 3.t2theta to 4.fallback"""
    pass

"""4. FB Guard Functions"""
# NO TRANSITIONS OUT OF FALLBACK CURRENTLY THEREFORE NO GUARDS

"""5. WAYPOINT_REACHED Guard Functions"""
# NO TRANSITIONS OUT OF WAYPOINT_REACHED CURRENTLY THEREFORE NO GUARDS



