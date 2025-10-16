""" 
Integration Tests for hybrautNav StrategyNode
"""


import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
import pytest
from hybraut_nav_strategy import StrategyNode
from hybraut_nav_strategy.strategy_node import map_qos, world_state_qos
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

    """ === Test parameter updates Via CLI === """
        
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

        invalid_values = ['InvalidPlanner', '', '123']
        for invalid_value in invalid_values:
            try:
                result = set_planner_param(invalid_value)
                assert not result.results[-1].successful, f"Parameter update with invalid value '{invalid_value}' should fail"
                assert strategy_node.get_parameter('planner').value == strategy_node.DEFAULT_PLANNER_TYPE, "Planner type parameter should remain unchanged on invalid update"
            except TimeoutError as e:
                pytest.fail(f"Parameter update timed out for invalid value '{invalid_value}': {e}")
        
    """ === No need to test publishers === """
        
    """ === Test subscription callbacks via cli === """
        
    def test_map_callback_via_cli(self, strategy_node_and_mock_node_cli: Tuple[StrategyNode, Node]):
        from nav_msgs.msg import OccupancyGrid
        
        strategy_node, cli_node = strategy_node_and_mock_node_cli
        sample_occupancy_grid = OccupancyGrid()
        sample_occupancy_grid.header.frame_id = "map"
        sample_occupancy_grid.info.resolution = 1.0
        sample_occupancy_grid.info.width = 10
        sample_occupancy_grid.info.height = 10
        sample_occupancy_grid.info.origin.position.x = 0.0
        sample_occupancy_grid.info.origin.position.y = 0.0
        sample_occupancy_grid.data = [0] * 100  # 10x10 grid
        
        from rclpy.publisher import Publisher
        map_pub: Publisher = cli_node.create_publisher(OccupancyGrid, '/map', map_qos)
        map_pub.publish(sample_occupancy_grid)
        import time
        time.sleep(1.0)
        
        cli_node.destroy_publisher(map_pub)
        
        # Validate that the received map matches the published map
        received_map = strategy_node._map
        assert received_map is not None, "StrategyNode should have received the map data"
        from hybraut_nav_strategy.path_planning.planner import Grid as PlannerGrid
        assert isinstance(received_map, PlannerGrid) 
        assert received_map.resolution == sample_occupancy_grid.info.resolution
        assert received_map.width == sample_occupancy_grid.info.width
        assert received_map.height == sample_occupancy_grid.info.height
        assert received_map.origin[0] == sample_occupancy_grid.info.origin.position.x
        assert received_map.origin[1] == sample_occupancy_grid.info.origin.position.y
        import numpy as np
        # sample_occupancy_grid.data is a flat array('b') or list; convert to a 2D numpy array
        expected = np.array(sample_occupancy_grid.data, dtype=np.int8)
        expected = expected.reshape((sample_occupancy_grid.info.height, sample_occupancy_grid.info.width))
        # received_map.data is a 2D numpy array (PlannerGrid); compare shapes and values
        np.testing.assert_array_equal(received_map.data, expected, err_msg="OccupancyGrid data should match")

    def test_map_callback_via_cli_invalid_msg(self, strategy_node_and_mock_node_cli: Tuple[StrategyNode, Node]):
        """ 
        Test the strategy node's behavior when receiving an invalid map message via CLI.
        """
        ... 

    def test_agent_callback_via_cli(self, strategy_node_and_mock_node_cli: Tuple[StrategyNode, Node]):
        from colav_interfaces.msg import AgentState
        from geometry_msgs.msg import Pose
        strategy_node, cli_node = strategy_node_and_mock_node_cli
        
        from rclpy.publisher import Publisher 
        from geometry_msgs.msg import Point
        sample_agent_state = AgentState(pose=Pose(position=Point(x=1.0, y=2.0, z=0.0)))
        agent_state_pub: Publisher = strategy_node.create_publisher(AgentState, '/agent_state', world_state_qos)
        
        agent_state_pub.publish(sample_agent_state)
        
        import time
        time.sleep(0.1)
        strategy_node.destroy_publisher(agent_state_pub)
        assert strategy_node._start_point is not None, "StrategyNode should have updated the start point from the agent state"
        assert strategy_node._start_point.x == 1.0 and strategy_node._start_point.y == 2.0, "Start point should match the agent state position"
    
    def test_agent_callback_via_cli_invalid_msg(self, strategy_node_and_mock_node_cli):
        pass
    
    """ === Test Service Interfaces via CLI === """
    
    def test_activate_service_via_cli(self, strategy_node_and_mock_node_cli: Tuple[StrategyNode, Node]):
        strategy_node, cli_node = strategy_node_and_mock_node_cli 
        from hybraut_interfaces.srv import SendPose
        from rclpy.client import Client
        from nav_msgs.msg import OccupancyGrid
        from colav_interfaces.msg import AgentState 
        from rclpy.publisher import Publisher
        from geometry_msgs.msg import Pose, Point
        
        map_pub: Publisher = cli_node.create_publisher(OccupancyGrid, '/map', map_qos)
        agent_state_pub: Publisher = cli_node.create_publisher(AgentState, '/agent_state', world_state_qos)
        
        from rclpy.subscription import Subscription
        
        plan = []
        plan_sub: Subscription = cli_node.create_subscription(
            topic='/hybraut_nav/planner/plan',
            msg_type=OccupancyGrid,
            callback=lambda msg: plan.append(msg),
            qos_profile=world_state_qos # prob should change this to map qos? 
        )
        
        sample_occupancy_grid = OccupancyGrid()
        sample_occupancy_grid.header.frame_id = "map"
        sample_occupancy_grid.info.resolution = 1.0
        sample_occupancy_grid.info.width = 10
        sample_occupancy_grid.info.height = 10
        sample_occupancy_grid.info.origin.position.x = 0.0
        sample_occupancy_grid.info.origin.position.y = 0.0
        sample_occupancy_grid.data = [0] * 100  # 10x10 grid
        
        import time
        
        agent_state_pub.publish(AgentState(pose=Pose(position=Point(x=1.0, y=2.0, z=0.0))))
        time.sleep(0.05)
        map_pub.publish(sample_occupancy_grid)
        
        activate_cli: Client = cli_node.create_client(
            SendPose,
            '/hybraut_nav/planner/activate'
        )
        req: SendPose.Request = SendPose.Request()
        future = activate_cli.call_async(req)

        # Wait for the future to complete with a timeout
        rclpy.spin_until_future_complete(cli_node, future, timeout_sec=100.0)
        assert future.done(), "Service call timed out"
        response = future.result()
        assert response is not None, "Service response should not be None"
        assert response.success, "Service call should be successful"
        assert plan[-1] is not None, "StrategyNode should have published a plan"
        from nav_msgs.msg import Path
        assert isinstance(plan[-1], Path), "Published plan should be of type Path"

        # Add further assertions on response as needed

        cli_node.destroy_client(activate_cli)
        
    def test_deactivate_service_via_cli(self, strategy_node_and_mock_node_cli):
        ... 
        

    
    
if __name__ == '__main__':
    pytest.main([__file__])