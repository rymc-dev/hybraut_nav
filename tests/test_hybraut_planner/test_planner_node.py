import pytest
import rclpy
from rclpy.node import Node
from hybraut_planner import PlannerNode

from hybraut_planner.path_planning import AStar, Dijkstra, RRT, RRTStar, Planner
from typing import Type

import threading
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import QoSProfile, QoSDurabilityPolicy

from nav_msgs.msg import OccupancyGrid
from colav_interfaces.msg import AgentState
from geometry_msgs.msg import PoseStamped

from typing import Any
from rclpy.serialization import serialize_message
import time


qos_profile = QoSProfile(depth=10)
qos_profile.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL

@pytest.fixture(scope="session", autouse=True)
def rclpy_init_shutdown():
    rclpy.init()
    yield
    rclpy.shutdown()

@pytest.fixture(scope="class")
def test_node_fixture(request, rclpy_init_shutdown):
    node = Node('test_node')
    
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    
    spinner_thread = threading.Thread(target=executor.spin, daemon=True)
    spinner_thread.start()
    
    request.cls.node = node
    request.cls.executor = executor
    request.cls.spinner_thread = spinner_thread
    
    yield node
    node.destroy_node()
    
@pytest.fixture(scope="class")
def planner_node_fixture(request):
    # Initialize the planner node
    planner_node = PlannerNode()
    request.cls.planner_node = planner_node
    yield planner_node
    planner_node.destroy_node()


