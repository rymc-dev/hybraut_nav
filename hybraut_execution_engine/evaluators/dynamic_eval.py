#! /usr/bin/env python3
"""

"""

# TODO: dynamics evaluation is going to output to it's own output topic like with resets. 
#       not only simplifying the code for the executor and improving udp communication 
#       but also enhancing the modularity and reusability of the codebase.

from rclpy.node import Node
from typing import List, Any, Dict, Callable
from threading import Lock
from builtin_interfaces.msg import Time
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.publisher import Publisher
from hybraut_model import HybridAutomaton
import threading
from hybraut_interfaces.msg import AutomatonDynamicsEvaluation, AutomatonMode, AutomatonStatus

from colav_interfaces.msg import AgentState, WaypointsState

from rclpy.qos import QoSProfile, qos_profile_system_default
from rclpy.callback_groups import CallbackGroup, ReentrantCallbackGroup


class HybrautDynamicEvaluator:
    """ 
    Evaluator for dynamics
    """

    def __init__(self, node: Node, automaton: HybridAutomaton):
        """ 
        Initialize the dynamics evaluator.
        """
        self.node = node
        self.automaton = automaton

        self.__post_init__()

    def __post_init__(
        self, 
        qos: QoSProfile = qos_profile_system_default, 
        cb_group: CallbackGroup = ReentrantCallbackGroup()
    ):
        """
        Post-initialization for the dynamics evaluator.
        """
        self.lock = Lock()
        self.dynamics_evaluation_publisher = self.node.create_publisher(
            AutomatonDynamicsEvaluation,
            '/automaton/dynamics_evaluation',
            qos_profile=qos,
            callback_group=cb_group
        )
    

    """ === evaluation functions ==="""

    def _validate_current_mode(current_mode: int, hybraut_model: HybridAutomaton) -> None:
        """Validate that the current mode exists in the automaton"""
        if current_mode not in list(hybraut_model._modes._modes.keys()):
            raise ValueError(f"Invalid mode type: {current_mode}")

    def _evaluate_dynamics(current_mode: int, hybraut_model: HybridAutomaton, stamp: Time) -> AutomatonDynamicsEvaluation:
        """evaluates the dynamics for the current automaton mode"""
        msg = AutomatonDynamicsEvaluation(
            mode=AutomatonMode(type=current_mode, stamp=stamp),
            stamp=stamp
        )
        
        try:
            msg = hybraut_model.evaluate_dynamics(current_mode_id=current_mode)
        except Exception as e:
            msg.error = True
            msg.message = f"exception occured: {str(e)}"

        return msg

    def dynamics_evaluation_callback(
            self,
            current_mode: int,
            status_publisher: Publisher
    ):
        """
        Callback for evaluating dynamics in the hybrid automaton on a timer.

        At regular time intervals, this function evaluates the dynamics associated with the 
        current mode of the hybrid automaton.

        We publish dynamics based on agent_state and other states assigend to the dynamic controllers
        in the hybrid automaton dynamics module, we publish the dynamics updates to '/hybrid_automaton/dynamics
        and at the same time if anything goes wrong we publish status updates to '/hybrid_automaton/status
        """
        try:
            with self.lock:
                self._validate_current_mode(current_mode, self.automaton)

                evaluation_result:AutomatonDynamicsEvaluation = self._evaluate_dynamics(current_mode=current_mode, hybraut_model=self.automaton, stamp=self.node.get_clock().now().to_msg())

                self.dynamics_evaluation_publisher.publish(evaluation_result)
        except Exception as e:
            status_publisher.publish(AutomatonStatus(
                type=AutomatonStatus.ERROR, 
                meesage=f"exception occured during dynamics evaluation: {str(e)}",
                stamp=self.node.get_clock().now().to_msg()
            ))

    """ === class functions === """

    def __call__(self, current_mode: int, status_publisher: Publisher):
        self.dynamics_evaluation_callback(current_mode, status_publisher)

    def __str__(self):
        """String representation of the dynamics evaluator."""
        pass

    def __repr__(self):
        """Official string representation of the dynamics evaluator."""
        pass


import rclpy
from hybraut_model import HybridAutomaton
from rclpy.executors import MultiThreadedExecutor
import threading

def main():
    rclpy.init()

    executor = MultiThreadedExecutor(num_threads=2)
    mock_node = Node('mock_node')
    executor.add_node(mock_node)

    thread = threading.Thread(target=executor.spin)
    thread.start()
    path = "/home/ryan/ros2_ws/src/hybraut_tb3/amdl/turtlebot3.amdl.yml"
    import yaml

    with open(path, 'r') as file:
        amdl_dict = yaml.safe_load(file)

    hybraut_model = HybridAutomaton.register_automaton(
        node=mock_node,
        amdl_dict=amdl_dict
    )

    hybraut_dynamic_evaluator = HybrautDynamicEvaluator(
        node=mock_node,
        automaton=hybraut_model
    )
    
    hybraut_dynamic_evaluator(
        current_mode=0,
        status_publisher=None
    )

    rclpy.shutdown()

if __name__ == '__main__':
    main()


# import rclpy
# from rclpy.qos import QoSProfile
# from rclpy.executors import MultiThreadedExecutor
# from hybraut_model import HybridAutomaton

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
#     dynamics_evaluation_publisher = mock_node.create_publisher(
#         topic = '/hybrid_automaton/dynamics',
#         msg_type = HybridAutomatonDynamicsEvaluation,
#         qos_profile = QoSProfile(depth=10)
#     ) 
#     status_publisher = mock_node.create_publisher(
#         topic = '/hybrid_automaton/status',
#         msg_type = HybridAutomatonStatus,
#         qos_profile = QoSProfile(depth=10)
#     )

#     threading.Thread(target=executor.spin).start()
    
#     dynamics_evaluation_callback(
#         lock=lock,
#         automaton_model=automaton_model,
#         stamp=stamp,
#         dynamics_evaluation_publisher=dynamics_evaluation_publisher,
#         status_publisher=status_publisher
#     )

#     rclpy.shutdown()