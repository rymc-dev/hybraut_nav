"""
Integration Tests for hybrautNav StrategyNode
"""


import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, ActionClient
from rclpy.executors import MultiThreadedExecutor
import threading
import pytest
from hybraut_nav_strategy import StrategyNode
from hybraut_nav_strategy.strategy_node import map_qos, world_state_qos
from hybraut_nav_strategy.path_planning import AStar, Planner
from typing import Tuple
from hybraut_nav.action import ExecuteMission, NavigateToGoal


class FakeTacticalNode(Node):
    """
    Stands in for tactical_node's execute_mission action so StrategyNode's
    leg-by-leg dispatch logic can be exercised without a real tactical
    layer. Accepts every goal and immediately succeeds it (as if the
    automaton reached the target instantly), recording each waypoint
    received.
    """

    def __init__(self):
        super().__init__('fake_tactical_node')
        self.received_goals = []
        self._action_server = ActionServer(
            self, ExecuteMission, '/hybraut_nav/tactical_node/execute_mission',
            execute_callback=self._execute_cb,
        )

    def _execute_cb(self, goal_handle):
        self.received_goals.append(goal_handle.request.goal_waypoint)
        goal_handle.succeed()
        return ExecuteMission.Result(success=True, message="Waypoint reached")


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
def fake_tactical_node(rclpy_fixture):
    """
    Stands in for tactical_node - see FakeTacticalNode. Spun in its own
    executor/thread, independent of strategy_node_and_mock_node_cli's -
    action calls route fine across independent executors sharing the same
    rclpy context.
    """
    _ = rclpy_fixture
    node = FakeTacticalNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    yield node

    executor.shutdown()
    thread.join()
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
    These tests validate the initialization and configuration of the StrategyNode's parameters, publishers, subscriptions, and action interfaces.
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
        assert strategy_node.get_parameter('planner').value == strategy_node.DEFAULT_PLANNER_TYPE, "Planner type parameter should be initialized to default value"
        assert strategy_node.get_parameter('max_tactical_waypoints').value == strategy_node.DEFAULT_MAX_TACTICAL_WAYPOINTS
        assert strategy_node.get_parameter('plan_check_frequency').value == strategy_node.DEFAULT_PLAN_CHECK_FREQUENCY
        assert strategy_node.get_parameter('path_deviation_tolerance').value == strategy_node.DEFAULT_PATH_DEVIATION_TOLERANCE

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
        from hybraut_nav.msg import AgentState
        assert strategy_node._agent_sub.msg_type is AgentState

    def test_action_interface_initialization(self, strategy_node_and_mock_node_cli):
        """
        @test integration_test test_action_interface_initialization
        @brief Test that the StrategyNode's own action server and its
        action client into the tactical layer are initialized correctly.

        This test:
        - Initializes the StrategyNode.
        - Asserts the navigate_to_goal action server exists and is reachable by name/type.
        - Asserts the execute_mission action client exists and is of the right type.
        """

        strategy_node, cli_node = strategy_node_and_mock_node_cli
        strategy_node: StrategyNode = strategy_node

        assert isinstance(strategy_node._mission_action_server, ActionServer), \
            "navigate_to_goal action server should be initialized"
        assert isinstance(strategy_node._tactical_action_client, ActionClient), \
            "execute_mission action client should be initialized"

        probe = ActionClient(cli_node, NavigateToGoal, '/hybraut_nav/strategy_node/navigate_to_goal')
        try:
            assert probe.wait_for_server(timeout_sec=5.0), \
                "navigate_to_goal action server should be discoverable"
        finally:
            probe.destroy()

    """ === Test parameter updates Via CLI === """

    @pytest.mark.parametrize("new_value, expected_planner_cls", [
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
        from hybraut_nav.msg import AgentState
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

    """ === Test navigate_to_goal action via CLI === """

    def test_navigate_to_goal_action_via_cli(
        self,
        strategy_node_and_mock_node_cli: Tuple[StrategyNode, Node],
        fake_tactical_node: FakeTacticalNode,
    ):
        strategy_node, cli_node = strategy_node_and_mock_node_cli
        from nav_msgs.msg import OccupancyGrid, Path
        from hybraut_nav.msg import AgentState, Waypoint
        from rclpy.publisher import Publisher
        from geometry_msgs.msg import Pose, Point

        map_pub: Publisher = cli_node.create_publisher(OccupancyGrid, '/map', map_qos)
        agent_state_pub: Publisher = cli_node.create_publisher(AgentState, '/agent_state', world_state_qos)

        from rclpy.subscription import Subscription

        plan = []
        plan_sub: Subscription = cli_node.create_subscription(
            topic='/hybraut_nav/planner/plan',
            msg_type=Path,
            callback=lambda msg: plan.append(msg),
            qos_profile=world_state_qos
        )

        sample_occupancy_grid = OccupancyGrid()
        sample_occupancy_grid.header.frame_id = "map"
        sample_occupancy_grid.info.resolution = 1.0
        sample_occupancy_grid.info.width = 10
        sample_occupancy_grid.info.height = 10
        sample_occupancy_grid.info.origin.position.x = 0.0
        sample_occupancy_grid.info.origin.position.y = 0.0
        sample_occupancy_grid.data = [0] * 100  # 10x10 grid, all free

        import time

        agent_state_pub.publish(AgentState(pose=Pose(position=Point(x=1.0, y=2.0, z=0.0))))
        time.sleep(0.05)
        map_pub.publish(sample_occupancy_grid)
        time.sleep(0.05)

        action_client = ActionClient(cli_node, NavigateToGoal, '/hybraut_nav/strategy_node/navigate_to_goal')
        assert action_client.wait_for_server(timeout_sec=5.0), "navigate_to_goal action server should be available"

        goal_msg = NavigateToGoal.Goal()
        goal_msg.goal_waypoint = Waypoint(position=Point(x=8.0, y=8.0, z=0.0))

        send_future = action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(cli_node, send_future, timeout_sec=10.0)
        assert send_future.done(), "send_goal call timed out"
        goal_handle = send_future.result()
        assert goal_handle is not None and goal_handle.accepted, "navigate_to_goal goal should be accepted"

        # planning happens inside execute_callback, which only starts after
        # goal acceptance - so it isn't guaranteed to have published yet at
        # this point. It's always done before the result comes back though
        # (planning precedes any leg dispatch), so check there instead.
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(cli_node, result_future, timeout_sec=10.0)
        assert result_future.done(), "get_result call timed out"
        result = result_future.result().result
        assert result.success, f"Mission should complete successfully: {result.message}"

        assert plan, "StrategyNode should have published a plan"
        assert isinstance(plan[-1], Path), "Published plan should be of type Path"
        assert plan[-1].poses, "Published plan should contain at least one waypoint"

        assert fake_tactical_node.received_goals, \
            "StrategyNode should have dispatched at least one waypoint to tactical_node/execute_mission"

        # the fake tactical node resolves every leg instantly, so there's no
        # reliable window to catch strategy_node ACTIVE mid-mission here -
        # just confirm it's back to INACTIVE once the mission has resolved.
        assert not strategy_node.is_active(), "StrategyNode should be INACTIVE once the mission completes"

        action_client.destroy()
        cli_node.destroy_subscription(plan_sub)
        cli_node.destroy_publisher(map_pub)
        cli_node.destroy_publisher(agent_state_pub)

    def test_cancel_mission_via_cli(self, strategy_node_and_mock_node_cli):
        ...




if __name__ == '__main__':
    pytest.main([__file__])
