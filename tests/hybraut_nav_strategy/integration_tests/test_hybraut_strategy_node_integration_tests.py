""" 
Integration Tests for hybrautNav StrategyNode
"""


import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
import pytest
from hybraut_nav_strategy import StrategyNode


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
    node = StrategyNode()
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
def strategy_node_and_mock_node_cli(strategy_node, mock_node_cli):
    """ 
    Fixture to create a MultiThreadedExecutor and spin the StrategyNode and mock_node_cli.
    Yields the executor, strategy_node, and mock_node_cli for use in tests.
    """
    executor = MultiThreadedExecutor()
    executor.add_node(strategy_node)
    executor.add_node(mock_node_cli)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    
    yield strategy_node, mock_node_cli
    
    executor.shutdown()
    thread.join()

    
@pytest.mark.usefixtures("strategy_node_and_mock_node_cli")
class TestStrategyNodeIntegration: 
    def test_parameter_initialization(self, strategy_node_and_mock_node_cli):
        strategy_node, _ = strategy_node_and_mock_node_cli
        strategy_node: StrategyNode = strategy_node
        assert strategy_node.get_parameter('replan_frequency').value == strategy_node.DEFAULT_REPLAN_FREQUENCY, "Replan frequency parameter should be initialized to default value"
        assert strategy_node.get_parameter('planner_type').value == strategy_node.DEFAULT_PLANNER_TYPE, "Planner type parameter should be initialized to default value"
        assert strategy_node.get_parameter('max_planning_time').value == strategy_node.DEFAULT_MAX_PLANNING_TIME, "Max planning time parameter should be initialized to default value"


    def test_publisher_initialization(self, strategy_node):
        strategy_node, _ = strategy_node_and_mock_node_cli
        strategy_node: StrategyNode = strategy_node
        from rclpy.publisher import Publisher
        assert isinstance(strategy_node.__plan_pub, Publisher), "Plan publisher should be initialized as a publisher"
        assert 

    # def test_service_initialization(self):
    #     pass

    # def test_subscription_initialization(self):
    #     pass


    # def test_timer_initialization(self):
    #     pass
    
    # def test_get_replan_frequency(self):
    #     pass
    
    # def test_get_planner_type(self):
    #     pass 
    
    # def test_get_max_planning_time(self): 
    #     pass 
    
    # def test_get_description(self): 
    #     pass 
    
    # def test_get_state(self): 
    #     pass 
    
    # def test_set_planner(self): 
    #     pass 
    
    # def test_set_replan_frequency(self):
    #     pass 
    
    # def test_set_max_planning_time(self):
    #     pass 
    
    # def test_set_state(self): 
    #     pass 
    
    # def test_is_active(self): 
    #     pass 
    
    
    
    
    
if __name__ == '__main__':
    pytest.main([__file__])