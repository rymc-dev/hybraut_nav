#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Smoke testing for the StateBus class in the hybraut_exection_engine.watchdog.hybraut_bus module.
"""

import pytest

import rclpy
from rclpy.executors import MultiThreadedExecutor, Executor
import os
from rclpy.node import Node
import threading
from hybraut_interfaces.msg import State
from hybraut_execution_engine.watchdog.hybraut_bus.state_bus import StateBus, StateEnum

from rclpy.qos import QoSProfile, qos_profile_system_default

QOS = qos_profile_system_default

@pytest.fixture
def node_fixture():
    """ 
    create a mock node for testing purposes
    """
    rclpy.init()
    executor: Executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    node = Node("mock_node")
    executor.add_node(node)
    
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    
    yield node
    
    rclpy.shutdown()

@pytest.fixture
def publisher_fixture(setup_node: Node):
    """ 
    create a publisher to the /automaton/state topic for testing purposes
    """
    node: Node = setup_node
    state_publisher = node.create_publisher(
        msg_type=State,
        topic='/automaton/state',
        qos_profile=QOS
    )
    yield state_publisher
    node.destroy_publisher(state_publisher)
    
@pytest.fixture
def state_bus_fixture(setup_node: Node):
    """ 
    create a state bus for testing purposes
    """
    node: Node = setup_node
    received_messages = []
    
    def status_callback(msg):
        received_messages.append(msg)
    
    state_bus = StateBus(
        node=node,
        status_callback=status_callback,
        topic="/automaton/state",
        qos=QOS
    )
    
    yield state_bus, received_messages
    node.destroy_subscription(state_bus.subscription)

@pytest.mark.usefixtures("state_bus_fixture", "publisher_fixture")
class TestStateBus:
    """ 
    This class contains tests for the state bus class.
    ensuring that the 
    """
    
    @pytest.mark.order(1)
    def test_state_bus_initialization(self, setup_node):
        """
        Test the initialization of the StateBus class.
        """
        ... 
        
    @pytest.parameterze(
        "state, message, stamp"    
    )
    def test_bus_publish(self, state, message, stamp, setup_node):
        """ 
        tests several different states from hybraut_interfaces and validates that 
        when published, they are received correctly by the state bus subscription.
        """

def main():
    """
    Main function to demonstrate the usage of EventBus.
    This is just a placeholder and should be replaced with actual usage.
    """
    import rclpy
    from rclpy.executors import MultiThreadedExecutor, Executor
    import os
    import threading

    rclpy.init()
    executor: Executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    node = Node("mock_node")
    executor.add_node(node)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()

    try:
        status_bus: StateBus = StateBus(
            node=node,
            status_callback=lambda msg: print(
                f"Received state: {msg.type}, Message: {msg.message}"
            ),
        )
        status_bus.publish(StateEnum.ACTIVE, "watchdog state: ACTIVE")
        import time

        time.sleep(0.01)
        status_bus.publish(StateEnum.TRANSITIONING, "watchdog state: TRANSITIONING")
        time.sleep(0.01)

        time.sleep(0.01)
        status_bus.publish(StateEnum.FATAL, "watchdog state: FATAL")
        time.sleep(0.01)
        
        status_bus.publish(StateEnum.SYSTEM_SHUTDOWN, "watchdog state: SYSTEM_SHUTDOWN")
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
    finally:
        executor.shutdown()
        thread.join()
        node.destroy_node()

    rclpy.shutdown()

if __name__ == "__main__":
    main()
