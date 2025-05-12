#!/usr/bin/python3
"""
Unit Test Suite for COLAV Hybrid Automaton Guard Conditions.

This module contains unit tests to validate the behavior of individual guard condition functions
used in the COLAV Hybrid Automaton. Both standard and edge cases are tested to ensure full coverage
and confirm the expected functionality of each guard.

:author: Ryan McKee
:date: April 11, 2025
"""

from typing import Tuple, Union

import pytest

from builtin_interfaces.msg import Time
from geometry_msgs.msg import Point, Point32, Pose, Quaternion
from std_msgs.msg import Float64MultiArray, Header, MultiArrayDimension, MultiArrayLayout

from colav_interfaces.msg import (
    AgentUpdate,
    ObstaclesUpdate,
    UnsafeSet,
    Waypoint,
    Waypoints,
)

from hybrid_automaton.scripts.guards import (
    # guard_CRUISE_to_FB,
    # guard_CRUISE_to_T2LOS_1,
    is_heading_not_within_tolerance,
    # guard_CRUISE_to_WAYPOINT_REACHED,
    # guard_T2LOS_to_CRUISE,
    # guard_T2LOS_to_FB,
    # guard_WAYPOINT_REACHED_to_CRUISE,
)
# from hybrid_automaton.utils import get_current_ros_time
# from builtin_interfaces.msg import Duration

