from hybraut_common_behaviours.guards import BooleanFlagGuard
import pytest


def test_boolean_flag_guard():
    guard = BooleanFlagGuard(expected_flag=True)
    assert guard(flag_msg={"data": True}) is True
    assert guard(flag_msg={"data": False}) is False


if __name__ == "__main__":
    pytest.main([__file__])
