import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
import threading
from hybraut_nav_strategy import PlannerNode

rclpy.init()

planner_node: PlannerNode = PlannerNode()
cli_node: Node = Node("planner_test_cli_node")
executor = MultiThreadedExecutor()
executor.add_node(planner_node)
executor.add_node(cli_node)

spin_thread = threading.Thread(target=executor.spin, daemon=True)
spin_thread.start()

print(
    "Planner Node Default Initialization:",
    f"\n\tPlanner Type: {planner_node.get_planner_type()}",
    f"\n\tPlanner Active: {planner_node.is_active()}",
    f"\n\tPlanner Frequency: {planner_node.get_planner_frequency()}",
    f"\n\tMax Planning Time: {planner_node.get_max_planning_time()}"
)

import time
time.sleep(2.0)

from nav_msgs.msg import Path
from rclpy.callback_groups import ReentrantCallbackGroup
from hybraut_interfaces.srv import SendPose
from rclpy.client import Client
from rclpy.qos import qos_profile_system_default
# cli_node.create_subscription(
#     Path,
#     '/hybraut_nav/plan',
#     lambda msg: print(f"Received new plan with {len(msg.poses)} poses."),
#     qos_profile=qos_profile_system_default,
#     callback_group=ReentrantCallbackGroup()
# )
send_goal_cli:Client = cli_node.create_client(
    SendPose,
    '/hybraut_nav/send_goal',
    # qos_profile=qosprofile_system_default,
    callback_group=ReentrantCallbackGroup()
)
if send_goal_cli.wait_for_service(timeout_sec=5.0) is False:
    print("Service not available, waiting...")
    
from geometry_msgs.msg import PoseStamped, Pose

future = send_goal_cli.call_async(SendPose.Request(pose=PoseStamped(pose=Pose(x=480, y=480, z=0.0))))
rclpy.spin_until_future_complete(cli_node, future)
if future.result() is not None and future.result().success: 
    print ("Successfully send goal to the planner.")
    
import time
time.sleep(1.0)

assert planner_node.is_active() is True
print ('planner node is active after sending goal.')

time.sleep(40.0)

rclpy.shutdown()