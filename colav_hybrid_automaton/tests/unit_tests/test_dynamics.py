# #!/usr/bin/python3
# """
# Unit Test Suite for COLAV Hybrid Automaton Dynamics.

# This module contains unit tests to validate the behavior of individual Dynamic functions
# used in the COLAV Hybrid Automaton. Both standard and edge cases are tested to ensure full coverage
# and confirm the expected functionality of each guard.

# :author: Ryan McKee
# :date: April 15, 2025
# """

# # TODO: NEED TO VALIDATE TOLERANCE DURATION ISINSTANCE 'Duration'

# import pytest
# from typing import Tuple, Optional, Type

# from std_msgs.msg import Header
# from geometry_msgs.msg import Point32
# from builtin_interfaces.msg import Time

# from colav_interfaces.msg import AgentUpdate, Dynamics, Waypoint

# from hybrid_automaton.scripts.dynamics import (
#     dynamics_CRUISE,
#     dynamics_T2LOS,
#     dynamics_FALLBACK,
#     dynamics_WAYPOINT_REACHED
# )

# from hybrid_automaton.utils import get_current_ros_time

# TARGET_VELOCITY = 25 * 0.514444

# @pytest.mark.parametrize(
#     "input_args, expected, exception_cls, exception_msg, description",
#     [
#         # 1. bad agent_state
#         (
#             (None, 1.0),
#             None,
#             ValueError,
#             "agent state received is of none type not type AgentUpdate",
#             "reject non-AgentUpdate agent_state"
#         ),
#         # 2. bad dt type
#         (
#             (AgentUpdate(), None),
#             None,
#             ValueError,
#             "delta time must be type float",
#             "reject non-float dt"
#         ),
#         # 3. dt too small
#         (
#             (AgentUpdate(), 0.001),
#             None,
#             ValueError,
#             "delta time must be greater than or equal to 0.01",
#             "reject dt < 0.01"
#         ),
#         # 4. timestamp too old
#         (
#             (AgentUpdate(header=Header(stamp=Time(sec=0, nanosec=0))), 1.0),
#             None,
#             TimeoutError,
#             "timeout occurred in dynamics cruise",
#             "timeout on out-of-sync timestamp"
#         ),
#         # 5. invalid duration
#         (
#             (AgentUpdate(header=Header(stamp=get_current_ros_time()), velocity=10.0), 0.5, None),
#             None,
#             ValueError,
#             "tolerance must be Duration type",
#             "reject not-Duration tolerance"
#         ),
#         # 6. valid input
#         (
#             (AgentUpdate(header=Header(stamp=get_current_ros_time()), velocity=10.0), 0.5),
#             Dynamics(velocity=10.5),  # or whatever the correct expected value is
#             None,
#             None,
#             "happy path: should accelerate toward TARGET_VELOCITY"
#         ),
#         (
#             (AgentUpdate(header=Header(stamp=get_current_ros_time()), velocity=10.0), 1.0),
#             Dynamics(velocity=11.0),  # or whatever the correct expected value is
#             None,
#             None,
#             "happy path: should accelerate toward TARGET_VELOCITY"
#         ),
#         (
#             (AgentUpdate(header=Header(stamp=get_current_ros_time()), velocity=11.0), 2.0),
#             Dynamics(velocity=TARGET_VELOCITY),  # or whatever the correct expected value is
#             None,
#             None,
#             "happy path: should max out at TARGET_VELOCITY"
#         ),
#         # TODO: Test: how controller deals with inertia and previous acceleration 
#     ],
# )
# def test_dynamics_CRUISE(
#     input_args: Tuple[AgentUpdate, float],
#     expected: Optional[Dynamics],
#     exception_cls: Optional[Type[Exception]],
#     exception_msg: Optional[str],
#     description: str
# ):
#     """
#     Test if dynamics_CRUISE is working correctly

#     This test verifies:
#     1. input args are correctly validated and correct excpetions are returned
#     2. CRUISE dynamics are returned as expected from the controller

#     :raises: AssertionError if any of the checks fails
#     """
#     if exception_cls is None:
#         # no exception expected
#         result = dynamics_CRUISE(*input_args)
#         assert result == expected,\
#             f"{description}: expected {expected}, got {result}"
#     else:
#         # exception expected
#         with pytest.raises(exception_cls) as excinfo:
#             dynamics_CRUISE(*input_args)
#         assert str(excinfo.value) == exception_msg, (
#             f"{description}: expected message {exception_msg!r}, "
#             f"got {str(excinfo.value)!r}"
#         )

