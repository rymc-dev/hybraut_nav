from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint
from utils.unsafe_set_utils import is_inside_unsafe_set, is_imminent_collision
from builtin_interfaces.msg import Duration 
from typing import List, Tuple
import inspect
import numpy as np
import time
from builtin_interfaces.msg import Time
from shapely.geometry import Polygon, LineString
from utils import (
    validate_timestamps,
    delta_heading,
    euclidean_distance,
    quaternion_to_heading
)
from std_msgs.msg import Header

DSF = 80 # constant distance threshold for now
# TODO: DSF Should be changed to: Dmaneuver​=Cs​+(vrel​×Tp​)

"""1. CRUISE Guard Functions"""
def guard_CRUISE_to_T2Theta(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet, waypoint: Waypoint, dsf: float = DSF) -> bool:
    """This guard checks if the agent is in a position to move from 1.cruise to 3.t2theta"""
    # condition_1: if los within distance threshold intercepts unsafe set meaning it's going to hit a dynamic obstacle
    # distance threhsold should be determined by how long it takes vessel at current velocity to turn 180 degrees 

    agent_position = (agent_state.pose.position.x, agent_state.pose.position.y)
    goal_position = (waypoint.position.x, waypoint.position.y)

    los_line = LineString([agent_position, goal_position])
    unsafe_polygon = Polygon([(unsafe_set.vertices.data[i], unsafe_set.vertices.data[i+1]) for i in range(0, len(unsafe_set.vertices.data), 2)])

    if los_line.intersects(unsafe_polygon):
        intersection_point = los_line.intersection(unsafe_polygon)
        if intersection_point.is_empty:
            return False
        
        if isinstance(intersection_point, LineString):
            intersection_point = intersection_point.interpolate(0.5, normalized=True)

        intersection_distance = euclidean_distance(agent_position, (intersection_point.x, intersection_point.y))

        if intersection_distance <= dsf:
            return True # The LOS intersects the unsafe set within the distance threshold

    # condition_2: if los within distance threshold intercepts unsafe set meaning it's going to any individual static obstacles

    return False

# TODO: Need to add 2 guard conditions for T2LOS one which executes reset condition for vw generation another for just generating virtual waypoint.
def guard_CRUISE_to_T2LOS(agent_state: AgentUpdate, current_waypoint: Waypoint, heading_error_tolerance: float = 0.1, tolerance: Duration = None) -> bool:
    """This guard checks if the agent is in a position to move from 1.cruise to 2.t2los"""
    # if tolerance is None:
    #     tolerance = Duration(sec=1,nanosec=0)

    # # should not only validate timestamp against comparator and arg operators but against current timestamp for system
    
    # if not validate_timestamps(agent_state.header.stamp, current_waypoint):
    #     func_name = inspect.currentframe().f_code.co_name
    #     raise TimeoutError(f"{__file__}::{func_name}: "
    #                        f"State variables agent_state and unsafe_set were not updated within tolerance: \n"
    #                        f"\tagent_update_timestamp: {agent_state.header.stamp}\n"
    #                        f"\tunsafe_set_update_timestamp: {unsafe_set.header.stamp}\n"
    #                    '    f"\ttolerance: {tolerance}")
    
    # Condition 1: If heading to waypoint is equal to around 0 then transition occurs
    
    # TODO: Condition 1: unsafe set on los within dsf and 

    waypoint_heading_error = delta_heading(
        x_a=agent_state.pose.position.x, 
        y_a=agent_state.pose.position.y, 
        theta_a=quaternion_to_heading(
            qx=agent_state.pose.orientation.x,
            qy=agent_state.pose.orientation.y,
            qz=agent_state.pose.orientation.z,
            qw=agent_state.pose.orientation.w
        ),
        x_w=current_waypoint.position.x,
        y_w=current_waypoint.position.y
    )
    if waypoint_heading_error < heading_error_tolerance:
        return True

    return False

