# """ 
# Integration tests for the PlannerNode in the hybraut_planner package.
# These tests cover node lifecycle and initialization tests, ros communication tests,
# service interface tests, dynamic reconfiguration tests, the functionality fo the path planners 
# are tested within the path_planning module tests.
# """

# import pytest
# import rclpy
# from rclpy.node import Node
# from rclpy.executors import MultiThreadedExecutor
# from rclpy.qos import QoSProfile, QoSDurabilityPolicy
# from rclpy.serialization import serialize_message
# from rclpy.callback_groups import MutuallyExclusiveCallbackGroup

# from hybraut_planner import PlannerNode
# from hybraut_planner.path_planning import AStar, Dijkstra, RRT, RRTStar, Planner

# from nav_msgs.msg import OccupancyGrid, Path
# from colav_interfaces.msg import AgentState
# from geometry_msgs.msg import PoseStamped
# from std_srvs.srv import Trigger
# from hybraut_interfaces.srv import SendPose

# from typing import Any, Type
# import threading
# import time
# import types
# from hybraut_planner.planner_node import PlannerNode, PlannerState, PlannerType


# # Constants
# QOS_PROFILE = QoSProfile(depth=10, durability=QoSDurabilityPolicy.TRANSIENT_LOCAL)
# SERVICE_TIMEOUT = 1.0
# SPIN_TIMEOUT = 2.0
# SLEEP_DURATION = 0.1


# # Fixtures
# @pytest.fixture(scope="session", autouse=True)
# def rclpy_init_shutdown():
#     """Initialize and shutdown ROS 2 for the entire test session."""
#     rclpy.init()
#     yield
#     rclpy.shutdown()


# @pytest.fixture(scope="class")
# def test_node_fixture(request, rclpy_init_shutdown):
#     """Create a test node with executor for the test class."""
#     node = Node('test_node')
#     executor = MultiThreadedExecutor(num_threads=2)
#     executor.add_node(node)
    
#     spinner_thread = threading.Thread(target=executor.spin, daemon=True)
#     spinner_thread.start()
    
#     request.cls.node = node
#     request.cls.executor = executor
#     request.cls.spinner_thread = spinner_thread
    
#     yield node
#     node.destroy_node()
    

# @pytest.fixture(scope="class")
# def planner_node_fixture(request):
#     """Create the planner node for the test class."""
#     planner_node = PlannerNode()
#     request.cls.planner_node = planner_node
#     yield planner_node
#     planner_node.destroy_node()


# # Helper Functions
# def ros_type_string(msg_cls):
#     """Convert a ROS message class to its type string representation."""
#     parts = msg_cls.__module__.split('.')
#     pkg = parts[0]
#     subfolder = parts[1]
#     name = msg_cls.__name__
#     return f"{pkg}/{subfolder}/{name}"


# def call_service_sync(node: Node, client, request, timeout=SPIN_TIMEOUT):
#     """Synchronously call a ROS service and return the result."""
#     future = client.call_async(request)
#     try:
#         rclpy.spin_until_future_complete(node, future, timeout_sec=timeout)
#     except TimeoutError:
#         node.get_logger().error('Service call timed out')
#         raise
#     except Exception as e:
#         node.get_logger().error(f'Error occurred: {e}')
#         raise
#     return future


# def wait_for_service(client, node: Node, timeout=SERVICE_TIMEOUT):
#     """Wait for a service to become available."""
#     while not client.wait_for_service(timeout_sec=timeout):
#         node.get_logger().info('Service not available, waiting again...')


# def activate_planner(node: Node, goal: PoseStamped) -> tuple:
#     """
#     Activate the planner by sending a goal.
#     Returns the service client for cleanup.
#     """
#     send_goal_cli = node.create_client(
#         SendPose,
#         '/hybraut_nav/send_goal',
#         callback_group=MutuallyExclusiveCallbackGroup()
#     )
    