@pytest.mark.usefixtures("test_node_fixture", "planner_node_fixture")
class TestPlannerNode:
    
    def test_node_is_running(self):
        assert self.node.get_name() == 'test_node'
        assert self.spinner_thread.is_alive()
        
    def test_initialize_planner(self):
        assert self.planner_node is not None
        assert self.planner_node.get_name() == 'planner'
        assert self.planner_node.get_namespace() == '/hybraut_nav'
        
    def test_run_planner(self):
        self.executor.add_node(self.planner_node)
        
    def test_default_planner_parameters(self):        
        # Check some default parameters
        assert self.planner_node.get_parameter('use_sim_time').get_parameter_value().bool_value == False
        assert self.planner_node.get_parameter('planner_frequency').get_parameter_value().double_value == 0.1
        assert self.planner_node.get_parameter('planner_type').get_parameter_value().string_value == 'A*'
        assert self.planner_node.get_parameter('max_planning_time').get_parameter_value().double_value == 5.0
        assert self.planner_node.get_parameter('description').get_parameter_value().string_value == "This node handles global path planning using various algorithms for the hybraut_nav stack."
        # assert self.planner_node.get_parameter('max_planning_retries').get_parameter_value().integer_value == 3
        
    def test_default_attributes(self):
        assert hasattr(self.planner_node, 'state') and self.planner_node.state.value == 'inactive' 
        assert hasattr(self.planner_node, 'current_cost_map') and self.planner_node.current_cost_map is None
        assert hasattr(self.planner_node, 'current_agent_pose') and self.planner_node.current_agent_pose is None
        assert hasattr(self.planner_node, 'current_goal_pose') and self.planner_node.current_goal_pose is None
        assert hasattr(self.planner_node, 'planner') and type(self.planner_node.planner).__name__ == "AStar"
        
    def test_subscriptions(self):
        expected_subscriptions = [
            "/map",
            "/agent_state"
        ]

        from nav_msgs.msg import OccupancyGrid
        from colav_interfaces.msg import AgentState

        expected_types = [
            OccupancyGrid,
            AgentState
        ]

        def ros_type_string(msg_cls):
            parts = msg_cls.__module__.split('.')
            pkg = parts[0]
            subfolder = parts[1]
            name = msg_cls.__name__
            return f"{pkg}/{subfolder}/{name}"

        for expected_topic, expected_type in zip(expected_subscriptions, expected_types):
            infos = self.planner_node.get_subscriptions_info_by_topic(expected_topic)
            matching_infos = [info for info in infos if info.node_name == self.planner_node.get_name()]

            assert matching_infos, f"Subscription for {expected_topic} not found in node {self.planner_node.get_name()}"

            topic_info = matching_infos[0]

            expected_type_str = ros_type_string(expected_type)
            actual_type_str = topic_info.topic_type

            assert actual_type_str == expected_type_str, (
                f"Type mismatch for topic {expected_topic}: expected {expected_type_str}, got {actual_type_str}"
            )

    @pytest.mark.parametrize(
        "topic, msg, callback_attribute, expected_attribute_value",
        [
            ("/map", OccupancyGrid(), "current_cost_map", OccupancyGrid()),
            ("/agent_state", AgentState(), "current_agent_pose", PoseStamped()),
        ],
        ids=[
            "test /map callback updates current_cost_map attribute",
            "test /agent_state callback updates current_agent_pose attribute correctly"
        ]
    )
    def test_subscription_callbacks(self, topic: str, msg: Any, callback_attribute: str, expected_attribute_value: Any):
        pub = self.node.create_publisher( 
            type(msg), 
            topic, 
            qos_profile=10 
        ) 
        import time 
        time.sleep(0.05) 
        pub.publish(msg)  
        self.node.destroy_publisher(pub) 
        time.sleep(0.05)
        actual_value = getattr(self.planner_node, callback_attribute) 
        
        assert serialize_message(actual_value) == serialize_message(expected_attribute_value)
                
    def test_publishers(self):
        from nav_msgs.msg import Path 
        expected_publisher = "/hybraut_nav/plan"
        expected_type = Path

        infos = self.planner_node.get_publishers_info_by_topic(expected_publisher)
        matching_infos = [info for info in infos if info.node_name == self.planner_node.get_name()]

        assert matching_infos, f"Publisher for {expected_publisher} not found in node {self.planner_node.get_name()}"

        topic_info = matching_infos[0]

        def ros_type_string(msg_cls):
            parts = msg_cls.__module__.split('.')
            pkg = parts[0]
            subfolder = parts[1]
            name = msg_cls.__name__
            return f"{pkg}/{subfolder}/{name}"

        expected_type_str = ros_type_string(expected_type)
        actual_type_str = topic_info.topic_type

        assert actual_type_str == expected_type_str, (
            f"Type mismatch for topic {expected_publisher}: expected {expected_type_str}, got {actual_type_str}"
        )
        
    def test_services(self):
        ...
        
    @pytest.mark.parametrize(
        "planner_frequency", [0.1, 1.0, 5.0],
        ids=["planner_frequency_0.1", "planner_frequency_1.0", "planner_frequency_5.0"]
    )
    def test_planner_frequency_when_planner_not_active(self, planner_frequency: float):
        self.planner_node.set_parameters([
            rclpy.parameter.Parameter(
                'planner_frequency', 
                rclpy.Parameter.Type.DOUBLE, 
                planner_frequency
            )
        ])
        time.sleep(0.1)
        expected_period_ns = int((1.0 / planner_frequency) * 1e9)
        assert self.planner_node.planner_timer.timer_period_ns == expected_period_ns

    @pytest.mark.parametrize(
        "planner_type, expected_planner_class", [('A*', AStar), ('Dijkstra', Dijkstra), ('RRT', RRT), ('RRT*', RRTStar)],
        ids=["planner_type_AStar", "planner_type_Dijkstra", "planner_type_RRT", "planner_type_RRTStar"]
    )
    def test_planner_type_change_when_planner_inactive(self, planner_type: str, expected_planner_class: Type[Planner]): 
        self.planner_node.set_parameters([
            rclpy.parameter.Parameter(
                'planner_type',
                rclpy.Parameter.Type.STRING,
                planner_type
            )
        ])
        time.sleep(0.1)
        expected_planner_class_name = expected_planner_class.__name__
        assert self.planner_node.planner.__class__.__name__ == expected_planner_class_name
    
    @pytest.mark.parametrize(
        "goal",
        [
            PoseStamped()
        ],
        ids=[
            "pose_stamped"
        ]
    )
    def test_set_goal_service(self, goal: PoseStamped):
        self.node: Node = self.node
        from hybraut_interfaces.srv import SendPose
        from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
        send_goal_cli = self.node.create_client(
            SendPose,
            '/hybraut_nav/send_goal',
            callback_group=MutuallyExclusiveCallbackGroup()
        )
        
        while not send_goal_cli.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().info('service not available, waiting again...')
                        
        request = SendPose.Request(pose=goal)
        future = send_goal_cli.call_async(request)
        try:
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=2.0)
        except TimeoutError:
            self.node.get_logger().error('Service call timed out')
        except Exception as e:
            self.node.get_logger().error(f'Error occurred: {e}')

        assert future.done()
        assert future.result().success == True
        
        time.sleep(0.1)
        
        assert getattr(self.planner_node, 'state').value == 'active'
        assert serialize_message(getattr(self.planner_node, 'current_goal_pose')) == serialize_message(goal)
        assert not getattr(self.planner_node, 'planner_timer').is_canceled()

        
        from std_srvs.srv import Trigger
        deactivate_planner_cli = self.node.create_client(
            Trigger,
            '/hybraut_nav/deactivate',
            callback_group=MutuallyExclusiveCallbackGroup()
        )
        while not deactivate_planner_cli.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().info('service not available, waiting again...')
            
        try:
            future = deactivate_planner_cli.call_async(Trigger.Request())
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=2.0)
        except TimeoutError:
            self.node.get_logger().error('Service call timed out')
        except Exception as e:
            self.node.get_logger().error(f'Error occurred: {e}')
        
        assert future.done()
        assert future.result().success == True
        time.sleep(0.1)
        
        assert getattr(self.planner_node, 'state').value == 'inactive'
        assert getattr(self.planner_node, 'current_goal_pose') is None
        assert getattr(self.planner_node, 'planner_timer').is_canceled()
        
        self.planner_node: Node = self.planner_node
        
        self.planner_node.destroy_client(send_goal_cli)
        self.planner_node.destroy_client(deactivate_planner_cli)

    # @pytest.mark.parametrize(
    #     "goal",
    #     [
    #         PoseStamped()
    #     ],
    #     ids=[
    #         "pose_stamped"
    #     ]
    # )
    # def test_planner_frequency_when_planner_active(self):
    #     ...
    
    # @pytest.mark.parametrize(
        
    # )
    # def test_planner_type_change_when_planner_active(self):
    #     ... 
         
         
def main():
    pytest.main([__file__])

if __name__ == '__main__':
    main()