# !/usr/bin/env python3
""" 
Test Suite for Dynamics class

This class contains both a Wrapper for a Dynamics ACI (Automaton Compoennt Interface)
and a registry for storing and providing utilities for easier interface with the hyraut_ros2
models you define
"""


import pytest
import math
from typing import Dict

from hybraut_models.core.dynamics import DynamicsWrapper, DynamicsRegistry
from geometry_msgs.msg import Twist, Vector3, PoseStamped
from hybraut_aci import DynamicsInterface, IOSpec


class SimpleVelocityController(DynamicsInterface):
    
    """
    A mock Velocity controller implementing the DynamicsInterface, 
    It simply drives toward waypoint with constant speed.
    """
    
    _dynamic_output_type = Twist
    _init_input_spec = [
        IOSpec.create_io_spec('speed', float)
    ]
    _state_input_spec = [
        IOSpec.create_io_spec('current_pose', PoseStamped),
        IOSpec.create_io_spec('goal_pose', PoseStamped)
    ]

    def _evaluate(self, **state_kwargs) -> Twist:
        cur_pose = state_kwargs['current_pose'].pose
        goal_pose = state_kwargs['goal_pose'].pose

        # Compute heading difference
        dx = goal_pose.position.x - cur_pose.position.x
        dy = goal_pose.position.y - cur_pose.position.y
        target_heading = math.atan2(dy, dx)

        # Convert current orientation (quaternion) to yaw
        q = cur_pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        current_heading = math.atan2(siny_cosp, cosy_cosp)

        # Angular velocity = shortest heading difference
        heading_error = math.atan2(
            math.sin(target_heading - current_heading),
            math.cos(target_heading - current_heading)
        )

        twist_msg = Twist(
            linear=Vector3(x=self.speed, y=0.0, z=0.0),
            angular=Vector3(x=0.0, y=0.0, z=heading_error)
        )

        return twist_msg
    
@pytest.fixture
def mock_initialization_cfg(): 
    """
    A mock of initialization configuration for dynamics wrapper mock, 
    utilited within tests!
    """
    yield {"speed": 10.0}    

@pytest.fixture
def mock_dynamics_wrapper(mock_initialization_cfg):
    """
    A fixture for the mock DynamicsWrapper which can be utilized for 
    testing
    """
    mock_dynamic_wrapper = DynamicsWrapper(
        name="simple_velocity_controller_mock",
        component_class=SimpleVelocityController,
        configuration=mock_initialization_cfg,
        output_topic="/cmd_vel",
        output_msg_type=PoseStamped
    )
    yield mock_dynamic_wrapper
        


class TestDynamicsWrapper: 
    """ 
    Test Suite for `hybraut_models.core.dynamics.dynamics_wrapper`
    
    this is a key component of a hybraut_model, it is a wrapper function utilized 
    by hybraut models for encapsulating hybraut aci instances, it provides functionality 
    for retrieving metadata, and performing evaluations, this test class is primarly utilized for ensuring
    these functionalities work as expected.
    """
    
    
    def test_dynamic_wrapper_initialization_and_attributes(self, mock_dynamics_wrapper: DynamicsWrapper, mock_initialization_cfg: Dict[str, any]):
        """ 
        tests if dynamics wrapper instance in the fixture initializes as expected and tests the access
        modifiers to ensure that the initialization and state configurations are assigned to the instance
        corretly as well as initialization configuration initialized correctly
        """
        assert "simple_velocity_controller_mock" == mock_dynamics_wrapper.get_dynamic_name()
        assert mock_dynamics_wrapper.get_initialization_configuration() == mock_initialization_cfg
        assert mock_dynamics_wrapper.get_output_msg_type() == PoseStamped
        assert mock_dynamics_wrapper.get_output_topic() == "/cmd_vel"
        
        initialization_configuration_names_and_types = mock_dynamics_wrapper.get_initialization_configuration()
        assert initialization_configuration_names_and_types == {'speed': 10.0}
        
        state_configuration_names_and_types = mock_dynamics_wrapper.get_state_configuration_names_and_types()
        
        assert list(state_configuration_names_and_types.keys()) == ["current_pose", "goal_pose"]
        assert list(state_configuration_names_and_types.values()) == [PoseStamped, PoseStamped] 
        
    # TODO: Need to complete the evaluation for dynamics
    def test_evaluate_dynamics(self, mock_dynamics_wrapper: DynamicsWrapper):
        """
        perform some simple tests on how the dynamics wrapper evaluation function operates
        """
        assert True
        
    def test_string_and_repr_representations(self, mock_dynamics_wrapper: DynamicsWrapper):
        """
        Test the string and repr representation of a dynamics wrapper instance
        """        
        
        assert str(mock_dynamics_wrapper) == "DynamicsWrapper(name=simple_velocity_controller_mock, class=SimpleVelocityController, output_topic=/cmd_vel, initialized=True)", \
            f"str '__str__' representation not as expected."
        assert repr(mock_dynamics_wrapper) == "<DynamicsWrapper name='simple_velocity_controller_mock', class=SimpleVelocityController, output_topic='/cmd_vel', output_msg_type=PoseStamped, initialized=True>", \
            f"repr '__repr__' representation not as expected."
        

    


class TestDynamicRegistry:
    """ 
    Test Suite for the 'hybraut_models.core.dynamics.dynamics_registry'
    this dynamics registry is a key component of the hybraut_model.
    
    it stores several instances of dynamic wrapper and provide a simple 
    interface for classes utilizing it through providing access modifiers and 
    utility functions for evaluations, retrieving dynamics and so on.
    
    This test suite ensures the mvp functionlity of this class currently
    """
    
    def test_dynamics_registry_initialize_and_attributes(self):
        assert True
        
    
    @pytest.mark.parametrize(
        (),
        [
            
        ],
        ids=[]
    )
    def test_get_dynamics_by_names(self):
        ...
        
        
    @pytest.mark.parametrize(
        (),
        [
            
        ],
        ids=[]
    )
    def test_get_dynamic_by_name(self):
        ... 
        

    @pytest.mark.parametrize(
        (),
        [
            
        ],
        ids=[]
    )
    def test_dynamic_evaluations():
        ...
        
        
    def test_string_representations(self):
        ...


if __name__ == "__main__":
    pytest.main([__file__])
