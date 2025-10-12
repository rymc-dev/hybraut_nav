from hybraut_execution_engine.evaluators.invariants import InvariantEvaluator

import rclpy
from rclpy.node import Node
import threading
from rclpy.executors import MultiThreadedExecutor
import yaml
from hybraut_factory.amdl import HybridAutomatonFactory
from rclpy.publisher import Publisher
from hybraut_interfaces.msg import TransitionEvent

from hybraut_execution_engine.internal_state import EngineAutomatonStateTracker


QOS = rclpy.qos.qos_profile_system_default
CB_GROUP = rclpy.callback_groups.ReentrantCallbackGroup()


def main(**kwargs):
    amdl_path = kwargs.get("amdl_path")
    if amdl_path is None:
        raise ValueError("amdl_path is required")

    with open(amdl_path, "r") as f:
        amdl_data = yaml.safe_load(f)

    factory: HybridAutomatonFactory = HybridAutomatonFactory()
    hybraut_model = factory.register_automaton(amdl_data)

    rclpy.init()
    executor = MultiThreadedExecutor(num_threads=4)
    node = Node("node")
    event_publisher: Publisher = node.create_publisher(
        TransitionEvent, "/automaton/events", qos_profile=QOS, callback_group=CB_GROUP
    )
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    engine_state_tracker: EnvironmentError = EngineAutomatonStateTracker(
        node=node, initial_mode=0, q_goals=[1]
    )

    invariant_evaluator: InvariantEvaluator = InvariantEvaluator(
        node=node,
        state_tracker=engine_state_tracker,
        automaton=hybraut_model,
        event_publisher=event_publisher,
    )

    import time

    def evaluation_callback():

        while True:
            time.sleep(0.2)
            invariant_evaluator()

    # TODO: Need to look into why invariant statuses is not showing all the invariants invformation.
    thread1 = threading.Thread(target=evaluation_callback)
    thread1.start()

    time.sleep(10.0)

    executor.shutdown()
    rclpy.shutdown()


if __name__ == "__main__":
    kwargs = {
        "amdl_path": "/home/ryan/ros2_ws/src/hybraut_ros2/example_amdls/hybraut_tb3.amdl.yml"
    }
    main(**kwargs)
