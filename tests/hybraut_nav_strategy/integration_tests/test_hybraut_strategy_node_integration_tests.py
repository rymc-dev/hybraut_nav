""" 
Integration Tests for hybrautNav StrategyNode
"""


import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
import pytest
from hybraut_nav_strategy import StrategyNode
from hybraut_nav_strategy.path_planning import RRTStar, RRT, Dijkstra, AStar, Planner
from typing import Tuple


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
    """ 
    Integration tests for the StrategyNode.
    These tests validate the initialization and configuration of the StrategyNode's parameters, publishers, subscriptions, and services.
    """

    """ === Test node initialization of interfaces === """
     
    def test_parameter_initialization(self, strategy_node_and_mock_node_cli):
        """ 
        @test test_parameter_initialization
        @brief Test that the StrategyNode parameters are initialized to their default values.
        
        This test: 
        - Initializes the StrategyNode.
        - Asserts that each parameter is set to its expected default value.
        - Fails if any parameter does not match its default value.
        """
        strategy_node, _ = strategy_node_and_mock_node_cli
        strategy_node: StrategyNode = strategy_node
        # assert strategy_node.get_parameter('replan_frequency').value == strategy_node.DEFAULT_REPLAN_FREQUENCY, "Replan frequency parameter should be initialized to default value"
        assert strategy_node.get_parameter('planner').value == strategy_node.DEFAULT_PLANNER_TYPE, "Planner type parameter should be initialized to default value"
        # assert strategy_node.get_parameter('max_planning_time').value == strategy_node.DEFAULT_MAX_PLANNING_TIME, "Max planning time parameter should be initialized to default value"

    def test_publisher_initialization(self, strategy_node_and_mock_node_cli):
        """ 
        @test integration_test test_publisher_initialization
        @brief Test that the StrategyNode publishers are initialized correctly.

        This test: 
        - Initializes the StrategyNode.
        - Asserts that each publisher is set up with the correct topic and message type.
        - Fails if any publisher does not match its expected configuration.
        """
        
        strategy_node, _ = strategy_node_and_mock_node_cli
        strategy_node: StrategyNode = strategy_node
        from rclpy.publisher import Publisher
        assert isinstance(strategy_node._plan_pub, Publisher), "Plan publisher should be initialized as a publisher"
        assert strategy_node._plan_pub.topic_name == "/hybraut_nav/planner/plan"
        from nav_msgs.msg import Path
        assert strategy_node._plan_pub.msg_type is Path, "Plan publisher should be of type nav_msgs/Path"
        # TODO:  assert strategy_node._plan_pub.qos_profile        
        
        assert isinstance(strategy_node._goal_pose_pub, Publisher)
        assert strategy_node._goal_pose_pub.topic_name == "/hybraut_nav/planner/goal_pose"
        from geometry_msgs.msg import PoseStamped
        assert strategy_node._goal_pose_pub.msg_type is PoseStamped, "Goal pose publisher should be of type geometry_msgs/PoseStamped"  
        # TODO: Test qos profile
        
    def test_subscription_initialization(self, strategy_node_and_mock_node_cli):
        """ 
        @test integration_test test_subscription_initialization
        @brief Test that the StrategyNode subscriptions are initialized correctly.

        This test: 
        - Initializes the StrategyNode.
        - Asserts that each subscription is set up with the correct topic and message type.
        - Fails if any subscription does not match its expected configuration.
        """
        strategy_node, _ = strategy_node_and_mock_node_cli
        strategy_node: StrategyNode = strategy_node
        
        from rclpy.subscription import Subscription
        assert isinstance(strategy_node._vw_sub, Subscription), "Virtual waypoint subscription should be initialized as a subscription"
        assert strategy_node._vw_sub.topic_name == "/hybraut_nav/tactical/virtual_waypoint"
        from geometry_msgs.msg import PoseStamped
        assert strategy_node._vw_sub.msg_type is PoseStamped, "Virtual waypoint subscription should be of type geometry_msgs/PoseStamped"

        assert isinstance(strategy_node._map_sub, Subscription), "Goal subscription should be initialized as a subscription"
        assert strategy_node._map_sub.topic_name == "/map"
        from nav_msgs.msg import OccupancyGrid
        assert strategy_node._map_sub.msg_type is OccupancyGrid
                
        assert isinstance(strategy_node._agent_sub, Subscription), "Odometry subscription should be initialized as a subscription"
        assert strategy_node._agent_sub.topic_name == "/agent_state"
        from colav_interfaces.msg import AgentState
        assert strategy_node._agent_sub.msg_type is AgentState
    
    def test_service_initialization(self, strategy_node_and_mock_node_cli):
        """ 
        @test integration_test test_service_initialization
        @brief Test that the StrategyNode services are initialized correctly.

        This test: 
        - Initializes the StrategyNode.
        - Asserts that each service is set up with the correct topic and message type.
        - Fails if any service does not match its expected configuration.
        """
        
        strategy_node, _ = strategy_node_and_mock_node_cli
        strategy_node: StrategyNode = strategy_node
        from rclpy.service import Service
        assert isinstance(strategy_node._activate_srv, Service), "Activate service should be initialized as a service"
        assert strategy_node._activate_srv.service_name == "/hybraut_nav/planner/activate"
        from hybraut_interfaces.srv import SendPose
        assert strategy_node._activate_srv.srv_type is SendPose, "Activate service should be of type hybraut_interfaces/srv/SendPose" 
        # TODO: Test qos and callback type
        
        assert isinstance(strategy_node._deactivate_srv, Service), "Deactivate service should be initialized as a service"
        assert strategy_node._deactivate_srv.service_name == "/hybraut_nav/planner/deactivate"
        from std_srvs.srv import Trigger
        assert strategy_node._deactivate_srv.srv_type is Trigger, "Deactivate service should be of type std_srvs/srv/Trigger"
        # TODO: Test qos and callback type

        
    @pytest.mark.parametrize("new_value, expected_planner_cls", [
        ('RRT*', RRTStar),
        ('RRT', RRT),
        ('Dijkstra', Dijkstra),
        ('A*', AStar),
    ])
    def test_paramater_update_planner_via_cli(self, new_value: str, expected_planner_cls: Planner, strategy_node_and_mock_node_cli: Tuple[StrategyNode, Node]):
        strategy_node, cli_node = strategy_node_and_mock_node_cli

        def set_planner_param(new_value):
            from rclpy.parameter import Parameter
            from rclpy.parameter_client import AsyncParameterClient

            param_client = AsyncParameterClient(cli_node, '/hybraut_nav/strategy_node')
            future = param_client.set_parameters([Parameter('planner', Parameter.Type.STRING, new_value)])
            rclpy.spin_until_future_complete(cli_node, future, timeout_sec=5.0)
            if not future.done():
                raise TimeoutError("Setting parameter timed out.")
            return future.result()

        try:
            result = set_planner_param(new_value)
        except TimeoutError as e: 
            pytest.fail(f"Parameter update timed out: {e}")
            
        
        assert result, "Parameter update should return a success message"
        assert strategy_node.get_parameter('planner').value == new_value, "Planner type parameter should be updated to new value"
        assert isinstance(strategy_node._planner, expected_planner_cls), f"Planner instance should be of type {expected_planner_cls.__name__}"
        
    def test_parameter_update_planner_via_cli_invalid_values(self, strategy_node_and_mock_node_cli): 
        ... 
        
    
        

    # def test_timer_initialization(self):
    #     pass
    
    # def test_get_replan_frequency(self):
    #     pass
    
    # def test_get_planner(self):
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