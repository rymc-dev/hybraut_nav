from hybraut_common_behaviours.invariants import TrivialInvariant
import pytest


def test_trivial_invariant():
    # Create an instance of TrivialInvariant
    invariant = TrivialInvariant()

    # Check that the invariant is always satisfied
    assert invariant() is True


if __name__ == "__main__":
    pytest.main([__file__])
