import os
import sys
import time
import unittest
import uuid
import pytest

import launch
import launch_ros
import launch_ros.actions
import launch_testing.actions

import rclpy

from std_msgs.msg import String

# launch feature node
@pytest.mark.rostest
def generate_test_description():
    file_path = os.path.dirname(__file__)

    # listener node
    listener_node = launch_ros.actions.Node(
        executable=sys.executable, # sys.executable python interpreted
        arguments=[os.path.join(file_path, "..", "talker_listener", "listener_node.py")],
        additional_env={'PYTHONBUFFERED':'1'}, # std::out std::error streams being sent straight to terminal in real time
        parameters=[{
            "topic": "talker_chatter"
        }]
    )

    # talker node
    talker_node = launch_ros.actions.Node(
        executable=sys.executable, # sys.executable python interpreted
        arguments=[os.path.join(file_path, "..", "talker_listener", "talker_node.py")],
        additional_env={'PYTHONBUFFERED':'1'}, # std::out std::error streams being sent straight to terminal in real time
        parameters=[{
            "topic": "talker_chatter"
        }]
    )

    return (
        launch.LaunchDescription([
            talker_node,
            listener_node,
            launch_testing.actions.ReadyToTest()
        ]),
        {
            'talker': talker_node,
            'listener': listener_node
        }
    )


# test node, test node interfaces: talker is publisher, listener is subscriber

class TestTalkerListenerLink(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize ROS context
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        # Shutdown ROS context
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_talker_listener_link')

    def tearDown(self):
        self.node.destroy_node()

    def sub_callback(self, msg: String):
        self.node.get_logger().info(f'msg received: {msg}')
        self.msgs_rx.append(msg)

    def test_talker_transmits(self, talker, proc_output):
        self.msgs_rx = []

        self.node.create_subscription(
            String,
            'talker_chatter',
            self.sub_callback,
            10
        )

        try: 
            end_time = time.time() + 10
            while time.time() < end_time:

                rclpy.spin_once(self.node, timeout_sec=0.1)
                if len(self.msgs_rx) > 2:
                    break
            
            self.assertGreater(len(self.msgs_rx), 2)

            # # make sure talker also outpus the same data via stdout
            # for msg in msgs_rx:
            #     proc_output.assertWaitFor(
            #         expected_output=msg.data, process=talker
            #     )

        finally:
            self.node.destroy_node()

        assert True

    def test_listener_receives(self, listener, proc_output):
        pub = self.node.create_publisher(
            String,
            'talker_chatter',
            10
        )

        time.sleep(2)
        try:
            msg = String()
            msg.data = str(uuid.uuid4())
            for _ in range(10):
                pub.publish(msg)
                success = proc_output.waitFor(
                    expected_output=msg.data,
                    process=listener,
                    timeout=1.0
                )
                if success:
                    break
            assert success, 'waiting for output timed out'
        finally:
            self.node.destroy_node()

        assert True