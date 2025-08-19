# !/usr/bin/env python3
"""
test class for mode factory
"""

import pytest
from hybraut_factory.amdl.core.mode_factory import ModeFactory


@pytest.fixture
def sample_mode_id_and_amdl():
    return (
        0,
        {
            "name": "Idle",
            "description": "The robot is idle.",
            "dynamics": "idle_dynamics",
            "invariants": ["idle_invariant"],
            "transitions": {1: "start_transition", 2: "stop_transition"},
        },
    )


@pytest.fixture
def sample_mode_amdl():
    return {
        0: {
            "name": "Idle",
            "description": "The robot is idle.",
            "dynamics": "idle_dynamics",
            "invariants": ["idle_invariant"],
            "transitions": {1: "start_transition", 2: "stop_transition"},
        },
        1: {
            "name": "Active",
            "description": "The robot is active.",
            "dynamics": "active_dynamics",
            "invariants": ["active_invariant"],
            "transitions": {0: "stop_transition", 2: "pause_transition"},
        },
    }


def test_load_mode_from_amdl(sample_mode_id_and_amdl):
    idx, mode_cfg = sample_mode_id_and_amdl
    mode = ModeFactory.load_mode_from_amdl(idx, mode_cfg)

    assert mode.get_id() == idx
    assert mode.get_name() == mode_cfg["name"]
    assert mode.get_description() == mode_cfg["description"]
    assert mode.get_dynamics_ref() == mode_cfg["dynamics"]
    assert mode.get_invariant_refs() == mode_cfg["invariants"]
    assert mode.get_transition_refs() == mode_cfg["transitions"]

    assert mode.get_entry_actions() == None
    assert mode.get_exit_actions() == None
    assert mode.get_is_goal_mode() == False


def test_load_modes_registry_from_amdl(sample_mode_amdl):
    amdl = sample_mode_amdl
    mode_registry = ModeFactory.load_modes_registry_from_amdl(amdl)

    assert mode_registry is not None
    assert mode_registry.get_num_nodes() == len(amdl.keys())

    for mode_id, mode_cfg in amdl.items():
        mode = mode_registry.get_mode(mode_id)
        assert mode is not None
        assert mode.get_id() == mode_id
        assert mode.get_name() == mode_cfg["name"]
        assert mode.get_description() == mode_cfg["description"]
        assert mode.get_dynamics_ref() == mode_cfg["dynamics"]
        assert mode.get_invariant_refs() == mode_cfg["invariants"]
        assert mode.get_transition_refs() == mode_cfg["transitions"]

        assert mode.get_entry_actions() == None
        assert mode.get_exit_actions() == None
        assert mode.get_is_goal_mode() == False


if __name__ == "__main__":
    pytest.main([__file__])
