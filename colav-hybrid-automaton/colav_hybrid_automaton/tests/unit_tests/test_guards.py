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
    guard_CRUISE_to_FB,
    guard_CRUISE_to_T2LOS_1,
    guard_CRUISE_to_T2LOS_2,
    guard_CRUISE_to_WAYPOINT_REACHED,
    guard_T2LOS_to_CRUISE,
    guard_T2LOS_to_FB,
    guard_WAYPOINT_REACHED_to_CRUISE,
)
from hybrid_automaton.utils.validate_timestamps import get_current_ros_time


"""CRUISE Guards Tests"""
@pytest.mark.parametrize("input_args, expected_output, description", [
    # Test Case 1: unsafe_set on los and within distance threshold
    (
        (
            AgentUpdate(
                header=Header(stamp=get_current_ros_time()),
                pose=Pose(
                    position=Point(
                        x=float(400),
                        y=float(100)
                    )
                ),
                velocity=float(10)
            ),
            ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
            UnsafeSet(
                header=Header(stamp=get_current_ros_time()),
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        300.0, 100.0,  # Point 1
                        350.0, 150.0,  # Point 2
                        400.0, 150.0,  # Point 3
                        400.0, 100.0   # Point 4
                    ]
                )
            ),
            Waypoint(
                position=Point32(x=float(500), y=float(100))
            ),
            float(float(50))
        ),
        True,
        "unsafe set on los within distance threshold"
    ),
    # Test Case 2: unsafe_set on los but outside distance threshold
    (
        (
            AgentUpdate(
                header=Header(stamp=get_current_ros_time()),
                pose=Pose(
                    position=Point(
                        x=float(100),
                        y=float(100)
                    )
                ),
                velocity=float(10)
            ),
            ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
            UnsafeSet(
                header=Header(stamp=get_current_ros_time()),
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        300.0, 100.0,  # Point 1
                        350.0, 150.0,  # Point 2
                        400.0, 150.0,  # Point 3
                        400.0, 100.0   # Point 4
                    ]
                )
            ),
            Waypoint(
                position=Point32(x=float(500), y=float(100))
            ),
            float(float(50))
        ),
        False,
        "unsafe_set on los but outside distance threshold"
    ),
    # Test Case 3: Unsafe set within distance threshold but not on los
    (
        (
            AgentUpdate(
                header=Header(stamp=get_current_ros_time()),
                pose=Pose(
                    position=Point(
                        x=float(100),
                        y=float(100)
                    )
                ),
                velocity=float(10)
            ),
            ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
            UnsafeSet(
                header=Header(stamp=get_current_ros_time()),
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        250.0, 130.0,  # Point 1
                        260.0, 130.0,  # Point 2
                        260.0, 140.0,  # Point 3
                        250.0, 140.0   # Point 4
                    ]
                )
            ),
            Waypoint(
                position=Point32(x=float(500), y=float(100))
            ),
            float(50)
        ),
        False,
        "unsafe set within distance threshold but not on los"
    ),
    # Test Case 4: unsafe set outside distance threshold off line of sight
    (
        (
            AgentUpdate(
                header=Header(stamp=get_current_ros_time()),
                pose=Pose(
                    position=Point(
                        x=float(100),
                        y=float(100)
                    )
                ),
                velocity=float(10)
            ),
            ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
            UnsafeSet(
                header=Header(stamp=get_current_ros_time()),
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        300.0, 300.0,  # Point 1
                        310.0, 300.0,  # Point 2
                        310.0, 310.0,  # Point 3
                        300.0, 310.0   # Point 4
                    ]
                )
            ),
            Waypoint(
                position=Point32(x=float(500), y=float(100))
            ),
            float(50)
        ),
        False,
        "unsafe set outside distance threshold off line of sight"
    ),
    # # Test Case 5: static obstacle on los within distance threshold
    # (
    #     (),
    #     True,
    #     'Static obstacle on los within distance threshold'
    # ),
    # # Test Case 6: static obstacle on los but not within distance threshold
    # (
    #     (),
    #     False,
    #     'static obstacle on los but not within distance threshold'
    # ),
    # # Test Case 7: static obstacle within distance threshold not on los
    # (
    #     (),
    #     False,
    #     "static within distance threshold not on los"
    # ),
    # # Test Case 8: static obstacle outside distance threshold outside line of sight
    # (
    #     (),
    #     False,
    #     "static obstacle outside distance threshold outside line of sight"
    # )
    # Test Case 9: agent_update out of sync
    (
        (
            AgentUpdate(header=Header(stamp=Time(sec=0, nanosec=0))),
            ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
            UnsafeSet(header=Header(stamp=get_current_ros_time())),
            Waypoint(),
            float(50)
        ),
        TimeoutError('Timeout Exception occured'),
        "Timeout error was not thrown for ObstaclesUpdate"
    ),
    # Test Case 20: obstacle_update out of sync
    (
        (
            AgentUpdate(header=Header(stamp=get_current_ros_time())),
            ObstaclesUpdate(header=Header(stamp=Time(sec=1, nanosec=0))),
            UnsafeSet(header=Header(stamp=get_current_ros_time())),
            Waypoint(),
            float(50)
        ),
        TimeoutError('Timeout Exception occured'),
        "Timeout error was not thrown for ObstaclesUpdate"
    ),
    # Test Case 11: unsafe_set out of sync
    (
        (
            AgentUpdate(header=Header(stamp=get_current_ros_time())),
            ObstaclesUpdate(header=Header(stamp=get_current_ros_time())),
            UnsafeSet(header=Header(stamp=Time(sec=0, nanosec=0))),
            Waypoint(),
            float(50)
        ),
        TimeoutError('Timeout Exception occured'),
        "Timeout error was not thrown for ObstaclesUpdate"
    ),
])
def test_guard_CRUISE_to_T2LOS_1(
    input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, float],
    expected_output: Union[bool, Exception],
    description: str
):
    """   
    Test if the guard_CRUISE_to_T2Theta is working correctly.

    This test verifies:
    1. guard correctly evaluates unsafe set scenarios and returns expected transition evaluation
    2. TODO: guard correctly evaluates static obstacles scenarios and returns expected transition evaluation
    3. guard handles out of sync state updates and raises exception
    4. TODO: guard handles invalid input data and raises exception

    :raises: AssertionError if any of the checks fails
    """
    try:
        actual = guard_CRUISE_to_T2LOS_1(*input_args)
        assert actual == expected_output, f"{description}: expected {expected_output}, got {actual}"
    except Exception as e:
        assert type(e) == type(expected_output), f"{description}, expected {expected_output}, got {type(e)}"
        assert str(e) == str(expected_output), f"{description}, expected {expected_output}, got {str(e)}"

