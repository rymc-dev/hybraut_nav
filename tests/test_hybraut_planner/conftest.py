import rclpy
from rclpy.node import Node
import pytest

@pytest.fixture
def rclpy_init_shutdown():
    rclpy.init()
    yield
    rclpy.shutdown()

@pytest.fixture
def test_node_fixture(rclpy_init_shutdown):
    node = Node('test_node')
    yield node
    node.destroy_node()
    