#     wait_for_service(send_goal_cli, node)
    
#     request = SendPose.Request(pose=goal)
#     future = call_service_sync(node, send_goal_cli, request)
    
#     assert future.done()
#     assert future.result().success is True
    
#     return send_goal_cli


# def deactivate_planner(node: Node) -> tuple:
#     """
#     Deactivate the planner.
#     Returns the service client for cleanup.
#     """
#     deactivate_cli = node.create_client(
#         Trigger,
#         '/hybraut_nav/deactivate',
#         callback_group=MutuallyExclusiveCallbackGroup()
#     )
    
#     wait_for_service(deactivate_cli, node)
    
#     future = call_service_sync(node, deactivate_cli, Trigger.Request())
    
#     assert future.done()
#     assert future.result().success is True
#     time.sleep(SLEEP_DURATION)
    
#     return deactivate_cli


# def verify_planner_inactive(planner_node):
#     """Verify that the planner is in inactive state."""
#     assert getattr(planner_node, 'state').value == 'inactive'
#     assert getattr(planner_node, 'current_goal_pose') is None
#     assert getattr(planner_node, 'planner_timer').is_canceled()


# def verify_planner_active(planner_node, goal: PoseStamped):
#     """Verify that the planner is in active state with the correct goal."""
#     assert getattr(planner_node, 'state').value == 'active'
#     assert serialize_message(getattr(planner_node, 'current_goal_pose')) == serialize_message(goal)
#     assert not getattr(planner_node, 'planner_timer').is_canceled()


# # Test Class
# @pytest.mark.usefixtures("test_node_fixture", "planner_node_fixture")
# class TestPlannerNode:
    
#     # Lifecycle and Initialization Tests
#     def test_node_is_running(self):
#         """Verify that the test node is running correctly."""
#         assert self.node.get_name() == 'test_node'
#         assert self.spinner_thread.is_alive()
        
#     def test_initialize_planner(self):
#         """Verify planner node initialization and configuration."""
#         assert self.planner_node is not None
#         assert self.planner_node.get_name() == 'planner'
#         assert self.planner_node.get_namespace() == '/hybraut_nav'
        
#     def test_run_planner(self):
#         """Add planner node to executor."""
#         self.executor.add_node(self.planner_node)
        
#     def test_default_planner_parameters(self):
#         """Verify default parameter values."""
#         params = {
#             'use_sim_time': (False, 'bool_value'),
#             'planner_frequency': (0.1, 'double_value'),
#             'planner_type': ('A*', 'string_value'),
#             'max_planning_time': (5.0, 'double_value'),
#             'description': ("This node handles global path planning using various algorithms for the hybraut_nav stack.", 'string_value')
#         }
        
#         for param_name, (expected_value, value_type) in params.items():
#             actual_value = getattr(
#                 self.planner_node.get_parameter(param_name).get_parameter_value(),
#                 value_type
#             )
#             assert actual_value == expected_value, f"Parameter {param_name} mismatch"
        
#     def test_default_attributes(self):
#         """Verify default attribute values."""
#         attributes = {
#             'state': ('inactive', lambda x: x.value),
#             'current_cost_map': (None, lambda x: x),
#             'current_agent_pose': (None, lambda x: x),
#             'current_goal_pose': (None, lambda x: x),
#             'planner': ("AStar", lambda x: type(x).__name__)
#         }
        
#         for attr_name, (expected_value, transform) in attributes.items():
#             assert hasattr(self.planner_node, attr_name)
#             actual_value = transform(getattr(self.planner_node, attr_name))
#             assert actual_value == expected_value, f"Attribute {attr_name} mismatch"
    
#     # ROS Communication Tests
#     def test_subscriptions(self):
#         """Verify that the node subscribes to the correct topics with correct types."""
#         subscriptions = {
#             "/map": OccupancyGrid,
#             "/agent_state": AgentState
#         }

