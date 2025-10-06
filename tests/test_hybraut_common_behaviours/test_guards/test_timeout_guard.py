# """
# Unit tests for the TimeoutGuard class, which checks if a timeout has occurred
# based on the provided start time and timeout duration.
# """

# import time
# import pytest
# from hybraut_common_behaviours.guards import TimeoutGuard


# @pytest.mark.parametrize(
#     "timeout_sec, elapsed_sec, expected",
#     [
#         (3.0, 0.0, False),  # Not timed out
#         (3.0, 2.9, False),  # Just before timeout
#         (3.0, 3.0, True),  # Exactly at timeout
#         (3.0, 5.0, True),  # After timeout
#     ],
# )
# def test_timeout_guard(timeout_sec, elapsed_sec, expected):
#     start_time = time.time()
#     guard = TimeoutGuard(timeout_sec=timeout_sec, start_time_sec=start_time)
#     current_time = start_time + elapsed_sec
#     assert guard(current_time_sec=current_time) == expected


# if __name__ == "__main__":
#     pytest.main([__file__])
