import pytest
import rclpy
from rclpy.node import Node



@pytest.fixture
def mock_invaraints_callback_requirements():
    pass

class TestInvariantCallback:
    """test suite for the invariants evaluation callback"""

    @pytest.mark.parametrize(
            "",
            [

            ],
            ids=[

            ]
    )
    def test_invariant_evaluation_callback_comprehensive():
        pass


if __name__ == '__main__':
    pytest.main([__file__])
# import rclpy
# from rclpy.executors import MultiThreadedExecutor
# import threading
# from hybrid_automaton_interfaces.msg import (
#     HybridAutomatonDynamicsEvaluation,

# )
# from rclpy.qos import QoSProfile
# from colav_hybrid_automaton.automaton._internal.factory import HybridAutomatonFactory

# if __name__ == '__main__':
#     rclpy.init()
#     executor = MultiThreadedExecutor(num_threads=2)
#     mock_node = Node('mock_node')
#     executor.add_node(mock_node)

#     lock = threading.Lock()
#     automaton_model:HybridAutomaton = HybridAutomatonFactory.hybrid_automaton_registry(
#         automaton_famd_path='/home/ryan/ros2_ws/src/colav-hybrid-automaton/colav_hybrid_automaton/colav_hybrid_automaton/automaton/colav-famd.yml', 
#         generate_mmd_diagrams=False
#     )
#     automaton_model.create_state_publishers(node=mock_node)
#     automaton_model.create_state_subscriptions(node=mock_node)
#     stamp = Time()
#     invariants_evaluation_publisher = mock_node.create_publisher(
#         topic = '/hybrid_automaton/invariants',
#         msg_type = HybridAutomatonInvariantsEvaluation,
#         qos_profile = QoSProfile(depth=10)
#     ) 
#     status_publisher = mock_node.create_publisher(
#         topic = '/hybrid_automaton/status',
#         msg_type = HybridAutomatonStatus,
#         qos_profile = QoSProfile(depth=10)
#     )

#     threading.Thread(target=executor.spin).start()
    
#     invariants_evaluation_callback(
#         lock=lock,
#         automaton_model=automaton_model,
#         stamp=stamp,
#         invariants_evaluation_publisher=invariants_evaluation_publisher,
#         status_publisher=status_publisher
#     )

#     rclpy.shutdown()