# @pytest.mark.parametrize(
#     "input_args, expected, exception_cls, exception_msg, description", [
#     # Test Case 1: Bad agent state
#     (
#         (
#             None,
#             Waypoint(),
#             0.1,
#             0.001,
#             0.1
#         ),
#         None,
#         ValueError,
#         "agent state received is of none type not type AgentUpdate",
#         "reject non-AgentUpdate agent_state"
#     ),
#     # Test Case 2: Bad Waypoint: TODO: THIS IS FAILING FOR SOME REASON BEYOND ME
#     (
#         (
#             AgentUpdate(),
#             None,
#             0.1,
#             0.001,
#             0.1
#         ),
#         None,
#         ValueError,
#         "waypoint not an instance of Waypoint",
#         "reject non-Waypoint waypoint"
#     ), 
#     # Test case 3: bad delta time
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             None,
#             0.001,
#             0.1
#         ),
#         None,
#         ValueError,
#         "delta time must be type float",
#         "reject non-float dt"
#     ), 
#     # Test case 4: delta time too small
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.001,
#             0.001,
#             0.1
#         ),
#         None,
#         ValueError,
#         "delta time must be greater than or equal to 0.01",
#         "reject dt < 0.01"
#     ),
#     # Test case 5: bad error tolerance
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.5,
#             None,
#             0.1
#         ),
#         None,
#         ValueError,
#         "Heading error tolerance invalid, should be type float",
#         "reject non-float error_tolerance"
#     ),
#     # Test case 6: heading error tolerance too low
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.5,
#             0.0001,
#             0.1
#         ),
#         None,
#         ValueError,
#         "Heading error tolerance invalid, should be greater than or equal to 0.001",
#         "reject error_tolerance <  0.001"
#     ), 
#     # Test case 7: bad proportional gain
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.5,
#             0.1,
#             None
#         ),
#         None,
#         ValueError,
#         "proportional gain must be type float",
#         "reject non-float proportional_gain"
#     ),
#     # Test case 8: invalid proportional gain > 10
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.5,
#             0.1,
#             11.0
#         ),
#         None,
#         ValueError,
#         "proportional gain must be greater than 0 and less than 10",
#         "reject proportional_gain > 10"
#     ),
#     # Test case 9: invalid proportional gain <= 0.0
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.5,
#             0.1,
#             -0.1
#         ),
#         None,
#         ValueError,
#         "proportional gain must be greater than 0 and less than 10",
#         "reject proportional_gain > 10"
#     ),
#     #Test Case 10: tolerance must be Duration type
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.5,
#             0.1,
#             9.0,
#             None
#         ),
#         None,
#         ValueError,
#         "tolerance must be Duration type",
#         "reject non-Duration tolerance"
#     ),
#     # Test case 11: out of sync agentUpdate
#     (
#         (
#             AgentUpdate(),
#             Waypoint(),
#             0.5,
#             0.1,
#             0.1
#         ),
#         None,
#         TimeoutError,
#         "timeout occurred in dynamics cruise",
#         "reject (stamp.now() - AgentUpdate.header.stamp) > tolerance "
#     ),
#     # Test 12: valid args: TODO: NEED TO FULLY VALIDATE THE OUTPUTS MANUALLY
#     (
#         (
#             AgentUpdate(yaw_rate=0.2, velocity = 10.0, header=Header(stamp=get_current_ros_time())),
#             Waypoint(position=Point32(x=400.0, y=-600.0), acceptance_radius=20.0),
#             1.0,
#             0.01,
#             1.0
#         ),
#         Dynamics(velocity=10.0, yaw_rate=-0.982793723247329),
#         None,
#         None,
#         "happy path: Should begin aligning heading with waypoint"
#     ),
# ])
# def test_dynamics_T2LOS(
#     input_args: Tuple[AgentUpdate, Waypoint, float, float, float],
#     expected: Optional[Dynamics],
#     exception_cls: Optional[Type[Exception]],
#     exception_msg: Optional[str],
#     description: str
# ):
#     """
#     Test if dynamics_T2LOS is working correctly

#     This test verifies:
#     1. input args are correctly validated and correct excpetions are returned
#     2. T2LOS dynamics are returned as expected from the controller

#     :raises: AssertionError if any of the checks fails
#     """
#     if exception_cls is None:
#         # no exception expected
#         result = dynamics_T2LOS(*input_args)
#         assert result == expected,\
#             f"{description}: expected {expected}, got {result}"
#     else:
#         # exception expected
#         with pytest.raises(exception_cls) as excinfo:
#             dynamics_T2LOS(*input_args)
#         assert str(excinfo.value) == exception_msg, (
#             f"{description}: expected message {exception_msg!r}, "
#             f"got {str(excinfo.value)!r}"
#         )

# # NOTE: FOR NOW FALLBACK MODE DYNAMICS ARE GOING TO HANDLER BY CONTROLLER ON BOAT WHICH WILL TAKE velocity=0.0, yaw_rate=0.0 which will stop the boat slowly
# def test_dynamics_FALLBACK():
#     """
#     Test if FALLBACK dynamics is working correctly

#     This test verifies:
#     1. input args are correctly validated and correct excpetions are returned
#     2. FALLBACK dynamics are returned as expected from the controller

#     :raises: AssertionError if any of the checks fails
#     """
#     assert dynamics_FALLBACK() == Dynamics(), \
#         f"Test failed: expected: {Dynamics()}, got: {dynamics_FALLBACK()}"

# # NOTE: FOR NOW WAYPOINT_REACHED DYNAMICS ARE GIONG TO BE HANDLED BY CONTROLLER ON BOAT WHICH WILL TAKE velocity=0.0, yaw_rate=0.0 which will stop the boat slowly
# def test_dynamics_WAYPOINT_REACHED():
#     """
#     Test if WAYPOINT_REACHED dynamics is working correctly

#     This test verifies:
#     1. input args are correctly validated and correct excpetions are returned
#     2. WAYPOINT_REACHED dynamics are returned as expected from the controller

#     :raises: AssertionError if any of the checks fails
#     """
#     assert dynamics_WAYPOINT_REACHED() == Dynamics(), \
#         f"Test failed: expected {Dynamics()}, got: {dynamics_WAYPOINT_REACHED()}"
