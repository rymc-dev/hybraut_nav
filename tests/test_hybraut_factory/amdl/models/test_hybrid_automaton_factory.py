# !/usr/bin/env python3
"""
test suite for the hybrid automaton factory
"""

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

from unittest.mock import Mock, MagicMock
import pytest


@pytest.fixture
def mock_dynamics_factory_generation(): ...


@pytest.fixture
def mock_guard_factory_generation(): ...


@pytest.fixture
def mock_invariants_factory_generation(): ...


@pytest.fixture
def mock_mode_factory_generation(): ...


@pytest.fixture
def mock_reset_factory_generation(): ...


@pytest.fixture
def mock_state_factory_generation(): ...


@pytest.fixture
def mock_transition_factory_generation(): ...


class TestHybridAutomatonFactory: ...


if __name__ == "__main__":
    pytest.main([__file__])