#         for topic, expected_type in subscriptions.items():
#             infos = self.planner_node.get_subscriptions_info_by_topic(topic)
#             matching_infos = [info for info in infos if info.node_name == self.planner_node.get_name()]

#             assert matching_infos, f"Subscription for {topic} not found"

#             expected_type_str = ros_type_string(expected_type)
#             actual_type_str = matching_infos[0].topic_type

#             assert actual_type_str == expected_type_str, \
#                 f"Type mismatch for {topic}: expected {expected_type_str}, got {actual_type_str}"

#     @pytest.mark.parametrize(
#         "topic, msg, callback_attribute, expected_attribute_value",
#         [
#             ("/map", OccupancyGrid(), "current_cost_map", OccupancyGrid()),
#             ("/agent_state", AgentState(), "current_agent_pose", PoseStamped()),
#         ],
#         ids=[
#             "map_callback",
#             "agent_state_callback"
#         ]
#     )
#     def test_subscription_callbacks(self, topic: str, msg: Any, 
#                                    callback_attribute: str, expected_attribute_value: Any):
#         """Verify that subscription callbacks update attributes correctly."""
#         pub = self.node.create_publisher(type(msg), topic, qos_profile=10)
#         time.sleep(0.05)
        
#         pub.publish(msg)
        
#         time.sleep(0.05)
#         self.node.destroy_publisher(pub)
        
#         actual_value = getattr(self.planner_node, callback_attribute)
#         assert serialize_message(actual_value) == serialize_message(expected_attribute_value)
                
#     def test_publishers(self):
#         """Verify that the node publishes to the correct topic with correct type."""
#         expected_topic = "/hybraut_nav/plan"
#         expected_type = Path

#         infos = self.planner_node.get_publishers_info_by_topic(expected_topic)
#         matching_infos = [info for info in infos if info.node_name == self.planner_node.get_name()]

#         assert matching_infos, f"Publisher for {expected_topic} not found"

#         expected_type_str = ros_type_string(expected_type)
#         actual_type_str = matching_infos[0].topic_type

#         assert actual_type_str == expected_type_str, \
#             f"Type mismatch: expected {expected_type_str}, got {actual_type_str}"
    
#     # Dynamic Reconfiguration Tests (Inactive State)
#     @pytest.mark.parametrize(
#         "planner_frequency", 
#         [0.1, 1.0, 5.0],
#         ids=["freq_0.1", "freq_1.0", "freq_5.0"]
#     )
#     def test_planner_frequency_when_planner_not_active(self, planner_frequency: float):
#         """Verify planner frequency changes when inactive."""
#         self.planner_node.set_parameters([
#             rclpy.parameter.Parameter('planner_frequency', rclpy.Parameter.Type.DOUBLE, planner_frequency)
#         ])
#         time.sleep(SLEEP_DURATION)
        
#         expected_period_ns = int((1.0 / planner_frequency) * 1e9)
#         assert self.planner_node.planner_timer.timer_period_ns == expected_period_ns

#     @pytest.mark.parametrize(
#         "planner_type, expected_planner_class", 
#         [
#             ('A*', AStar), 
#             ('Dijkstra', Dijkstra), 
#             ('RRT', RRT), 
#             ('RRT*', RRTStar)
#         ],
#         ids=["AStar", "Dijkstra", "RRT", "RRTStar"]
#     )
#     def test_planner_type_change_when_planner_inactive(self, planner_type: str, 
#                                                        expected_planner_class: Type[Planner]): 
#         """Verify planner type changes when inactive."""
#         self.planner_node.set_parameters([
#             rclpy.parameter.Parameter('planner_type', rclpy.Parameter.Type.STRING, planner_type)
#         ])
#         time.sleep(SLEEP_DURATION)
        
#         assert self.planner_node.planner.__class__.__name__ == expected_planner_class.__name__
    
