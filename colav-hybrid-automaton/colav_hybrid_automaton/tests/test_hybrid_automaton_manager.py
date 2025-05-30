import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from hybrid_automaton_interfaces.action import HybridAutomaton
from builtin_interfaces.msg import Time
from unique_identifier_msgs.msg import UUID
from colav_interfaces.msg import Waypoint, Waypoints
from hybrid_automaton.utils import get_current_ros_time
from geometry_msgs.msg import Pose, Point32, Quaternion
from unique_identifier_msgs.msg import UUID
import uuid
import time
import numpy as np

SYSTEM_CLOCK = None


class HybridAutomatonClient(Node):
    def __init__(self):
        super().__init__('hybrid_automaton_client')
        self._action_client = ActionClient(
            self, HybridAutomaton, '/colav/hybrid_automaton/hybrid_automaton_action_server')

    def send_goal(self):
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        goal_msg = HybridAutomaton.Goal()
        goal_msg.stamp = get_current_ros_time()

        # # Create UUIDs
        mission_uuid = uuid.uuid4()
        agent_uuid = uuid.uuid4()

        # Create ROS 2 UUID messages and assign byte arrays
        goal_msg.mission_uuid = UUID(uuid=np.frombuffer(mission_uuid.bytes, dtype=np.uint8))
        goal_msg.agent_uuid = UUID(uuid=np.frombuffer(agent_uuid.bytes, dtype=np.uint8))
        goal_msg.mission_profile = 'COLAV'
        goal_msg.goal_waypoints = Waypoints(waypoints=[Waypoint(position=Point32(x=100.0, y=100.0, z=0.0), acceptance_radius = 0.5)])

        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: success={result.success}, message="{result.message}"')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Received feedback: {feedback}')


def main():
    rclpy.init()
    node = HybridAutomatonClient()
    node.send_goal()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