def guard_CRUISE_to_FB(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet, tolerance: Duration = None):
    """This guard checks if the agent is in iminant danger of hitting an obstacle therefore moving from 1.cruise to 4.fallback"""
    # Condition 1: If inside the unsafe set or interception with unsafe set is immenant but agnet constriants make it impossible # TODO: NEED TO WORK ON THIS
    #              to decelerate enough to avoid or navigate out of the road of the unsafe set
    if tolerance is None:
        tolerance = Duration(sec=1,nanosec=0)

    # if not validate_timestamps(agent_state.header.stamp, unsafe_set.header.stamp, tolerance) and validate_timestamps(agent_state.header.stamp, obstacles_state.header.stamp, tolerance):
    #     func_name = inspect.currentframe().f_code.co_name
    #     raise TimeoutError(f"{__file__}::{func_name}: "
    #                        f"State variables agent_state and unsafe_set were not updated within tolerance: \n"
    #                        f"\tagent_update_timestamp: {agent_state.header.stamp}\n"
    #                        f"\tunsafe_set_update_timestamp: {unsafe_set.header.stamp}\n"
    #                        f"\ttolerance: {tolerance}")

    if len(unsafe_set.vertices.data) > 0: # check if unsafe set has data
        # TODO: need to find a way to get static mission_request vessel config data to this function
        if is_inside_unsafe_set(agent_state=agent_state, unsafe_set=unsafe_set, tolerance=tolerance):
            return True
        
        # Condition 2: Imminent collision with static obstacles where no feasible maneuver exists 
        # to avoid impact within the available reaction time.
        # TODO: Need to find a way to pass the agent dynamics fo this function.
        if is_imminent_collision(agent_state=agent_state, unsafe_set=unsafe_set, tolerance=tolerance):
            return True
        
    return False

def guard_CRUISE_to_WAYPOINT_REACHED(agent_state: AgentUpdate, current_waypoint: Waypoint, tolerance: Duration = None):
    """This guard checks if the agent has reached its goal waypoint therefore moving from 1.cruise to 5.waypoint_reached"""
    # condition_1: If vessel is currently within waypoint acceptance radius
    if tolerance is None:
        tolerance = Duration(sec=1,nanosec=0)
    
    current_time = Time() # time should be the time now
    # if validate_timestamps(agent_state.header.stamp, current_time):
    #     raise ValueError('timeout')
    
    def euclidean_distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    if euclidean_distance(
        [agent_state.pose.position.x, agent_state.pose.position.y],
        [current_waypoint.position.x, current_waypoint.position.y]
    ) < current_waypoint.acceptance_radius:
        return True
    
    return False
        
"""2. T2LOS Guard Functions"""
def guard_T2LOS_to_CRUISE(agent_state: AgentUpdate, current_waypoint: Waypoint, heading_error_tolerance: float, tolerance: Duration = None) -> bool:
    """This guard checks if the agent is in a position to move from 2.t2los to 1.cruise"""
    return not guard_CRUISE_to_T2LOS(agent_state, current_waypoint, heading_error_tolerance, tolerance)

def guard_T2LOS_to_FB(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet, tolerance: Duration = None):
    """This guard checks if the agent is in iminant danger of hitting an obstacle therefore moving from 2.t2los to 4.fallback"""
    return guard_CRUISE_to_FB(agent_state, obstacles_state, unsafe_set, tolerance)

"""3. T2Theta Guard Functions"""
def guard_T2Theta_to_T2LOS(agent_state: AgentUpdate, virtual_waypoint: Waypoint): # This control mode finds a safe 
    """This guard checks that a virtual waypoint has been set and is not None therefore allowing us to move to T2LOS"""
    return virtual_waypoint is not None 

def guard_T2Theta_to_FB(agent_state: AgentUpdate, obstacles_state: ObstaclesUpdate, unsafe_set: UnsafeSet, tolerance: Duration = None):
    """This guard checks if the agent is in iminant danger of hitting an obstacle therefore moving from 3.t2theta to 4.fallback"""
    return guard_CRUISE_to_FB(agent_state, obstacles_state, unsafe_set, tolerance)

"""4. FB Guard Functions"""
# NO TRANSITIONS OUT OF FALLBACK CURRENTLY THEREFORE NO GUARDS

"""5. WAYPOINT_REACHED Guard Functions"""
# NO TRANSITIONS OUT OF WAYPOINT_REACHED CURRENTLY THEREFORE NO GUARDS