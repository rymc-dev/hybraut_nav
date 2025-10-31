"""
a test file for testing the execution engine
"""

import rclpy
from rclpy.node import Node

from rclpy.executors import MultiThreadedExecutor

from tactical_execution_engine.execution_engine import ExecutionEngine
from hybraut_model_factory.amdl import HybridAutomatonFactory
from hybraut_model_diag_gen.generator import HybrautDiag

import yaml

import threading


def main(amdl_path, generate_diagram: bool = False):

    rclpy.init()

    executor = MultiThreadedExecutor(num_threads=4)
    node: Node = Node("execution_engine_node")
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    if amdl_path is None:
        raise ValueError("amdl_path is required")

    with open(amdl_path, "r") as f:
        amdl_data = yaml.safe_load(f)

    factory: HybridAutomatonFactory = HybridAutomatonFactory()
    hybraut_model = factory.register_automaton(amdl_data)

    if generate_diagram:
        # will use the diagram generator in here.
        pass

    execution_engine: ExecutionEngine = ExecutionEngine(
        node=node, hybraut_model=hybraut_model
    )

    execution_engine.activate()

    import time

    time.sleep(30.0)

    execution_engine.deactivate()

    rclpy.shutdown()


if __name__ == "__main__":
    main("/home/ryan/ros2_ws/src/hybraut_ros2/example_amdls/hybraut_tb3.amdl.yml")
