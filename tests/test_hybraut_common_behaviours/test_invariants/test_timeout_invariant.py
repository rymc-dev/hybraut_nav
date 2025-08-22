# test_timeout_invariant.py
# Unit tests for TimeoutInvariant from hybraut_common_behaviours.invariants.
# Tests are parameterized for various timeout scenarios.

import pytest
import time
from std_msgs.msg import Float64
from hybraut_common_behaviours.invariants import TimeoutInvariant


@pytest.mark.parametrize(
    "timeout_sec, entry_offset, expected, description",
    [
        (1.0, 0.5, True, "Invariant should hold within timeout"),
        (1.0, 1.5, False, "Invariant should not hold after timeout"),
        (2.0, 2.0, True, "Invariant should hold at the exact timeout limit"),
        (2.0, 2.1, False, "Invariant should not hold just after the timeout limit"),
    ],
)
def test_timeout_invariant_param(timeout_sec, entry_offset, expected, description):
    entry = time.time()
    invariant = TimeoutInvariant(timeout_sec=timeout_sec, entry_time=entry)
    current = Float64(data=entry + entry_offset)
    assert invariant(current_time=current) is expected, description


if __name__ == "__main__":
    pytest.main([__file__])