@pytest.mark.parametrize("input_args, expected_output, description", [
    # Test Case 1: Agent heading is not within error tolerance
    (
        (
            AgentUpdate(
                pose=Pose(
                    position=Point(x=0.0, y=0.0),  # Use Point32 here
                    orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
                )
            ),
            Waypoint(position=Point32(x=1.0, y=0.0)), 0.1),
        True,
        "agent_state heading is currently not within LOS error tolerance of current waypoint"
    ),
    # Test Case 2: Agent heading is within error tolerance
    (
        (AgentUpdate(
            pose=Pose(
                position=Point(x=0.0, y=0.0),  # Use Point32 here
                orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
            )
        ),
        Waypoint(position=Point32(x=0.0, y=1.0)), 0.1),  # Use Point32 here too
        False,
        "agent_state heading is current within LOS error tolerance of current waypoint"
    )
])
def test_guard_CRUISE_to_T2LOS_2(input_args: Tuple[AgentUpdate, Waypoint, float], expected_output, description):
    """
    Test if guard_CRUISE_to_T2LOS is working correctly.

    This test verifies:
    1. guard correctly evaluates agent heading error in relation to waypoint
    2. TODO: guard handles out of sync state updates and raises exceptions
    3. TODO: guard handles invalid input data and raises exception

    :raises: AssertionError if any of the checks fails
    """
    result = guard_CRUISE_to_T2LOS_2(*input_args)
    assert result == expected_output, description

