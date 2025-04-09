import pytest
from colav_hybrid_eval.scripts.guards import (
    guard_CRUISE_to_FB,
    guard_CRUISE_to_T2LOS,
    guard_CRUISE_to_T2Theta,
    guard_CRUISE_to_WAYPOINT_REACHED,
    guard_T2LOS_to_CRUISE,
    guard_T2LOS_to_FB,
    guard_T2Theta_to_FB,
    guard_T2Theta_to_T2LOS
)
from colav_interfaces.msg import AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint
from typing import Tuple

@pytest.mark.parametrize("input_args, expected_output, description", [
    ((), True, "unsafe set on los within distance threshold"),
    ((), False, "unsafe_set on los but outside distance threshold"),
    ((), False, "unsafe set within distance threshold but not on los"), 
    ((), False, "unsafe set outside distance threshold off line of sight"),
    ((), True, 'Static obstacle on los within distance threshold'),
    ((), False, 'static obstacle on los but not within distance threshold'),
    ((), False, "static within distance threshold not on los"),
    ((), False, "static obstacle outside distance threshold outside line of sight")
])
def test_guard_CRUISE_to_T2Theta(
    input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint],
    expected_output: bool,
    test_description: str
):
    """
        Tests to ensure that guard_CRUISE_to_T2Theta is working as expected
    """
    actual = guard_CRUISE_to_T2Theta(*input_args[0:3])  # Use proper slicing or input args
    assert actual == expected_output, f"{test_description}: expected {expected_output}, got {actual}"

@pytest.mark.parametrize("input_args, expected_output, description", [
    ((), True, "agent_state heading is currently not within LOS error tolerance of current waypoint"),
    ((), False, "agent_state heading is current within LOS error tolerance of current waypoint"),
])
def test_guard_CRUISE_TO_T2LOS(
    input_args: Tuple[AgentUpdate, Waypoint, float],
    expected_output: bool,
    test_description: str
):
    """
        Tests to ensure guard_CRUISE_TO_T2LOS is working as expected
    """
    actual = guard_CRUISE_to_T2LOS(*input_args[0:2])
    assert actual == expected_output, f"{test_description}: expected {expected_output}, got {actual}"

@pytest.mark.parametrize("input_args, expected_output, description", [
    ((), True, "agent_state shows that we are already inside the unsafe_set"),
    ((), False, "agent_state shows we are currently outside the unsafe set"),
    ((), False, "agent_state shows that based on the params of the vessel we can't maneuver away from a collision with unsafe set"),
])
def test_guard_CRUISE_to_FB(
    input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet],
    expected_output: bool,
    test_description: str
):
    """
        Tests to ensure guard_CRUISE_To_FB is working as expected
    """
    actual = guard_CRUISE_to_FB(*input_args[0:2])
    assert actual == expected_output, f"{test_description}: expected {expected_output}, got: {actual}"

def test_guard_CRUISE_to_WAYPOINT_REACHED():
    pass

def test_T2LOS_to_CRUISE():
    pass

def test_T2LOS_to_FB():
    pass

def test_T2Theta_to_FB():
    pass

def test_T2Theta_to_T2LOS():
    pass

def main():
    pass

if __name__ == "__main__":
    main()