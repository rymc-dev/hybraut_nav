#!/usr/bin/env python3
"""
Test suite for the HybridAutomatonFactory
(using monkeypatched factory functions).
"""

import pytest
from unittest.mock import MagicMock
from _pytest.monkeypatch import MonkeyPatch

from hybraut_factory.amdl.models.hybrid_automaton_factory import HybridAutomatonFactory
from hybraut_factory.amdl.core import (
    DynamicsFactory,
    StateFactory,
    GuardFactory,
    InvariantFactory,
    ModeFactory,
    ResetFactory,
    TransitionFactory,
)

# Registries
from hybraut_models import HybridAutomaton
from hybraut_models.core.dynamics import DynamicsRegistry
from hybraut_models.core.states import StateRegistry
from hybraut_models.core.guards import GuardRegistry
from hybraut_models.core.resets import ResetRegistry
from hybraut_models.core.invariants import InvariantRegistry
from hybraut_models.core.modes import ModeRegistry
from hybraut_models.core.transitions import TransitionRegistry


# ---------------------------------------------------------------------------
# Mock factory helpers (can be used as pytest fixtures or called manually)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_dynamics_factory_generation(monkeypatch):
    fake_registry = DynamicsRegistry()
    fake_dynamics = MagicMock(name="Dynamics")
    fake_registry._components = {"dynamic_1": fake_dynamics}
    monkeypatch.setattr(
        DynamicsFactory,
        "load_dynamics_registry_from_amdl",
        MagicMock(return_value=fake_registry),
    )
    return fake_registry


@pytest.fixture
def mock_guard_factory_generation(monkeypatch):
    fake_registry = GuardRegistry()
    fake_guard = MagicMock(name="Guard")
    fake_registry._components = {"guard1": fake_guard}
    monkeypatch.setattr(
        GuardFactory,
        "load_guards_registry_from_amdl",
        MagicMock(return_value=fake_registry),
    )
    return fake_registry


@pytest.fixture
def mock_invariants_factory_generation(monkeypatch):
    fake_registry = InvariantRegistry()
    fake_invariant = MagicMock(name="Invariant")
    fake_registry._components = {"invariant1": fake_invariant}
    monkeypatch.setattr(
        InvariantFactory,
        "load_invariant_registry_from_amdl",
        MagicMock(return_value=fake_registry),
    )
    return fake_registry


@pytest.fixture
def mock_mode_factory_generation(monkeypatch):
    fake_mode_1 = MagicMock(name="Mode1")
    fake_mode_2 = MagicMock(name="Mode2")
    fake_registry = ModeRegistry(_modes={0: fake_mode_1, 1: fake_mode_2})
    monkeypatch.setattr(
        ModeFactory,
        "load_modes_registry_from_amdl",
        MagicMock(return_value=fake_registry),
    )
    return fake_registry


@pytest.fixture
def mock_reset_factory_generation(monkeypatch):
    fake_registry = ResetRegistry()
    fake_reset = MagicMock(name="Reset")
    fake_registry._components = {"reset1": fake_reset}
    monkeypatch.setattr(
        ResetFactory,
        "load_reset_registry_from_amdl",
        MagicMock(return_value=fake_registry),
    )
    return fake_registry


@pytest.fixture
def mock_state_factory_generation(monkeypatch):
    fake_registry = StateRegistry()
    fake_state = MagicMock(name="State")
    fake_registry._components = {"state1": fake_state}
    monkeypatch.setattr(
        StateFactory,
        "load_state_registry_from_amdl",
        MagicMock(return_value=fake_registry),
    )
    return fake_registry

@pytest.fixture
def mock_transition_factory_generation(monkeypatch):
    fake_registry = TransitionRegistry()
    fake_transition = MagicMock(name="Transition")
    fake_registry._components = {"transition1": fake_transition}
    monkeypatch.setattr(
        TransitionFactory,
        "load_transition_registry_from_amdl",
        MagicMock(return_value=fake_registry),
    )
    return fake_registry




# ---------------------------------------------------------------------------
# Example test class (pytest style)
# ---------------------------------------------------------------------------

class TestHybridAutomatonFactory:

    def test_register_automaton(
            self,
            mock_state_factory_generation,
            mock_dynamics_factory_generation,
            mock_reset_factory_generation,
            mock_guard_factory_generation,
            mock_invariants_factory_generation,
            mock_transition_factory_generation,
            mock_mode_factory_generation
    ):
        """ 
        test the registration of the automaton
        """

        minimal_amdl = {
            "automaton_name": "TestAutomaton",
            "automaton_description": "A minimal test automaton",
            "version": "0.1",

            # Required by constructor
            "initial_mode": 0,
            "goal_modes": [1],

            # Each of these needs to exist but can be empty dicts
            "states": {},
            "guards": {},
            "resets": {},
            "dynamics": {},
            "invariants": {},
            "transitions": {},
            "modes": {}
        }

        hybrid_automaton: HybridAutomaton = HybridAutomatonFactory.register_automaton(
            minimal_amdl
        )

        assert isinstance(hybrid_automaton, HybridAutomaton)
        assert hybrid_automaton._name == minimal_amdl['automaton_name']
        assert hybrid_automaton._description == minimal_amdl['automaton_description']
        assert hybrid_automaton._version == minimal_amdl['version']
        assert hybrid_automaton._initial_mode == minimal_amdl['initial_mode']
        assert hybrid_automaton._goal_modes == minimal_amdl['goal_modes']

        assert hybrid_automaton._states == mock_state_factory_generation
        assert hybrid_automaton._dynamics == mock_dynamics_factory_generation
        assert hybrid_automaton._guards == mock_guard_factory_generation 
        assert hybrid_automaton._resets == mock_reset_factory_generation
        assert hybrid_automaton._invariants == mock_invariants_factory_generation
        assert hybrid_automaton._modes == mock_mode_factory_generation
        assert hybrid_automaton._transitions == mock_transition_factory_generation



# ---------------------------------------------------------------------------
# Manual run (no pytest required)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    pytest.main([__file__])