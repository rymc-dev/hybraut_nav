# """
# Test suite for BooleanFlagGuard in hybraut_common_behaviours.
# """

# import pytest
# from hybraut_common_behaviours.guards import BooleanFlagGuard
# from std_msgs.msg import Bool


# @pytest.mark.parametrize(
#     "expected_flag, input_data, expected_result",
#     [
#         (True, True, True),
#         (True, False, False),
#         (False, False, True),
#         (False, True, False),
#     ],
# )
# def test_boolean_flag_guard(expected_flag, input_data, expected_result):
#     guard = BooleanFlagGuard(expected_flag=expected_flag)
#     assert guard(flag_msg=Bool(data=input_data)) is expected_result


# if __name__ == "__main__":
#     pytest.main([__file__])
