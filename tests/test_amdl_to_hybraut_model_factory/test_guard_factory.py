# TODO: This class tests needs to be finished.

""" """

import pytest
from amdl_to_hybraut_model_factory.guard_factory import GuardFactory
from hybraut_model.guards import GuardWrapper, GuardRegistry
from typing import Dict


@pytest.fixture
def sample_guard_name_and_conf():
    """fixture with a sample guard name and guard configuration"""
    return (
        "boolean_flag_guard",
        {
            "module": "hybraut_common_behaviours.guards",
            "class_name": "BooleanFlagGuard",
            "configuration": {"expected_flag": True},
        },
    )


@pytest.fixture
def sample_guard_amdl():
    """fixture with a sample guard amdl
    this guard amdl links to hybraut_common_behaviour guards"""
    return {
        "boolean_flag_guard": {
            "module": "hybraut_common_behaviours.guards",
            "class_name": "BooleanFlagGuard",
            "configuration": {"expected_flag": True},
        },
        "timeout_guard": {
            "module": "hybraut_common_behaviours.guards",
            "class_name": "TimeoutGuard",
            "configuration": {"timeout_sec": 5.0, "start_time_sec": 0.0},
        },
    }


def test_load_guard_from_amdl(sample_guard_name_and_conf):
    """test the load_guard_from_amdl method"""
    guard_name, guard_cfg = sample_guard_name_and_conf
    guard: GuardWrapper = GuardFactory.load_guard_from_amdl(guard_name, guard_cfg)

    assert guard._name == guard_name
    assert guard._configuration == guard_cfg["configuration"]


def test_register_transitions_from_amdl(sample_guard_amdl):
    """test the register_transitions_from_amdl method"""
    guards: Dict[str, GuardWrapper] = GuardFactory.register_transitions_from_amdl(
        sample_guard_amdl
    )

    assert len(guards) == len(sample_guard_amdl)
    for name, guard in guards.items():
        assert name == guard._name
        assert guard._configuration == sample_guard_amdl[name]["configuration"]


def test_load_guards_registry_from_amdl(sample_guard_amdl):
    """test the laod_guards_registry_from_amdl"""
    amdl = sample_guard_amdl
    registry: GuardRegistry = GuardFactory.load_guards_registry_from_amdl(amdl)

    assert registry.get_num_guards() == len(amdl)


if __name__ == "__main__":
    pytest.main([__file__])
