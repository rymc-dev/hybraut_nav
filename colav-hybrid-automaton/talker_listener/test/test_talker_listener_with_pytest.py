# import os
# import sys
# import time
# import uuid

# import pytest
# import launch
# import launch_ros
# import launch_testing.actions

# import rclpy
# from std_msgs.msg import String

# # --- ROS init/shutdown fixture ---
# @pytest.fixture(scope='session', autouse=True)
# def ros_init_shutdown():
#     rclpy.init()
#     yield
#     rclpy.shutdown()

# # --- Node fixture ---
# @pytest.fixture
# def node():
#     test_node = rclpy.create_node('test_talker_listener')
#     yield test_node
#     try:
#         test_node.destroy_node()
#     except Exception:
#         pass

# # --- Generate launch description for rostest ---
# @pytest.mark.rostest
# def generate_test_description():
#     file_path = os.path.dirname(__file__)

#     listener_node = launch_ros.actions.Node(
#         executable=sys.executable,
#         arguments=[os.path.join(file_path, '..', 'talker_listener', 'listener_node.py')],
#         additional_env={'PYTHONBUFFERED': '1'},
#         parameters=[{"topic": "talker_chatter"}]
#     )

#     talker_node = launch_ros.actions.Node(
#         executable=sys.executable,
#         arguments=[os.path.join(file_path, '..', 'talker_listener', 'talker_node.py')],
#         additional_env={'PYTHONBUFFERED': '1'},
#         parameters=[{"topic": "talker_chatter"}]
#     )

#     return (
#         launch.LaunchDescription([
#             talker_node,
#             listener_node,
#             launch_testing.actions.ReadyToTest()
#         ]),
#         {'talker': talker_node, 'listener': listener_node}
#     )

# # --- Test that talker publishes messages on the topic ---
# def test_talker_transmits(node, talker, proc_output):
#     msgs_rx = []

#     def callback(msg: String):
#         node.get_logger().info(f"Received: {msg.data}")
#         msgs_rx.append(msg)

#     node.create_subscription(String, 'talker_chatter', callback, 10)

#     deadline = time.time() + 10
#     while time.time() < deadline and len(msgs_rx) <= 2:
#         rclpy.spin_once(node, timeout_sec=0.1)

#     assert len(msgs_rx) > 2, f"Expected more than 2 msgs, got {len(msgs_rx)}"

# # --- Test that listener node outputs messages it receives ---
# def test_listener_receives(node, listener, proc_output):
#     publisher = node.create_publisher(String, 'talker_chatter', 10)

#     # give listener time to come up
#     time.sleep(2)
#     msg = String()
#     msg.data = str(uuid.uuid4())

#     success = False
#     for _ in range(10):
#         publisher.publish(msg)
#         if proc_output.waitFor(
#             expected_output=msg.data,
#             process=listener,
#             timeout=1.0
#         ):
#             success = True
#             break

#     assert success, f"Listener did not output the published msg {msg.data}"