#     # Service Interface Tests
#     @pytest.mark.parametrize("goal", [PoseStamped()], ids=["pose_stamped"])
#     def test_set_goal_service(self, goal: PoseStamped):
#         """Verify goal setting and deactivation services work correctly."""
#         # Activate planner
#         send_goal_cli = activate_planner(self.node, goal)
#         time.sleep(SLEEP_DURATION)
#         verify_planner_active(self.planner_node, goal)
        
#         # Deactivate planner
#         deactivate_cli = deactivate_planner(self.node)
#         verify_planner_inactive(self.planner_node)
        
#         # Cleanup
#         self.planner_node.destroy_client(send_goal_cli)
#         self.planner_node.destroy_client(deactivate_cli)

#     # Dynamic Reconfiguration Tests (Active State)
#     @pytest.mark.parametrize(
#         "frequency",
#         [1.0, 2.0, 0.1],
#         ids=["freq_1.0", "freq_2.0", "freq_0.1"]
#     )
#     def test_planner_frequency_change_when_planner_active(self, frequency: float):
#         """Verify planner frequency changes when active."""
#         goal = PoseStamped()
        
#         # Activate planner
#         send_goal_cli = activate_planner(self.node, goal)
        
#         # Change frequency
#         self.planner_node.set_parameters([
#             rclpy.parameter.Parameter('planner_frequency', rclpy.Parameter.Type.DOUBLE, frequency)
#         ])
#         time.sleep(SLEEP_DURATION)
        
#         expected_period_ns = int((1.0 / frequency) * 1e9)
#         assert self.planner_node.planner_timer.timer_period_ns == expected_period_ns
        
#         # Deactivate and cleanup
#         deactivate_cli = deactivate_planner(self.node)
#         verify_planner_inactive(self.planner_node)
        
#         self.planner_node.destroy_client(send_goal_cli)
#         self.planner_node.destroy_client(deactivate_cli)
         
#     @pytest.mark.parametrize(
#         "planner_type, expected_planner_class",
#         [
#             ('A*', AStar),
#             ('Dijkstra', Dijkstra),
#             ('RRT', RRT),
#             ('RRT*', RRTStar)
#         ],
#         ids=["AStar", "Dijkstra", "RRT", "RRTStar"]
#     )
#     def test_planner_type_change_when_planner_active(self, planner_type: str, 
#                                                      expected_planner_class: Type[Planner]):
#         """Verify planner type changes when active."""
#         goal = PoseStamped()
        
#         # Activate planner
#         send_goal_cli = activate_planner(self.node, goal)

#         # Change planner type
#         self.planner_node.set_parameters([
#             rclpy.parameter.Parameter('planner_type', rclpy.Parameter.Type.STRING, planner_type)
#         ])
#         time.sleep(SLEEP_DURATION)

#         assert self.planner_node.planner.__class__.__name__ == expected_planner_class.__name__
#         assert not getattr(self.planner_node, 'planner_timer').is_canceled()

#         # Deactivate and cleanup
#         deactivate_cli = deactivate_planner(self.node)
#         verify_planner_inactive(self.planner_node)

#         self.planner_node.destroy_client(send_goal_cli)
#         self.planner_node.destroy_client(deactivate_cli)
# # === UNIT TESTS FOR PlannerNode (no rclpy running) ===




# class DummyPlanner:
#     def __init__(self):
#         self.plan_path_called = False
#     def plan_path(self, grid, start, goal):
#         self.plan_path_called = True
#         return "dummy_path"

# def test_set_planner_sets_correct_type(monkeypatch):
#     node = PlannerNode.__new__(PlannerNode)
#     # Patch set_planner to avoid rclpy dependency
#     monkeypatch.setattr('hybraut_planner.planner_node.PlannerType.initialize_planner', lambda pt: DummyPlanner())
#     node.set_planner(PlannerType.ASTAR)
#     assert isinstance(node.planner, DummyPlanner)

