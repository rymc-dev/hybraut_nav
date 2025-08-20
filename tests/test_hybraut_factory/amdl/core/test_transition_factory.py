# !/usr/bin/env python3
"""
Unit tests for the TransitionFactory class in amdl_to_hybraut_model_factory.
These tests verify the correct loading, registration, and registry creation of transitions from AMDL configurations.
"""

import pytest
from hybraut_factory.amdl.core.transition_factory import TransitionFactory
from hybraut_models.const.urgency import UrgencyEnums


@pytest.fixture
def sample_transition_name_and_amdl():
    return (
        "transition_1",
        {
            "target_mode": 2,
            "guard": ["guard_1", "guard_2"],
            "reset": ["reset_1"],
            "urgency": UrgencyEnums.EAGER.value,  # EAGER urgency,
        },
    )


@pytest.fixture
def sample_transitions_amdl():
    return {
        "transition_1": {
            "target_mode": 2,
            "guard": ["guard_1", "guard_2"],
            "reset": ["reset_1"],
            "urgency": UrgencyEnums.EAGER.value,
        },
        "transition_2": {
            "target_mode": 3,
            "guard": ["guard_3"],
            "reset": ["reset_2", "reset_3"],
            "urgency": UrgencyEnums.LAZY.value,
        },
    }


def test_load_transition_from_amdl(sample_transition_name_and_amdl):
    transition_name, transition_amdl = sample_transition_name_and_amdl

    transition = TransitionFactory.load_transition_from_amdl(
        transition_name=transition_name, transition_amdl=transition_amdl
    )

    assert transition.get_name() == transition_name
    assert transition.get_target_mode() == transition_amdl["target_mode"]
    assert transition.get_guard_refs() == transition_amdl["guard"]
    assert transition.get_reset_refs() == transition_amdl["reset"]
    assert transition.get_urgency().value == transition_amdl["urgency"]


def test_register_transitions_from_amdl(sample_transitions_amdl):
    transition_amdl = sample_transitions_amdl
    transitions = TransitionFactory.register_transitions_from_amdl(transition_amdl)

    for transition_key, transition_cfg in transition_amdl.items():
        assert transition_key in transitions
        assert transitions[transition_key].get_name() == transition_key
        assert (
            transitions[transition_key].get_target_mode()
            == transition_cfg["target_mode"]
        )
        assert transitions[transition_key].get_guard_refs() == transition_cfg["guard"]
        assert transitions[transition_key].get_reset_refs() == transition_cfg["reset"]
        assert (
            transitions[transition_key].get_urgency().value == transition_cfg["urgency"]
        )


def test_load_transition_registry_from_amdl(sample_transitions_amdl):
    transitions_amdl = sample_transitions_amdl
    transitions_registry = TransitionFactory.load_transition_registry_from_amdl(
        transitions_amdl
    )

    transitions = transitions_registry.get_component_names()
    assert all(transition in transitions_amdl.keys() for transition in transitions)

    for transition_key, transition_cfg in transitions_amdl.items():
        transition = transitions_registry.get_component(transition_key)

        assert transition.get_name() == transition_key
        assert transition.get_target_mode() == transition_cfg["target_mode"]
        assert transition.get_guard_refs() == transition_cfg["guard"]
        assert transition.get_reset_refs() == transition_cfg["reset"]
        assert transition.get_urgency().value == transition_cfg["urgency"]


if __name__ == "__main__":
    pytest.main([__file__])
