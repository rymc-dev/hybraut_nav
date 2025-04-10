import pytest
from scripts.guards import ( 
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
from geometry_msgs.msg import Pose, Point32, Quaternion, Point
from typing import Tuple
from std_msgs.msg import Float64MultiArray, MultiArrayLayout
from std_msgs.msg import MultiArrayDimension

@pytest.mark.parametrize("input_args, expected_output, description", [
    # Test Case 1: unsafe_set on los and within distance threshold
    (
        (
            AgentUpdate(
                pose=Pose(
                    position=Point(
                        x=float(400),
                        y=float(100)
                    )
                ),
                velocity=float(10)
            ),
            ObstaclesUpdate(),
            UnsafeSet(
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        300.0, 100.0,  # Point 1
                        350.0, 150.0,  # Point 2
                        400.0, 150.0,  # Point 3
                        400.0, 100.0   # Point 4
                    ]
                )
            ),
            Waypoint(
                position=Point32(x=float(500), y=float(100))
            ),
            float(float(50))
        ),
        True, 
        "unsafe set on los within distance threshold"
    ),
    # Test Case 2: unsafe_set on los but outside distance threshold
    (
        (
            AgentUpdate(
                pose=Pose(
                    position=Point(
                        x=float(100),
                        y=float(100)
                    )
                ),
                velocity=float(10)
            ),
            ObstaclesUpdate(),
            UnsafeSet(
                vertices=Float64MultiArray(
                    layout=MultiArrayLayout(
                        dim=[MultiArrayDimension(label='vertices', stride=2)]
                    ),
                    data=[
                        300.0, 100.0,  # Point 1
                        350.0, 150.0,  # Point 2
                        400.0, 150.0,  # Point 3
                        400.0, 100.0   # Point 4
                    ]
                )
            ),
            Waypoint(
                position=Point32(x=float(500), y=float(100))
            ),
            float(float(50))
        ), 
        False, 
        "unsafe_set on los but outside distance threshold"
    ),
    # ((), False, "unsafe set within distance threshold but not on los"), 
    # ((), False, "unsafe set outside distance threshold off line of sight"),
    # ((), True, 'Static obstacle on los within distance threshold'),
    # ((), False, 'static obstacle on los but not within distance threshold'),
    # ((), False, "static within distance threshold not on los"),
    # ((), False, "static obstacle outside distance threshold outside line of sight")
])
def test_guard_CRUISE_to_T2Theta(
    input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet, Waypoint, float],
    expected_output: bool,
    description: str
):
    """
        Tests to ensure that guard_CRUISE_to_T2Theta is working as expected
    """
    actual = guard_CRUISE_to_T2Theta(*input_args)  # Use proper slicing or input args
    assert actual == expected_output, f"{description}: expected {expected_output}, got {actual}"

@pytest.mark.parametrize("input_args, expected_output, description", [
    # Test Case 1: Agent heading is not within error tolerance
    (
        (
            AgentUpdate(
                pose=Pose(
                    position=Point(x=0.0, y=0.0),  # Use Point32 here
                    orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
                )
            ), 
            Waypoint(position=Point32(x=1.0, y=0.0)), 0.1), 
        True, 
        "agent_state heading is currently not within LOS error tolerance of current waypoint"
    ),
    # Test Case 2: Agent heading is within error tolerance
    (
        (AgentUpdate(
            pose=Pose(
                position=Point(x=0.0, y=0.0),  # Use Point32 here
                orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
            )
        ), 
        Waypoint(position=Point32(x=0.0, y=1.0)), 0.1),  # Use Point32 here too
        False, 
        "agent_state heading is current within LOS error tolerance of current waypoint"
    )
])
def test_guard_CRUISE_to_T2LOS(input_args: Tuple[AgentUpdate, Waypoint, float], expected_output, description):
    # Unpack input_args (AgentUpdate, Waypoint, tolerance)
    agent_state, current_waypoint, tolerance = input_args
    
    # Here you would call your guard function with these parameters
    result = guard_CRUISE_to_T2LOS(agent_state, current_waypoint, heading_error_tolerance=tolerance)
    
    # Assert that the result matches the expected output
    assert result == expected_output, description

@pytest.mark.parametrize("input_args, expected_output, description", [
    ((AgentUpdate(pose=Pose(position=Point(x=0,y=0,z=0))), ObstaclesUpdate(), UnsafeSet()), True, "agent_state shows that we are already inside the unsafe_set"),
    ((AgentUpdate(), ObstaclesUpdate(), UnsafeSet()), False, "agent_state shows we are currently outside the unsafe set"),
    ((AgentUpdate(), ObstaclesUpdate(), UnsafeSet()), False, "agent_state shows that based on the params of the vessel we can't maneuver away from a collision with unsafe set"),
])
def test_guard_CRUISE_to_FB(
    input_args: Tuple[AgentUpdate, ObstaclesUpdate, UnsafeSet],
    expected_output: bool,
    description: str
):
    """
        Tests to ensure guard_CRUISE_To_FB is working as expected
    """
    actual = guard_CRUISE_to_FB(agent_state=input_args[0], obstacles_state=input_args[1], unsafe_set=input_args[2])
    # actual = guard_CRUISE_to_FB(*input_args[0:2])
    assert actual == expected_output, f"{description}: expected {expected_output}, got: {actual}"

# def test_guard_CRUISE_to_WAYPOINT_REACHED():
#     pass

# def test_T2LOS_to_CRUISE():
#     pass

# def test_T2LOS_to_FB():
#     pass

# def test_T2Theta_to_FB():
#     pass

# def test_T2Theta_to_T2LOS():
#     pass

def main():
    pass

if __name__ == "__main__":
    main()