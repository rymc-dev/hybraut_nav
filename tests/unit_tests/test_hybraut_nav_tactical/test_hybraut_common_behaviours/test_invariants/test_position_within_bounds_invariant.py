# # test_position_within_bounds_invariant.py
# # Unit tests for PositionWithinBoundsInvariant from hybraut_common_behaviours.invariants.
# # Verifies that positions are correctly identified as within or outside specified bounds.

# from hybraut_common_behaviours.invariants import PositionWithinBoundsInvariant
# from geometry_msgs.msg import PoseStamped
# import pytest


# @pytest.mark.parametrize(
#     "x, y, expected",
#     [
#         (5.0, 7.0, True),  # within bounds
#         (0.0, 0.0, True),  # on lower bound
#         (10.0, 10.0, True),  # on upper bound
#         (15.0, 12.0, False),  # outside bounds
#         (-1.0, 5.0, False),  # x below min
#         (5.0, -1.0, False),  # y below min
#         (11.0, 5.0, False),  # x above max
#         (5.0, 11.0, False),  # y above max
#     ],
# )
# def test_position_within_bounds_invariant(x, y, expected):
#     invariant = PositionWithinBoundsInvariant(
#         x_min=0.0, x_max=10.0, y_min=0.0, y_max=10.0
#     )
#     pose_msg = PoseStamped()
#     pose_msg.pose.position.x = x
#     pose_msg.pose.position.y = y
#     result = invariant(pose=pose_msg)
#     assert result is expected


# if __name__ == "__main__":
#     pytest.main([__file__])
