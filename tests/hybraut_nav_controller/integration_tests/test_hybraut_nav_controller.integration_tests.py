""" 
Integration Tests for hybrautNav StrategyNode
"""


import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
import pytest
from hybraut_nav_controller import ControllerNode
from typing import Tuple
from hybraut_nav_controller.controller_node import DEFAULT_CONTROLLER_FREQUENCY, DEFAULT_CONTROLLER_TYPE

@pytest.fixture
def rclpy_fixture():
    """Initializes rclpy and shutdown cleanly after completion."""
    rclpy.init()
    yield
    rclpy.shutdown()
    
@pytest.fixture
def strategy_node(rclpy_fixture):
    """ 
    Initializes the StrategyNode for testing.
    """
    _ = rclpy_fixture  # Explicitly access to avoid unused argument warning
    node = ControllerNode()
    yield node
    node.destroy_node()

@pytest.fixture 
def mock_node_cli(rclpy_fixture):
    """ 
    creates a mock node to simulate cli interactions with the StrategyNode.
    """
    _ = rclpy_fixture  # Explicitly access to avoid unused argument warning
    node = Node('test_node')
    yield node
    node.destroy_node()
    node.destroy_node()
     
@pytest.fixture
def controller_node_and_mock_node_cli(controller_node, mock_node_cli):
    """ 
    Fixture to create a MultiThreadedExecutor and spin the ControllerNode and mock_node_cli.
    Yields the executor, controller_node, and mock_node_cli for use in tests.
    """
    executor = MultiThreadedExecutor()
    executor.add_node(controller_node)
    executor.add_node(mock_node_cli)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    
    yield controller_node, mock_node_cli
    
    executor.shutdown()
    thread.join()


class TestControllerNodeIntegration: 
    def test_parameter_initialization(self, controller_node_and_mock_node_cli: tuple[ControllerNode, Node]):
        """Test that the ControllerNode Initializes ROS2 parameters"""
        
        controller_node, _ = controller_node_and_mock_node_cli
        assert controller_node.get_parameter('controller_frequency').value == DEFAULT_CONTROLLER_FREQUENCY, "Controller Frequency parameter not initialized correctly"
        assert controller_node.get_parameter('controller_type').value ==  DEFAULT_CONTROLLER_FREQUENCY, "Controller Type parameter not initialized correctly"
        
    def test_publisher_initialization(self, controller_node_and_mock_node_cli: tuple[ControllerNode, Node]):
        """Test that the ControllerNode Initializes Publishers"""
        
        controller_node, _ = controller_node_and_mock_node_cli
        from rclpy.publisher import Publisher
        assert isinstance(controller_node.cmd_vel_pub, Publisher)
        assert controller_node.cmd_vel_pub.topic_name == '/cmd_vel'
        from geometry_msgs.msg import Twist
        assert controller_node.cmd_vel_pub.msg_type is Twist, "cmd_vel publisher message type is not Twist"
        from rclpy.qos import qos_profile_system_default
        assert controller_node.cmd_vel_pub.qos_profile is qos_profile_system_default, "cmd_vel publisher QoS profile is not system default"
        
        
    def test_subscription_initialization(self, controller_node_and_mock_node_cli: tuple[ControllerNode, Node]):
        """Test that the ControllerNode Initializes Subscribers"""
        pass 
        # controller_node, _ = controller_node_and_mock_node_cli
        # from rclpy.subscription import Subscription
        # assert isinstance(controller_node.odom_sub, Subscription)
        # assert controller_node.odom_sub.topic_name == '/odom'
        # from nav_msgs.msg import Odometry
        # assert controller_node.odom_sub.msg_type is Odometry, "odom subscriber message type is not Odometry"
        # from rclpy.qos import qos_profile_system_default
        # assert controller_node.odom_sub.qos_profile is qos_profile_system_default, "odom subscriber QoS profile is not system default"
        
    def test_service_initialization(self, controller_node_and_mock_node_cli):
        ... 
        


if __name__ == '__main__':
    pytest.main([__file__])