# TODO: THis functions implementation is yet to be completed, still needs work therefore will write more tests when completed
@pytest.mark.parametrize("input_args, expected_output, description", [
    (
        (
            AgentUpdate(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=float(10)),
            ObstaclesUpdate(),
            UnsafeSet(
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        -5.0, -5.0,  # Point 1
                        -5.0, 5.0,   # Point 2
                        5.0, 5.0,    # Point 3
                        5.0, -5.0    # Point 4
                    ]
                )
            )
        ),
        True,
        "agent_state shows that we are already inside the unsafe_set"
    ),
    # "Test Case 2: agent_state shows we are currently outside the unsafe set and within dsf"
    # (
    #     (
    #         AgentUpdate(),
    #         ObstaclesUpdate(),
    #         UnsafeSet()
    #     ),
    #     True,
    #     "agent_state shows we are currently outside the unsafe set"
    # ),
    # "Test Case 3: agent_state shows we are outside the unsafe set and outside the dsf"
    # (
    #     (
    #         AgentUpdate(),
    #         ObstaclesUpdate(),
    #         UnsafeSet()
    #     ),
    #     False,
    #     "agent_state shows that based on the params of the vessel we can't maneuver away from a collision with unsafe set"
    # ),
    # "Test Case 4: We are we are intercepting the safety_radius of a static obstacle"
])
def test_guard_CRUISE_to_FB(
    input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet],
    expected_output: bool,
    description: str
):
    """
    Test if guard_CRUISE_to_FB is working correctly.

    This test verifies:
    1. guard correctly evaluates fallback conditions
    2. TODO: guard handles out of sync state updates and raises exceptions
    3. TODO: guard handles invalid input data and raises exception

    :raises: AssertionError if any of the checks fails
    """
    actual = guard_CRUISE_to_FB(*input_args)
    assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

@pytest.mark.parametrize("input_args, expected_output, description", [
    (
        (
            AgentUpdate(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=float(10.0)),
            Waypoint(position=Point32(x=1.0, y=0.0), acceptance_radius=10.0)
        ),
        True,
        "agent vessel is within acceptance radius of the waypoint"
    ),
    (
        (
            AgentUpdate(pose=Pose(position=Point(x=100.0, y=100.0, z=0.0)), safety_radius=float(10.0)),
            Waypoint(position=Point32(x=-100.0, y=-100.0), acceptance_radius=10.0)
        ),
        False,
        "agent vessel is outside acceptance radius of the waypoint"
    )
])
def test_guard_CRUISE_to_WAYPOINT_REACHED(
    input_args: Tuple[AgentUpdate, Waypoint],
    expected_output: bool,
    description: str
):
    """
    Test if guard_CRUISE_to_WAYPOINT_REACHED is working correctly

    This test verifies:
    1. guard correctly evaluates whether we are within goal_waypoint acceptance radius or not
    2. TODO: guard handles out of sync state updates and raises exceptions
    3: TODO: guard handles invalid input data and raises exception
    """
    actual = guard_CRUISE_to_WAYPOINT_REACHED(*input_args)
    assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