# """CRUISE Guards Tests"""
# @pytest.mark.parametrize("input_args, expected_output, description", [
#     # Test Case 1: unsafe_set on los and within distance threshold
#     (
#         (
#             AgentUpdate(
#                 header=Header(stamp=get_current_ros_time()),
#                 pose=Pose(
#                     position=Point(
#                         x=float(400),
#                         y=float(100)
#                     )
#                 ),
#                 velocity=float(10)
#             ),
#             ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
#             UnsafeSet(
#                 header=Header(stamp=get_current_ros_time()),
#                 vertices=Float64MultiArray(
#                     layout=MultiArrayLayout(
#                         dim=[MultiArrayDimension(label='vertices', stride=2)]
#                     ),
#                     data=[
#                         300.0, 100.0,  # Point 1
#                         350.0, 150.0,  # Point 2
#                         400.0, 150.0,  # Point 3
#                         400.0, 100.0   # Point 4
#                     ]
#                 )
#             ),
#             Waypoint(
#                 position=Point32(x=float(500), y=float(100))
#             ),
#             float(50),
#             Duration(sec=10)
#         ),
#         True,
#         "unsafe set on los within distance threshold"
#     ),
#     # Test Case 2: unsafe_set on los but outside distance threshold
#     (
#         (
#             AgentUpdate(
#                 header=Header(stamp=get_current_ros_time()),
#                 pose=Pose(
#                     position=Point(
#                         x=float(100),
#                         y=float(100)
#                     )
#                 ),
#                 velocity=float(10)
#             ),
#             ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
#             UnsafeSet(
#                 header=Header(stamp=get_current_ros_time()),
#                 vertices=Float64MultiArray(
#                     layout=MultiArrayLayout(
#                         dim=[MultiArrayDimension(label='vertices', stride=2)]
#                     ),
#                     data=[
#                         300.0, 100.0,  # Point 1
#                         350.0, 150.0,  # Point 2
#                         400.0, 150.0,  # Point 3
#                         400.0, 100.0   # Point 4
#                     ]
#                 )
#             ),
#             Waypoint(
#                 position=Point32(x=float(500), y=float(100))
#             ),
#             float(50),
#             Duration(sec=10)
#         ),
#         False,
#         "unsafe_set on los but outside distance threshold"
#     ),
#     # Test Case 3: Unsafe set within distance threshold but not on los
#     (
#         (
#             AgentUpdate(
#                 header=Header(stamp=get_current_ros_time()),
#                 pose=Pose(
#                     position=Point(
#                         x=float(100),
#                         y=float(100)
#                     )
#                 ),
#                 velocity=float(10)
#             ),
#             ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
#             UnsafeSet(
#                 header=Header(stamp=get_current_ros_time()),
#                 vertices=Float64MultiArray(
#                     layout=MultiArrayLayout(
#                         dim=[MultiArrayDimension(label='vertices', stride=2)]
#                     ),
#                     data=[
#                         250.0, 130.0,  # Point 1
#                         260.0, 130.0,  # Point 2
#                         260.0, 140.0,  # Point 3
#                         250.0, 140.0   # Point 4
#                     ]
#                 )
#             ),
#             Waypoint(
#                 position=Point32(x=float(500), y=float(100))
#             ),
#             float(50),
#             Duration(sec=10)
#         ),
#         False,
#         "unsafe set within distance threshold but not on los"
#     ),
#     # Test Case 4: unsafe set outside distance threshold off line of sight
#     (
#         (
#             AgentUpdate(
#                 header=Header(stamp=get_current_ros_time()),
#                 pose=Pose(
#                     position=Point(
#                         x=float(100),
#                         y=float(100)
#                     )
#                 ),
#                 velocity=float(10)
#             ),
#             ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
#             UnsafeSet(
#                 header=Header(stamp=get_current_ros_time()),
#                 vertices=Float64MultiArray(
#                     layout=MultiArrayLayout(
#                         dim=[MultiArrayDimension(label='vertices', stride=2)]
#                     ),
#                     data=[
#                         300.0, 300.0,  # Point 1
#                         310.0, 300.0,  # Point 2
#                         310.0, 310.0,  # Point 3
#                         300.0, 310.0   # Point 4
#                     ]
#                 )
#             ),
#             Waypoint(
#                 position=Point32(x=float(500), y=float(100))
#             ),
#             float(50),
#             Duration(sec=10)
#         ),
#         False,
#         "unsafe set outside distance threshold off line of sight"
#     ),
#     # # Test Case 5: static obstacle on los within distance threshold
#     # (
#     #     (),
#     #     True,
#     #     'Static obstacle on los within distance threshold'
#     # ),
#     # # Test Case 6: static obstacle on los but not within distance threshold
#     # (
#     #     (),
#     #     False,
#     #     'static obstacle on los but not within distance threshold'
#     # ),
#     # # Test Case 7: static obstacle within distance threshold not on los
#     # (
#     #     (),
#     #     False,
#     #     "static within distance threshold not on los"
#     # ),
#     # # Test Case 8: static obstacle outside distance threshold outside line of sight
#     # (
#     #     (),
#     #     False,
#     #     "static obstacle outside distance threshold outside line of sight"
#     # ),
#     # Test Case 9: agent_update out of sync
#     (
#         (
#             AgentUpdate(header=Header(stamp=Time(sec=0, nanosec=0))),
#             ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
#             UnsafeSet(header=Header(stamp=get_current_ros_time())),
#             Waypoint(),
#             float(50)
#         ),
#         TimeoutError('Timeout Exception occured'),
#         "Timeout error was not thrown for ObstaclesUpdate"
#     ),
#     # Test Case 20: obstacle_update out of sync
#     (
#         (
#             AgentUpdate(header=Header(stamp=get_current_ros_time())),
#             ObstaclesUpdate(header=Header(stamp=Time(sec=1, nanosec=0))),
#             UnsafeSet(header=Header(stamp=get_current_ros_time())),
#             Waypoint(),
#             float(50)
#         ),
#         TimeoutError('Timeout Exception occured'),
#         "Timeout error was not thrown for ObstaclesUpdate"
#     ),
#     # Test Case 11: unsafe_set out of sync
#     (
#         (
#             AgentUpdate(header=Header(stamp=get_current_ros_time())),
#             ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
#             UnsafeSet(header=Header(stamp=Time(sec=0, nanosec=0))),
#             Waypoint(),
#             float(50)
#         ),
#         TimeoutError('Timeout Exception occured'),
#         "Timeout error was not thrown for ObstaclesUpdate"
#     ),
# ])
# def test_guard_CRUISE_to_T2LOS_1(
#     input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, float, Duration],
#     expected_output: Union[bool, Exception],
#     description: str
# ):
#     """   
#     Test if the guard_CRUISE_to_T2Theta is working correctly.

#     This test verifies:
#     1. guard correctly evaluates unsafe set scenarios and returns expected transition evaluation
#     2. TODO: guard correctly evaluates static obstacles scenarios and returns expected transition evaluation
#     3. guard handles out of sync state updates and raises exception
#     4. TODO: guard handles invalid input data and raises exception

