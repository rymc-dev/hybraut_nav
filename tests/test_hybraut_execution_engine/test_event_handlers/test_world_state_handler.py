"""
Test Suite for the WorldStateHandler
contains several tests covering possible scenarios for this class.
"""

from geometry_msgs.msg import PoseStamped
from hybraut_execution_engine.event_handlers.world_state_update_handler import (
    WorldStateHandler,
)
from hybraut_execution_engine.event_handlers.world_state_update_handler import (
    WorldStateHandlerHub,
)
import pytest
import rclpy
from rclpy.node import Node
from hybraut_model.states import State, StateRegistry


@pytest.fixture
def initialize_mock_rclpy_and_node():
    import rclpy
    from rclpy.node import Node
    import threading
    import os
    from rclpy.executors import MultiThreadedExecutor

    rclpy.init()
    mock_node = Node("mock_node")
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(mock_node)

    thread = threading.Thread(target=executor.spin)
    thread.start()

    yield mock_node

    executor.shutdown()
    rclpy.shutdown()


class TestWorldStateHandler:
    """
    test suite for the WorldStateHandler,
    this test suite tests individual state handlers
    as well as the hub, and class methods which generate
    state handler hub based on .amdl state definitions
    """

    def __init__(self, initialize_mock_rclpy_and_node):
        self.mock_node: Node = initialize_mock_rclpy_and_node
        from typing import List

        self.states: List[PoseStamped] = self.initialize_world_state_test_dependencies

    @pytest.fixture
    def get_sample_state_amdl(self):
        """
        return an individual sample state for WorldStateHandlerTest
        """
        return "current_pose", {
            "topic": "/tb3/pose",
            "type": {"pkg": "geometry_msgs.msg", "msg": "PoseStamped"},
        }

    @pytest.fixture
    def initialize_world_state_test_dependencies(self):

        from rclpy.callback_groups import ReentrantCallbackGroup
        from rclpy.qos import qos_profile_system_default

        states = []

        def state_callback(msg: PoseStamped):
            states.append(states)

        self.state_subscription = self.mock_node.create_subscription(
            msg_type=PoseStamped(),
            topic="/tb3/pose",
            callback=lambda msg: state_callback(msg),
            callback_group=ReentrantCallbackGroup(),
            qos_profile=qos_profile_system_default,
        )

        yield states

        self.mock_node.destroy_subscription(self.state_subscription)

    def test_state_initialization_and_attributes(self):
        try:
            state_name, state_conf = self.get_sample_state_amdl
            from hybraut_model.automaton_types.msg_type import MsgType

            msg_type = MsgType(**state_conf.get("type", None))
            msg_type = msg_type.import_msg_type()

            state: State = State(
                name=state_name, topic=state_conf["topic"], msg_type=msg_type
            )
            mock_world_state_handler = WorldStateHandler.create(
                node=self.mock_node, state=state
            )
        except Exception as e:
            assert False, f"Unexpected Excetion occured during tests: '', : {str(e)}"

        # ok, lets validate the structure of the mock_world_state_handler here
        # making assertions throughout to test validatity.

        assert True


class TestWorldStateHandlerHub:
    """
    test suite for the world state handler hub
    """

    def __init__(self, initialize_mock_rclpy_and_node):
        self.mock_node = initialize_mock_rclpy_and_node

    @pytest.fixture
    def get_states_amdl(self):
        """
        returns a set of states from amdl
        """
        return {
            "states": {
                "current_pose": {
                    "topic": "/tb3/pose",
                    "type": {"pkg": "geometry_msgs.msg", "msg": "PoseStamped"},
                }
            },
            "goal_pose": {
                "topic": "/tb3/goal",
                "type": {"pkg": "geometry_msgs.msg", "msg": "PoseStamped"},
            },
        }