"""T2LOS Guards Tests"""
@pytest.mark.parametrize("input_args, expected_output, description", [
    # Test Case 1: Agent heading is within error tolerance
    (
        (
            AgentUpdate(
                pose=Pose(
                    position=Point(x=0.0, y=0.0),
                    orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
                )
            ),
            Waypoint(position=Point32(x=0.0, y=1.0)),
            0.1
        ),
        True,
        "agent_state heading is currently within LOS error tolerance of current waypoint"
    ),
    # Test Case 2: Agent heading is outside error tolerance
    (
        (
            AgentUpdate(
                pose=Pose(
                    position=Point(x=0.0, y=0.0),  # Use Point32 here
                    orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
                )
            ),
            Waypoint(position=Point32(x=1.0, y=0.0)),
            0.1
        ),
        False,
        "agent_state heading is currently not within LOS error tolerance of current waypoint"
    ),
])
def test_T2LOS_to_CRUISE(
        input_args: Tuple[AgentUpdate, Waypoint, float],
        expected_output: bool,
        description: str
):
    """
        Tests if guard_T2LOS is working correctly

        This test verifies:
        1. guard correctly evaluates whether we are able to move back to CRUISE Mode or not
        2. TODO: guard handles out of sync state updates and raises exceptions
        3. TODO: guard handles invalid input data and raises exception
    """
    actual = guard_T2LOS_to_CRUISE(*input_args)
    assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

@pytest.mark.parametrize("input_args, expected_output, description", [
    # Test Case 1: agent_state shows we are already within unsafe_set
    (
        (
            AgentUpdate(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0)), safety_radius=float(10)),
            ObstaclesUpdate(),
            UnsafeSet(
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        -5.0, -5.0,  # Point 1
                        -5.0, 5.0,   # Point 2
                        5.0, 5.0,    # Point 3
                        5.0, -5.0    # Point 4
                    ]
                )
            )
        ),
        True,
        "agent_state shows that we are already inside the unsafe_set"
    ),
    # Test Case 2: agent_state shows we are currently outside the unsafe set and within dsf
    # (
    #     (
    #         AgentUpdate(),
    #         ObstaclesUpdate(),
    #         UnsafeSet()
    #     ),
    #     True,
    #     "agent_state shows we are currently outside the unsafe set"
    # ),
    # "Test Case 3: agent_state shows we are outside the unsafe set and outside the dsf"
    # (
    #     (
    #         AgentUpdate(),
    #         ObstaclesUpdate(),
    #         UnsafeSet()
    #     ),
    #     False,
    #     "agent_state shows that based on the params of the vessel we can't maneuver away from a collision with unsafe set"
    # ),
    # "Test Case 4: We are we are intercepting the safety_radius of a static obstacle"
])
def test_T2LOS_to_FB(
    input_args: Tuple[AgentUpdate, Waypoint, ObstaclesUpdate, UnsafeSet],
    expected_output: bool,
    description: str
):
    """
    Tests if guard_T2LOS is working correctly

    This test verifies:
    1. guard correctly evaluates whether we are able to move back to CRUISE Mode or not
    2. TODO: guard handles out of sync state updates and raises exceptions
    3. TODO: guard handles invalid input data and raises exception
    """
    actual = guard_T2LOS_to_FB(*input_args)
    assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

"""WAYPOINT_REACHED Guards Tests"""
@pytest.mark.parametrize("input_args, expected_output, description", [
    (
        Waypoints(waypoints=[  # input_args
            Waypoint(position=Point32(x=0.0, y=0.0, z=0.0), acceptance_radius=0.0),
            Waypoint(position=Point32(x=1.0, y=1.0, z=0.0), acceptance_radius=0.0)
        ]),
        True,
        "More than one waypoint signifying virtual waypoints exist therefore transition should occur"
    ),
    (
        Waypoints(waypoints=[  # input_args
            Waypoint(position=Point32(x=0.0, y=0.0, z=0.0), acceptance_radius=0.0)
        ]),
        False,
        "One waypoint signifying we have arrived at the goal waypoint, therefore transition should not occur"
    ),
])
def test_WAYPOINT_REACHED_to_CRUISE(input_args, expected_output, description):
    """
    test if WAYPOINT_REACHED_TO_CRUISE guard is working correctly

    This test verifies: 
    1. The function returns expected outputs for valid params
    2. The function handles Exceptions correctly

    :raises: AssertionError if any of the checks fails
    """
    actual = guard_WAYPOINT_REACHED_to_CRUISE(input_args)
    assert actual == expected_output, f'Test: "{description}" failed, expected {expected_output}, got {actual}'
