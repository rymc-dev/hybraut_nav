from hybraut_common_behaviours.guards import TimeoutGuard
import pytest


def test_timeout_guard():
    import time

    timeout_guard = TimeoutGuard(timeout_sec=3.0, start_time_sec=time.time())
    current_time = time.time()
    assert not timeout_guard(current_time_sec=current_time)
    current_time += 5.0
    assert timeout_guard(current_time_sec=current_time)


if __name__ == "__main__":
    pytest.main([__file__])