#     :raises: AssertionError if any of the checks fails
#     """
#     try:
#         actual = guard_CRUISE_to_T2LOS_1(*input_args)
#         assert actual == expected_output, f"{description}: expected {expected_output}, got {actual}"
#     except Exception as e:
#         assert type(e) == type(expected_output), f"{description}, expected {expected_output}, got {type(e)}"
#         assert str(e) == str(expected_output), f"{description}, expected {expected_output}, got {str(e)}"

import math
import pytest

def make_quat_from_yaw(yaw: float) -> Quaternion:
    """Utility to build a (x,y,z,w) quaternion for a pure yaw rotation."""
    # Assuming ROS convention: roll=pitch=0, yaw as given
    half = yaw / 2.0
    return Quaternion(x=0.0, y=0.0, z=math.sin(half), w=math.cos(half))


@pytest.mark.parametrize("agent_yaw, wp_x, wp_y, tol_rad, expected, desc", [

    # 1) Perfectly aligned (0°) → within → not_within=False
    (0.0,            1.0,     0.0,     0.1, False, "exactly east"),

    # 2) Exactly on the tolerance boundary:
    #    agent=0°, waypoint at 6° (0.1047 rad), tol=6° → error=tol → within → not_within=False
    (0.0,            math.cos(0.1047), math.sin(0.1047), 0.1047, False, "on boundary"),

    # 3) Just outside tolerance:
    #    agent=0°, waypoint at 7° (0.1222 rad), tol=6° (0.1047) → error>tol → not_within=True
    (0.0,            math.cos(0.1222), math.sin(0.1222), 0.1047, True,  "just outside"),

    # 4) Large misalignment (90°) → not_within=True
    (0.0,            0.0,     1.0,     0.1, True,  "north (90° off)"),

    # 5) Diagonal within tolerance:
    #    agent=45° (0.7854 rad), waypoint at 50° → error=5° → tol=10° → within → not_within=False
    (0.7854,         math.cos(0.8727), math.sin(0.8727), 0.1745, False, "diagonal small error"),

    # 6) Diagonal outside tolerance:
    #    agent=45°, waypoint at 100° → error=55° → tol=10° → not_within=True
    (0.7854,         math.cos(1.7453), math.sin(1.7453), 0.1745, True,  "diagonal large error"),
])
def test_is_heading_not_within_tolerance(
    agent_yaw, wp_x, wp_y, tol_rad, expected, desc
):
    # handle the invalid‐input case
    if agent_yaw is None or wp_x is None:
        args = (None, Waypoints(waypoints=[]), tol_rad)
    else:
        agent = AgentUpdate(
            pose=Pose(
                position=Point(x=0.0, y=0.0),
                orientation=make_quat_from_yaw(agent_yaw)
            )
        )
        wp = Waypoint(position=Point32(x=wp_x, y=wp_y))
        args = (agent, Waypoints(waypoints=[wp]), tol_rad)

    result = is_heading_not_within_tolerance(*args)
    assert result == expected, f"{desc}: expected {expected}, got {result}"

@pytest.mark.parametrize("agent_state, waypoints, expected_error, error_message", [

    # 1) invalid agent_state input
    (None, Waypoints(), ValueError, "is_heading_within_tolerance input state 'agent_state' not received."),
    # 2) invalid waypoints type
    (AgentUpdate(), None, ValueError, "is_heading_within_tolerance input state 'waypoints_state' not received."),
    # 3) no waypoints in waypoints object
    (AgentUpdate(), Waypoints(), ValueError, "is_heading_within_tolerance input state 'waypoints_state' does not have waypoints.")
])
def test_is_heading_not_within_tolerance_exceptions(agent_state, waypoints, expected_error, error_message):
    with pytest.raises(expected_error, match=error_message):
        is_heading_not_within_tolerance(agent_state, waypoints) 

