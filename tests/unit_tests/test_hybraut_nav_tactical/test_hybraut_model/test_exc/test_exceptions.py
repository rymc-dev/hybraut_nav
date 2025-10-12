# test_exceptions.py
import pytest
from hybraut_models.exc import EvaluationException, NoneStateError, StateTimeoutException


def test_evaluation_exception_message_and_expression():
    exc = EvaluationException("Test error", expression="x + y")
    assert str(exc) == "Test error"
    assert exc.expression == "x + y"

    exc_no_expr = EvaluationException("Another error")
    assert str(exc_no_expr) == "Another error"
    assert exc_no_expr.expression is None


def test_none_state_error_message_and_state_name():
    state_name = "velocity"
    exc = NoneStateError(state_name)
    assert str(exc) == f"State '{state_name}' is not defined or has no value."
    assert exc.state_name == state_name


def test_state_timeout_exception_message_and_state_name():
    state_name = "position"
    exc = StateTimeoutException(state_name)
    assert str(exc) == f"State '{state_name}' timed out."
    assert exc.state_name == state_name


if __name__ == '__main__':
    pytest.main([__file__])
