"""
Test Suite for the hybraut_model EvaluationContext
"""

import pytest
from hybraut_models.ctx import EvaluationContext


class DummyStatesRegistry:
    def __init__(self):
        self.state_values = {"x": 10, "y": 20}
        self.states = {"x": {"value": 10}, "y": {"value": 20}}
        self.ages = {"x": 1.5, "y": 2.0}

    def get_current_states_by_state_names(self, state_names):
        return {name: self.state_values[name] for name in state_names}

    def get_states_by_name(self, state_names):
        return {name: self.states[name] for name in state_names}

    def get_state_age_by_state_name(self, state_name):
        return self.ages[state_name]


class TestEvaluationContext:
    @pytest.fixture
    def ctx(self):
        return EvaluationContext(
            current_mode=1,
            stamp=123.45,
            metadata={"event_history": ["evt1", "evt2"]},
            mode_registry=None,
            transition_registry=None,
            states_registry=DummyStatesRegistry(),
            guard_registry=None,
            reset_registry=None,
            invariant_registry=None,
        )

    def test_get_state_values(self, ctx):
        values = ctx.get_state_values(["x", "y"])
        assert values == {"x": 10, "y": 20}

    def test_get_states(self, ctx):
        states = ctx.get_states(["x"])
        assert states == {"x": {"value": 10}}

    def test_get_state_age(self, ctx):
        age = ctx.get_state_age("y")
        assert age == 2.0

    def test_get_event_history(self, ctx):
        history = ctx.get_event_history()
        assert history == ["evt1", "evt2"]

    def test_empty_event_history(self):
        ctx = EvaluationContext(
            current_mode=0,
            stamp=0.0,
            metadata={},  # no event_history
            mode_registry=None,
            transition_registry=None,
            states_registry=DummyStatesRegistry(),
            guard_registry=None,
            reset_registry=None,
            invariant_registry=None,
        )
        assert ctx.get_event_history() == []


if __name__ == "__main__":
    pytest.main([__file__])