# # TODO: THis functions implementation is yet to be completed, still needs work therefore will write more tests when completed
# @pytest.mark.parametrize("input_args, expected_output, description", [
#     (
#         (
#             AgentUpdate(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=float(10)),
#             ObstaclesUpdate(),
#             UnsafeSet(
#                 vertices=Float64MultiArray(
#                     layout=MultiArrayLayout(
#                         dim=[MultiArrayDimension(label='vertices', stride=2)]
#                     ),
#                     data=[
#                         -5.0, -5.0,  # Point 1
#                         -5.0, 5.0,   # Point 2
#                         5.0, 5.0,    # Point 3
#                         5.0, -5.0    # Point 4
#                     ]
#                 )
#             )
#         ),
#         True,
#         "agent_state shows that we are already inside the unsafe_set"
#     ),
#     # "Test Case 2: agent_state shows we are currently outside the unsafe set and within dsf"
#     # (
#     #     (
#     #         AgentUpdate(),
#     #         ObstaclesUpdate(),
#     #         UnsafeSet()
#     #     ),
#     #     True,
#     #     "agent_state shows we are currently outside the unsafe set"
#     # ),
#     # "Test Case 3: agent_state shows we are outside the unsafe set and outside the dsf"
#     # (
#     #     (
#     #         AgentUpdate(),
#     #         ObstaclesUpdate(),
#     #         UnsafeSet()
#     #     ),
#     #     False,
#     #     "agent_state shows that based on the params of the vessel we can't maneuver away from a collision with unsafe set"
#     # ),
#     # "Test Case 4: We are we are intercepting the safety_radius of a static obstacle"
# ])
# def test_guard_CRUISE_to_FB(
#     input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet],
#     expected_output: bool,
#     description: str
# ):
#     """
#     Test if guard_CRUISE_to_FB is working correctly.

#     This test verifies:
#     1. guard correctly evaluates fallback conditions
#     2. TODO: guard handles out of sync state updates and raises exceptions
#     3. TODO: guard handles invalid input data and raises exception

#     :raises: AssertionError if any of the checks fails
#     """
#     actual = guard_CRUISE_to_FB(*input_args)
#     assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

# @pytest.mark.parametrize("input_args, expected_output, description", [
#     (
#         (
#             AgentUpdate(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=float(10.0)),
#             Waypoint(position=Point32(x=1.0, y=0.0), acceptance_radius=10.0)
#         ),
#         True,
#         "agent vessel is within acceptance radius of the waypoint"
#     ),
#     (
#         (
#             AgentUpdate(pose=Pose(position=Point(x=100.0, y=100.0, z=0.0)), safety_radius=float(10.0)),
#             Waypoint(position=Point32(x=-100.0, y=-100.0), acceptance_radius=10.0)
#         ),
#         False,
#         "agent vessel is outside acceptance radius of the waypoint"
#     )
# ])
# def test_guard_CRUISE_to_WAYPOINT_REACHED(
#     input_args: Tuple[AgentUpdate, Waypoint],
#     expected_output: bool,
#     description: str
# ):
#     """
#     Test if guard_CRUISE_to_WAYPOINT_REACHED is working correctly

#     This test verifies:
#     1. guard correctly evaluates whether we are within goal_waypoint acceptance radius or not
#     2. TODO: guard handles out of sync state updates and raises exceptions
#     3: TODO: guard handles invalid input data and raises exception
#     """
#     actual = guard_CRUISE_to_WAYPOINT_REACHED(*input_args)
#     assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

# """T2LOS Guards Tests"""
# @pytest.mark.parametrize("input_args, expected_output, description", [
#     # Test Case 1: Agent heading is within error tolerance
#     (
#         (
#             AgentUpdate(
#                 pose=Pose(
#                     position=Point(x=0.0, y=0.0),
#                     orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
#                 )
#             ),
#             Waypoint(position=Point32(x=0.0, y=1.0)),
#             0.1
#         ),
#         True,
#         "agent_state heading is currently within LOS error tolerance of current waypoint"
#     ),
#     # Test Case 2: Agent heading is outside error tolerance
#     (
#         (
#             AgentUpdate(
#                 pose=Pose(
#                     position=Point(x=0.0, y=0.0),  # Use Point32 here
#                     orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
#                 )
#             ),
#             Waypoint(position=Point32(x=1.0, y=0.0)),
#             0.1
#         ),
#         False,
#         "agent_state heading is currently not within LOS error tolerance of current waypoint"
#     ),
# ])
# def test_T2LOS_to_CRUISE(
#         input_args: Tuple[AgentUpdate, Waypoint, float],
#         expected_output: bool,
#         description: str
# ):
#     """
#         Tests if guard_T2LOS is working correctly

