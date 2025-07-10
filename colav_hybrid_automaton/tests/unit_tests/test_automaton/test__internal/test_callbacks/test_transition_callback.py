"""
Test Suite for transition evaluation callback function
which is a key component of the hybrid automaton framework,
This callback function operates on a timer on the main lifecycle 
node when the automaton is active and performs transition evaluations
for the current automaton mode we are in.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
import pytest
from colav_hybrid_automaton.automaton._internal.callbacks.transition_callbacks import transition_evaluation_callback
from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory

from hybrid_automaton_interfaces.msg import (
    HybridAutomatonStatus,
    HybridAutomatonMode,
    HybridAutomatonTransitionEvaluations
)
import threading
from colav_hybrid_automaton.automaton._internal.model import HybridAutomaton
from rclpy.callback_groups import ReentrantCallbackGroup


DEFAULT_QOS = QoSProfile(depth=10)
DEFAULT_CALLBACK_GROUP = ReentrantCallbackGroup()

@pytest.fixture
def mocker_for_transition_evaluation_callback_tests():
    rclpy.init()

    mock_node = Node('mock_node')

    qos_profile = QoSProfile(depth=10)
    mode_publisher = mock_node.create_publisher(
        topic='/hybrid_automaton/mode',
        msg_type=HybridAutomatonMode,
        qos_profile=qos_profile
    )
    transition_evaluation_publisher = mock_node.create_publisher(
        topic='/hybrid_automaton/transition_evaluations',
        msg_type=HybridAutomatonTransitionEvaluations,
        qos_profile=qos_profile
    )
    status_publisher = mock_node.create_publisher(
        topic='/hybrid_automaton/status',
        msg_type=HybridAutomatonStatus,
        qos_profile=qos_profile
    )

    automaton_model:HybridAutomaton = HybridAutomatonFactory.hybrid_automaton_registry(
        automaton_famd_path='/home/3507145@eeecs.qub.ac.uk/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
        generate_mmd_diagrams=False
    )
    
     
    stamp = mock_node.get_clock().now().to_msg()
    lock = threading.Lock()

    yield (
        automaton_model,
        stamp,
        mode_publisher,
        transition_evaluation_publisher,
        status_publisher
    )

    rclpy.shutdown()

class TestTransitionEvaluationCallback():
    """test suite for the hybrid automatons transition evaluation callback function"""
    
    @pytest.mark.parametrize(
            
    )
    def test_transition_evaluation_callback_comprehensive(
        automaton_mode: HybridAutomatonMode,
        mocker_for_transition_evaluation_callback_tests,
        request
    ):
        """test comprehensively this callback function"""
        pass