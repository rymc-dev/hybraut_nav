import pytest
from builtin_interfaces.msg import Time, Duration
from hybraut_models.ctx import EvaluationContext

class MockStates:
    """Mock object to simulate states behavior."""

    def __init__(self):
        self.current = {"s1": 10, "s2": 20}
        self.components = {"s1": "comp1", "s2": "comp2"}
        self.times = {"s1": Time(sec=5, nanosec=100), "s2": Time(sec=7, nanosec=500)}

    def get_current_states(self, state_names):
        return {name: self.current[name] for name in state_names}

    def get_components_by_names(self, state_names):
        return {name: self.components[name] for name in state_names}

    def get_state_time(self, state_name):
        return self.times[state_name]

@pytest.fixture
def eval_context():
    states = MockStates()
    stamp = Time(sec=10, nanosec=200)
    metadata = {"event_history": ["event1", "event2"]}
    return EvaluationContext(
        states=states,
        current_mode=1,
        stamp=stamp,
        metadata=metadata,
        guard_registry=None,
        reset_registry=None,
        invariant_registry=None
    )

def test_get_state_values(eval_context):
    result = eval_context.get_state_values(["s1"])
    assert result == {"s1": 10}

def test_get_states(eval_context):
    result = eval_context.get_states(["s2"])
    assert result == {"s2": "comp2"}

def test_get_state_age(eval_context):
    age = eval_context.get_state_age("s1")
    assert isinstance(age, Duration)
    assert age.sec == 5
    assert age.nanosec == 100

def test_get_event_history(eval_context):
    history = eval_context.get_event_history()
    assert history == ["event1", "event2"]


if __name__ == '__main__':
    pytest.main([__file__])