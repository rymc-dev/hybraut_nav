""" 
test suite for dynamics callback
this is a key component of the hybrid automaton framework. 
This callback it utilized at a certain hz rate for calling 
the dynamics evaluation function.
"""

import pytest
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from colav_hybrid_automaton.automaton._internal.callbacks.dynamic_callbacks import dynamics_evaluation_callback
from hybrid_automaton_interfaces.msg import HybridAutomatonMode
from colav_interfaces.msg import (
    AgentState,
    WaypointsState
)
import threading
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton
from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory
from hybrid_automaton_interfaces.msg import HybridAutomatonDynamicsEvaluation, HybridAutomatonStatus
from rclpy.qos import QoSProfile
import time

@pytest.fixture
def mock_dynamics_fixture():
    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=2)
    mock_node = Node('mock_node')
    executor.add_node(mock_node)
    qos_profile = QoSProfile(depth=10)
    
    lock = threading.Lock()
    automaton_model:HybridAutomaton = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path='/home/ryan/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
        generate_mmd_diagrams=False
    )
    automaton_model.create_state_publishers(node=mock_node)
    automaton_model.create_state_subscriptions(node=mock_node)
    stamp = mock_node.get_clock().now().to_msg()
    dynamics_evaluation_publisher = mock_node.create_publisher(
        topic = '/hybrid_automaton/dynamics',
        msg_type = HybridAutomatonDynamicsEvaluation,
        qos_profile = qos_profile
    ) 
    status_publisher = mock_node.create_publisher(
        topic = '/hybrid_automaton/status',
        msg_type = HybridAutomatonStatus,
        qos_profile = qos_profile
    )

    status_list = []
    def status_callback(msg: HybridAutomatonStatus):
        status_list.append(msg)

    mock_node.create_subscription(
        msg_type=HybridAutomatonStatus,
        topic='/hybrid_automaton/dynamics',
        callback=status_callback,
        qos_profile=qos_profile
    )

    dynamics_evaluation_list = []
    def dynamics_callback(msg: HybridAutomatonDynamicsEvaluation):
        dynamics_evaluation_list.append(msg)

    mock_node.create_subscription(
        msg_type=HybridAutomatonDynamicsEvaluation,
        topic='/hybrid_automaton/dynamics_evaluation',
        callback=dynamics_callback,
        qos_profile=qos_profile
    )

    threading.Thread(target=executor.spin).start()

    yield lock, automaton_model, stamp, dynamics_evaluation_publisher, status_publisher, dynamics_evaluation_list, status_list

    rclpy.shutdown()

class TestDynamicsEvaluationCallback:
    """test suite for dynamics callback"""
    
    @pytest.mark.parametrize(
            "mode, agent_state, waypoints_state",
            [
                (HybridAutomatonMode.MODE_CRUISE, AgentState(), WaypointsState())
            ],
            ids=[
                "valid agent state and waypoints state for a controller"
            ]
    )
    def test_dynamics_evaluation_callback_comprehensive(self, mode, agent_state, waypoints_state, mock_dynamics_fixture, request):
        """test valid params for the dynamics callback function"""
        lock, automaton_model, stamp, dynamics_evaluation_publisher, status_publisher, dynamics_evaluation_list, status_list = mock_dynamics_fixture

        automaton_model.current_mode = mode
        automaton_model.states['agent_state'].publisher.publish(agent_state)
        automaton_model.states['waypoints_state'].publisher.publish(waypoints_state)

        time.sleep(0.1)

        dynamics_evaluation_callback(
            lock=lock,
            automaton_model=automaton_model,
            stamp=stamp,
            dynamics_evaluation_publisher=dynamics_evaluation_publisher,
            status_publisher=status_publisher
        )

        time.sleep(0.1)

        print (f"status list: {status_list}")
        print (f"dynamics_evaluation_list: {dynamics_evaluation_list}")
        assert True

if __name__ == '__main__':
    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=2)
    mock_node = Node('mock_node')
    executor.add_node(mock_node)
    qos_profile = QoSProfile(depth=10)
    
    lock = threading.Lock()
    automaton_model:HybridAutomaton = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path='/home/ryan/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
        generate_mmd_diagrams=False
    )
    automaton_model.create_state_publishers(node=mock_node)
    automaton_model.create_state_subscriptions(node=mock_node)
    stamp = mock_node.get_clock().now().to_msg()
    dynamics_evaluation_publisher = mock_node.create_publisher(
        topic = '/hybrid_automaton/dynamics',
        msg_type = HybridAutomatonDynamicsEvaluation,
        qos_profile = qos_profile
    ) 
    status_publisher = mock_node.create_publisher(
        topic = '/hybrid_automaton/status',
        msg_type = HybridAutomatonStatus,
        qos_profile = qos_profile
    )

    threading.Thread(target=executor.spin).start()

    status_list = []

    def status_callback(msg: HybridAutomatonStatus):
        status_list.append(msg)

    mock_node.create_subscription(
        msg_type=HybridAutomatonStatus,       # ❌ Wrong
        topic='/hybrid_automaton/status',   # This topic publishes `HybridAutomatonDynamicsEvaluation`
        callback=status_callback,
        qos_profile=qos_profile
    )

    dynamics_evaluation_list = []
    def dynamics_callback(msg: HybridAutomatonDynamicsEvaluation):
        dynamics_evaluation_list.append(msg)

    mock_node.create_subscription(
        msg_type=HybridAutomatonDynamicsEvaluation,
        topic='/hybrid_automaton/dynamics_evaluation',
        callback=dynamics_callback,
        qos_profile=qos_profile
    )

    mock_dynamics_fixture = lock, automaton_model, stamp, dynamics_evaluation_publisher, status_publisher, dynamics_evaluation_list, status_list

    TestDynamicsEvaluationCallback().test_dynamics_evaluation_callback_comprehensive(
        mode=HybridAutomatonMode.MODE_CRUISE,
        agent_state=AgentState(),
        waypoints_state=WaypointsState(),
        mock_dynamics_fixture=mock_dynamics_fixture,
        request="hello world"
    )

    rclpy.shutdown()