#         This test verifies:
#         1. guard correctly evaluates whether we are able to move back to CRUISE Mode or not
#         2. TODO: guard handles out of sync state updates and raises exceptions
#         3. TODO: guard handles invalid input data and raises exception
#     """
#     actual = guard_T2LOS_to_CRUISE(*input_args)
#     assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

# @pytest.mark.parametrize("input_args, expected_output, description", [
#     # Test Case 1: agent_state shows we are already within unsafe_set
#     (
#         (
#             AgentUpdate(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=float(10)),
#             ObstaclesUpdate(),
#             UnsafeSet(
#                 vertices=Float64MultiArray(
#                     layout=MultiArrayLayout(
#                         dim=[MultiArrayDimension(label='vertices', stride=2)]
#                     ),
#                     data=[
#                         -5.0, -5.0,  # Point 1
#                         -5.0, 5.0,   # Point 2
#                         5.0, 5.0,    # Point 3
#                         5.0, -5.0    # Point 4
#                     ]
#                 )
#             )
#         ),
#         True,
#         "agent_state shows that we are already inside the unsafe_set"
#     ),
#     # Test Case 2: agent_state shows we are currently outside the unsafe set and within dsf
#     # (
#     #     (
#     #         AgentUpdate(),
#     #         ObstaclesUpdate(),
#     #         UnsafeSet()
#     #     ),
#     #     True,
#     #     "agent_state shows we are currently outside the unsafe set"
#     # ),
#     # "Test Case 3: agent_state shows we are outside the unsafe set and outside the dsf"
#     # (
#     #     (
#     #         AgentUpdate(),
#     #         ObstaclesUpdate(),
#     #         UnsafeSet()
#     #     ),
#     #     False,
#     #     "agent_state shows that based on the params of the vessel we can't maneuver away from a collision with unsafe set"
#     # ),
#     # "Test Case 4: We are we are intercepting the safety_radius of a static obstacle"
# ])
# def test_T2LOS_to_FB(
#     input_args: Tuple[AgentUpdate, Waypoint, ObstaclesUpdate, UnsafeSet],
#     expected_output: bool,
#     description: str
# ):
#     """
#     Tests if guard_T2LOS is working correctly

#     This test verifies:
#     1. guard correctly evaluates whether we are able to move back to CRUISE Mode or not
#     2. TODO: guard handles out of sync state updates and raises exceptions
#     3. TODO: guard handles invalid input data and raises exception
#     """
#     actual = guard_T2LOS_to_FB(*input_args)
#     assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

# """WAYPOINT_REACHED Guards Tests"""
# @pytest.mark.parametrize("input_args, expected_output, description", [
#     (
#         Waypoints(waypoints=[  # input_args
#             Waypoint(position=Point32(x=0.0, y=0.0, z=0.0), acceptance_radius=0.0),
#             Waypoint(position=Point32(x=1.0, y=1.0, z=0.0), acceptance_radius=0.0)
#         ]),
#         True,
#         "More than one waypoint signifying virtual waypoints exist therefore transition should occur"
#     ),
#     (
#         Waypoints(waypoints=[  # input_args
#             Waypoint(position=Point32(x=0.0, y=0.0, z=0.0), acceptance_radius=0.0)
#         ]),
#         False,
#         "One waypoint signifying we have arrived at the goal waypoint, therefore transition should not occur"
#     ),
# ])
# def test_WAYPOINT_REACHED_to_CRUISE(input_args, expected_output, description):
#     """
#     test if WAYPOINT_REACHED_TO_CRUISE guard is working correctly

#     This test verifies: 
#     1. The function returns expected outputs for valid params
#     2. The function handles Exceptions correctly

#     :raises: AssertionError if any of the checks fails
#     """
#     actual = guard_WAYPOINT_REACHED_to_CRUISE(input_args)
#     assert actual == expected_output, f'Test: "{description}" failed, expected {expected_output}, got {actual}'
