from hybraut_common_behaviours.invariants import FailingInvariant
from hybraut_aci import InvariantInterface
import pytest


def test_failing_invariant() -> None:
    """Test that FailingInvariant always evaluates to False."""
    invariant: InvariantInterface = FailingInvariant()
    assert not invariant(), "FailingInvariant should always return False"


if __name__ == "__main__":
    # Allow running directly for quick check (optional)
    pytest.main([__file__])
