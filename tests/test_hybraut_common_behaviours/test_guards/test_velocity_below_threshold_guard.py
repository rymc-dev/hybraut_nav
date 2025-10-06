# # test_velocity_below_threshold_guard.py
# # Unit tests for VelocityBelowThresholdGuard in hybraut_common_behaviours.guards.
# # Verifies that the guard correctly identifies when the velocity is below a specified threshold.

# import pytest
# from geometry_msgs.msg import TwistStamped
# from hybraut_common_behaviours.guards import VelocityBelowThresholdGuard


# def make_twist(linear_x: float, linear_y: float = 0.0) -> TwistStamped:
#     """Helper to create a TwistStamped with given linear velocity."""
#     msg = TwistStamped()
#     msg.twist.linear.x = linear_x
#     msg.twist.linear.y = linear_y
#     return msg


# @pytest.mark.parametrize(
#     "linear_x, expected",
#     [
#         (0.5, True),  # speed 0.5 < 1.0 → True
#         (1.0, False),  # speed 1.0 == threshold → False
#         (1.5, False),  # speed 1.5 > threshold → False
#         (-0.5, True),  # abs(-0.5) = 0.5 < 1.0 → True
#     ],
# )
# def test_velocity_below_threshold_guard(linear_x, expected):
#     guard = VelocityBelowThresholdGuard(min_velocity=1.0)
#     msg = make_twist(linear_x)
#     assert guard(velocity=msg) is expected


# if __name__ == "__main__":
#     pytest.main([__file__])
