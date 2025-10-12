import pytest
from hybraut_nav_controller.controller import Controller 
from geometry_msgs.msg import Twist
from colav_interfaces.msg import AgentState
from hybraut_nav_controller import ControllerNode
from unittest.mock import MagicMock
from types import SimpleNamespace

class MockController(Controller):
    def __init__(self):
        self.agent_state = None
    
    def update_state(self, *args, **kwargs):
        self.agent_state = AgentState()

    def step(self) -> Twist:
        cmd = Twist()
        cmd.linear.x = 0.5  # Move forward at 0.5 m/s
        cmd.angular.z = 0.1  # Rotate at 0.1 rad/s
        return cmd
    
@pytest.fixture
def mock_controller_node():
    yield object.__new__(ControllerNode)

def test_continous_dynamics_cb_valid_msg(mock_controller_node: ControllerNode):
    """Test continous_dynamics_cb with valid ContinousDynamics message."""
    from hybraut_interfaces.msg import ContinousDynamics 
    from geometry_msgs.msg import Pose
    
    mock_controller_node.get_parameter = MagicMock(
        side_effect=lambda name: SimpleNamespace(value="FiniteTimeController")
        if name == "controller_type"
        else SimpleNamespace(value=None)
    )
    msg = ContinousDynamics()
    msg.controller_name = "FiniteTimeController"
    msg.desired_heading = 1.0
    msg.desired_velocity = 0.5
    msg.target_waypoint = Pose()
    msg.heading_tolerance = 0.1
    msg.velocity_tolerance = 0.05
    
    try: 
        mock_controller_node.continous_dynamics_cb(msg)
    except Exception as e: 
        pytest.fail(f"continous_dynamics_cb raised an exception: {e}")
    
    assert mock_controller_node.get_parameter('controller_type').value == "FiniteTimeController"
    assert mock_controller_node.desired_heading == 1.0
    assert mock_controller_node.desired_velocity == 0.5
    assert mock_controller_node.target_waypoint == msg.target_waypoint
    assert mock_controller_node.heading_tolerance == 0.1
    assert mock_controller_node.velocity_tolerance == 0.05
    
def test_continous_dynamics_cb_valid_path_different_controller_type(mock_controller_node: ControllerNode):
    """Test continous_dynamics_cb with valid ContinousDynamics message but different controller type."""
    from hybraut_interfaces.msg import ContinousDynamics 
    from geometry_msgs.msg import Pose
    
    mock_controller_node.get_parameter = MagicMock(
        side_effect=lambda name: SimpleNamespace(value="SomeOtherController")
        if name == "controller_type"
        else SimpleNamespace(value=None)
    )
    # Mock set_parameters to update controller_type from the Parameter list
    def mock_set_parameters(params):
        for p in params:
            if p.name == "controller_type":
                mock_controller_node.controller_type = p.value
        return True  # mimic rclpy’s success return
    
    mock_controller_node.set_parameters = MagicMock(side_effect=mock_set_parameters)
    
    msg = ContinousDynamics()
    msg.controller_name = "FiniteTimeController"
    msg.desired_heading = 1.0
    msg.desired_velocity = 0.5
    msg.target_waypoint = Pose()
    msg.heading_tolerance = 0.1
    msg.velocity_tolerance = 0.05
    
    try: 
        mock_controller_node.continous_dynamics_cb(msg)
    except Exception as e: 
        pytest.fail(f"continous_dynamics_cb raised an exception: {e}")
    
    assert mock_controller_node.get_parameter('controller_type').value == "SomeOtherController"
    assert mock_controller_node.desired_heading is None
    assert mock_controller_node.desired_velocity is None
    assert mock_controller_node.target_waypoint is None
    assert mock_controller_node.heading_tolerance is None
    assert mock_controller_node.velocity_tolerance is None


# def test_agent_state_cb_valid_path(mock_controller_node: ControllerNode):
#     """Test agent_state_cb with valid AgentState message."""
#     msg = AgentState()
    
#     try: 
#         mock_controller_node.agent_state_cb(msg)
#     except Exception as e: 
#         raise e
    
#     assert mock_controller_node

if __name__ == '__main__':
    pytest.main([__file__])