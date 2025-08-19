# !/usr/bin/env python3
"""
Test Suite for the dynamics factory
"""

from hybraut_factory.amdl.core.dynamics_factory import DynamicsFactory
import pytest
from hybraut_models.core.dynamics import DynamicsWrapper, DynamicsRegistry
from typing import Dict


@pytest.fixture
def sample_dynamics_name_and_cfg():
    """
    a fixture containing an individual dynamic controller
    name and configuration.
    """
    return (
        "pid_controller",
        {
            "module": "hybraut_common_behaviours.dynamics",
            "class_name": "PIDControllerDynamics",
            "configuration": {
                "control_frequency": 100,
                "max_velocity": 30.0,
                "derivative_filter_alpha": 0.1,
                "integral_max": 0.2,
                "target_velocity": 25.0,  # updated cruise speed
                "yaw_kp": 0.3,  # gentle heading proportional gain
                "yaw_ki": 0.01,  # small integral for smooth correction
                "yaw_kd": 0.05,  # small derivative gain to damp oscillations
                "vel_kp": 0.5,  # moderate velocity proportional gain
                "vel_ki": 0.05,  # small integral to avoid windup
                "vel_kd": 0.05,  # small derivative for smooth velocity changes
                "error_tolerance": 0.01,  # precision in heading error
                "max_yaw_rate": 0.1,  # limit yaw rate to gentle turns
            },
            "output": {
                "topic": "/cmd_vel",
                "type": {"pkg": "geometry_msgs.msg", "msg": "Twist"},
            },
        },
    )


@pytest.fixture
def sample_dynamics_controllers_amdl():
    """
    A fixture containing a full amdl for dynamics
    """
    return {
        "pid_controller": {
            "module": "hybraut_common_behaviours.dynamics",
            "class_name": "PIDControllerDynamics",
            "configuration": {
                "control_frequency": 100,
                "max_velocity": 30.0,
                "derivative_filter_alpha": 0.1,
                "integral_max": 0.2,
                "target_velocity": 25.0,  # updated cruise speed
                "yaw_kp": 0.3,  # gentle heading proportional gain
                "yaw_ki": 0.01,  # small integral for smooth correction
                "yaw_kd": 0.05,  # small derivative gain to damp oscillations
                "vel_kp": 0.5,  # moderate velocity proportional gain
                "vel_ki": 0.05,  # small integral to avoid windup
                "vel_kd": 0.05,  # small derivative for smooth velocity changes
                "error_tolerance": 0.01,  # precision in heading error
                "max_yaw_rate": 0.1,  # limit yaw rate to gentle turns
            },
            "output": {
                "topic": "/cmd_vel",
                "type": {"pkg": "geometry_msgs.msg", "msg": "Twist"},
            },
        }
    }


def test_load_dynamics_from_amdl(sample_dynamics_name_and_cfg):
    """tests loading an individual dynamics into a wrapper"""
    dynamics_name, dynamics_cfg = sample_dynamics_name_and_cfg
    dynamics: DynamicsWrapper = DynamicsFactory.load_dynamics_from_amdl(
        dynamics_name, dynamics_cfg
    )

    assert dynamics is not None and isinstance(dynamics, DynamicsWrapper)
    assert dynamics._name == "pid_controller"
    assert dynamics._configuration == dynamics_cfg["configuration"]


def test_register_dynamics_from_amdl(sample_dynamics_controllers_amdl):
    """tests registering dynamics from amdl into a list of dynamics"""
    amdl = sample_dynamics_controllers_amdl
    dynamics_list: Dict[str, DynamicsWrapper] = (
        DynamicsFactory.register_dynamics_from_amdl(amdl)
    )

    assert [key in dynamics_list.keys() for key in amdl.keys()]

    for _, dynamic_wrapper in dynamics_list.items():
        assert isinstance(dynamic_wrapper, DynamicsWrapper)
        assert (
            dynamic_wrapper._configuration
            == amdl[dynamic_wrapper._name]["configuration"]
        )


def test_load_dynamics_registry_from_amdl(sample_dynamics_controllers_amdl):
    """tests loading the dynamics registry from amdl"""
    amdl = sample_dynamics_controllers_amdl
    registry: DynamicsRegistry = DynamicsFactory.load_dynamics_registry_from_amdl(amdl)

    assert isinstance(registry, DynamicsRegistry)
    assert registry.get_num_dynamics() == len(amdl)


if __name__ == "__main__":
    pytest.main([__file__])