# def test_set_planner_frequency_changes_timer(monkeypatch):
#     node = PlannerNode.__new__(PlannerNode)
#     node.state = PlannerState.ACTIVE
#     node._plan_path_callback = lambda: None
#     # Mock planner_timer
#     class DummyTimer:
#         def cancel(self): self.canceled = True
#     node.planner_timer = DummyTimer()
#     def fake_create_timer(period, cb, autostart, callback_group):
#         node.timer_period = period
#         return DummyTimer()
#     node.create_timer = fake_create_timer
#     node.set_planner_frequency(2.0)
#     assert node.timer_period == 0.5

# def test_toggle_state_changes_state():
#     node = PlannerNode.__new__(PlannerNode)
#     node.state = PlannerState.INACTIVE
#     node.get_logger = lambda: types.SimpleNamespace(info=lambda msg: None)
#     node._PlannerNode__toggle_state(True)
#     assert node.state == PlannerState.ACTIVE
#     node._PlannerNode__toggle_state(False)
#     assert node.state == PlannerState.INACTIVE

# def test_is_active_property():
#     node = PlannerNode.__new__(PlannerNode)
#     node.state = PlannerState.ACTIVE
#     assert node.is_active is True
#     node.state = PlannerState.INACTIVE
#     assert node.is_active is False

# def test_has_required_data_true_false():
#     node = PlannerNode.__new__(PlannerNode)
#     node.current_agent_pose = object()
#     node.current_goal_pose = object()
#     node.current_cost_map = object()
#     assert node._has_required_data() is True
#     node.current_cost_map = None
#     assert node._has_required_data() is False

# def test_set_planner_type_sets_planner(monkeypatch):
#     node = PlannerNode.__new__(PlannerNode)
#     monkeypatch.setattr(node, 'set_planner', lambda pt: setattr(node, 'planner_type_set', pt))
#     node.get_logger = lambda: types.SimpleNamespace(info=lambda msg: None)
#     node._set_planner_type('A*')
#     assert node.planner_type_set == PlannerType.ASTAR

# def test_parameter_callback_handles_frequency_and_type(monkeypatch):
#     node = PlannerNode.__new__(PlannerNode)
#     monkeypatch.setattr(node, 'set_planner_frequency', lambda v: setattr(node, 'freq_set', v))
#     monkeypatch.setattr(node, '_set_planner_type', lambda v: setattr(node, 'type_set', v))
#     monkeypatch.setattr(node, '_PlannerNode__toggle_state', lambda v: setattr(node, 'state_set', v))
#     node.get_logger = lambda: types.SimpleNamespace(info=lambda msg: None)
#     params = [
#         types.SimpleNamespace(name='planner_frequency', value=2.0),
#         types.SimpleNamespace(name='planner_type', value='Dijkstra'),
#         types.SimpleNamespace(name='planner_active', value=True),
#         types.SimpleNamespace(name='event_horizon', value=5.0)
#     ]
#     result = node._PlannerNode__parameter_callback(params)
#     assert node.freq_set == 2.0
#     assert node.type_set == 'Dijkstra'
#     assert node.state_set is True
#     assert result.successful is True

# def test_compute_path_calls_planner(monkeypatch):
#     node = PlannerNode.__new__(PlannerNode)
#     dummy_planner = DummyPlanner()
#     node.planner = dummy_planner
#     node.current_cost_map = object()
#     node.current_agent_pose = object()
#     node.current_goal_pose = object()
#     monkeypatch.setattr('hybraut_planner.planner_node.PlannerGrid.from_ros_msg', lambda x: "grid")
#     monkeypatch.setattr('hybraut_planner.planner_node.PlannerPoint.from_ros_msg', lambda x: "pt")
#     result = node._compute_path()
#     assert dummy_planner.plan_path_called
#     assert result == "dummy_path"

# if __name__ == '__main__':
#     pytest.main([__file__])