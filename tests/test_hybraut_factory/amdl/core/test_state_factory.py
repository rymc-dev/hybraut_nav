# !/usr/bin/env python3
"""
Test Suite for the State Factory
"""

from hybraut_factory.amdl.core.state_factory import StateFactory
import pytest
from hybraut_models.core.states import State, StateRegistry
from typing import Dict


@pytest.fixture
def sample_state_name_and_cfg():
    return (
        "twist_state",
        {
            "topic": "/state/twist",
            "description": "Twist of the agent including linear and angular velocity.",
            "type": {"pkg": "geometry_msgs.msg", "msg": "Twist"},
            "params": {"update_hz": 10.0, "timeout_sec": 0.5},
        },
    )


@pytest.fixture
def sample_state_amdl():
    return {
        "pose_state": {
            "topic": "/state/pose",
            "description": "Pose of the agent including position and orientation.",
            "type": {"pkg": "geometry_msgs.msg", "msg": "Pose"},
            "params": {"update_hz": 10.0, "timeout_sec": 0.5},
        },
        "twist_state": {
            "topic": "/state/twist",
            "description": "Twist of the agent including linear and angular velocity.",
            "type": {"pkg": "geometry_msgs.msg", "msg": "Twist"},
            "params": {"update_hz": 10.0, "timeout_sec": 0.5},
        },
    }


def test_load_state_from_amdl(sample_state_name_and_cfg):
    state_name, state_cfg = sample_state_name_and_cfg
    state = StateFactory.load_state_from_amdl(state_name, state_cfg)
    assert state._name == state_name
    assert state._topic == state_cfg["topic"]
    from geometry_msgs.msg import Vector3

    # assert state._msg_type == Vector3
    assert state._update_hz == state_cfg["params"]["update_hz"]
    assert state._timeout_sec == state_cfg["params"]["timeout_sec"]


def test_register_state_from_amdl(sample_state_amdl):
    amdl = sample_state_amdl
    states: Dict[str, State] = StateFactory.register_states_from_amdl(amdl)

    assert len(states) == len(amdl)

    for state_key, state_conf in states.items():
        assert state_key in amdl
        assert state_conf._name == state_key
        assert state_conf._topic == amdl[state_key]["topic"]
        assert state_conf._update_hz == amdl[state_key]["params"]["update_hz"]
        assert state_conf._timeout_sec == amdl[state_key]["params"]["timeout_sec"]


def test_load_state_registry_from_amdl(sample_state_amdl):
    amdl = sample_state_amdl
    registry = StateFactory.load_state_registry_from_amdl(amdl)

    assert registry is not None
    assert isinstance(registry, StateRegistry)
    assert registry.get_num_states() == len(amdl)

    for state_key, state_conf in amdl.items():
        state = registry.get_component(state_key)
        assert state is not None
        assert state._name == state_key
        assert state._topic == amdl[state_key]["topic"]
        assert state._update_hz == amdl[state_key]["params"]["update_hz"]
        assert state._timeout_sec == amdl[state_key]["params"]["timeout_sec"]


if __name__ == "__main__":
    pytest.main([__file__])
