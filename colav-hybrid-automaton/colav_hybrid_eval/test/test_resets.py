# #!/usr/bin/python3
# """
# Unit Test Suite for COLAV Hybrid Automaton Guard Conditions.

# This module contains unit tests to validate the behavior of individual guard condition functions 
# used in the COLAV Hybrid Automaton. Both standard and edge cases are tested to ensure full coverage 
# and confirm the expected functionality of each guard.

# :author: Ryan McKee  
# :date: April 11, 2025
# """

# import pytest

# from colav_interfaces.msg import Waypoint
# from geometry_msgs.msg import Point32

# from scripts.resets import (
#     reset_WAYPOINT_REACHED_to_CRUISE,
#     reset_CRUISE_to_T2LOS
# )
# from typing import List

# @pytest.mark.parametrize("input_arg, expected_length, expected_waypoint, description", [
#     (
#         [ # input_args
#             Waypoint(), 
#             Waypoint(position=Point32(x=float(100) ,y=float(20),z=float(0)), acceptance_radius = float(10))
#         ],
#         float(1),
#         Waypoint(position=Point32(x=float(100) ,y=float(20),z=float(0)), acceptance_radius = float(10)),
#         "Reset with list containing 1 virtual waypoint"
#     )
# ])
# def test_reset_WAYPOINT_REACHED_to_CRUISE(input_arg: List[Waypoint], expected_length: float, expected_waypoint: Waypoint, description: str):
    

# @pytest.mark.parametrize("input_args, expected_output, description", [
#     ()
# ])
# def test_reset_CRUISE_to_T2LOS():
#     pass

