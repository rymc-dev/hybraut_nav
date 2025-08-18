from hybraut_common_behaviours.invariants import TimeoutInvariant
import pytest
import time
from std_msgs.msg import Float64


def test_timeout_invariant():
    # Create an instance of TimeoutInvariant with a timeout of 1 second
    entry = time.time()
    invariant = TimeoutInvariant(timeout_sec=1.0, entry_time=entry)

    # Simulate current time just after entry
    current = Float64(data=entry + 0.5)  # 0.5 seconds later
    assert (
        invariant(current_time=current) is True
    ), "Invariant should hold within timeout"
    # Simulate current time after timeout expires
    current = Float64(data=entry + 1.5)  # 1.5 seconds later
    assert (
        invariant(current_time=current) is False
    ), "Invariant should not hold after timeout"


def test_timeout_invariant_edge_case():
    # Create an instance of TimeoutInvariant with a timeout of 2 seconds
    entry = time.time()
    invariant = TimeoutInvariant(timeout_sec=2.0, entry_time=entry)

    # Simulate current time exactly at the timeout limit
    current = Float64(data=entry + 2.0)  # Exactly 2 seconds later
    assert (
        invariant(current_time=current) is True
    ), "Invariant should hold at the exact timeout limit"

    # Simulate current time just after the timeout limit
    current = Float64(data=entry + 2.1)  # Just over 2 seconds later
    assert (
        invariant(current_time=current) is False
    ), "Invariant should not hold just after the timeout limit"


if __name__ == "__main__":
    pytest.main([__file__])
