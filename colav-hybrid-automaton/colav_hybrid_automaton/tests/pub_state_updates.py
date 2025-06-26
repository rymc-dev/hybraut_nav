# from colav_interfaces.msg import AgentState, ObstaclesState, UnsafeSetState, Waypoint, WaypointsState
# from rclpy.node import Node

# import sys
# from geometry_msgs.msg import Point
# import os

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# import rclpy
# from std_msgs.msg import Header
# from builtin_interfaces.msg import Time

# import time
# from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy

# QOS_PROFILE = QoSProfile(
#     history=QoSHistoryPolicy.KEEP_LAST,
#     depth=10,
#     reliability=QoSReliabilityPolicy.BEST_EFFORT
# )


# rclpy.init()

# pub_node = Node('pub_node')
# agent_pub = pub_node.create_publisher(
#     AgentState,
#     '/state/agent',
#     10
# )

# obstacles_pub = pub_node.create_publisher(
#     ObstaclesState,
#     '/state/obstacles',
#     QOS_PROFILE
# )

# unsafe_set_pub = pub_node.create_publisher(
#     msg_type=UnsafeSetState,
#     topic='/state/unsafe_set/transformed',
#     qos_profile=QOS_PROFILE
# )

# # waypoints_pub = pub_node.create_publisher(
# #     '/state/waypoints_state',
# #     WaypointsState,
# #     qos_profile=QOS_PROFILE
# # )

# from geometry_msgs.msg import Point32

# waypoints_update = WaypointsState(waypoints=[Waypoint(position=Point32(x=0.0, y=0.0), acceptance_radius = 20.0), Waypoint(position=Point32(x=100.0, y=100.9), acceptance_radius=10.0)])
# # waypoints_update = Waypoints(waypoints=[Waypoint(position=Point32(x=100.0, y=0.0), acceptance_radius=10.0)])
# # waypoints_update = Waypoints(waypoints=[Waypoint(position=Point32(x=0.0, y=0.0), acceptance_radius=100.0)])
# # waypoints_update = Waypoint(position=Point32(x=100.0, y=0.0), acceptance_radius=10.0)
# # waypoints_update = Waypoints(waypoints=[Waypoint(position=Point32(x=0.0, y=0.0), acceptance_radius = 20.0) , Waypoint(position=Point32(x=100.0, y=100.0))])

# from std_msgs.msg import Header, Float64MultiArray, MultiArrayLayout, MultiArrayDimension
# from builtin_interfaces.msg import Time

# while True:
#     try:
#         now = time.time()  # seconds since epoch as float
#         sec = int(now)
#         nanosec = int((now - sec) * 1e9)

#         ros_time = Time()
#         ros_time.sec = sec
#         ros_time.nanosec = nanosec
#         from geometry_msgs.msg import Pose
#         from geometry_msgs.msg import Point
#         from geometry_msgs.msg import Quaternion
#         agent_update =AgentState(
#             header=Header(stamp=ros_time),
#             pose=Pose(
#                 position=Point(x=30.0, y=10.0),
#                 orientation=Quaternion(x=0.0, y=0.0, z=1.0, w=0.0)
#             ),
#             velocity=2.0
#         )
#         obstacles_update = ObstaclesState(header=Header(stamp=ros_time))
#         # Sample vertices for a rectangle [(1,1), (4,1), (4,3), (1,3), (1,1)] – closed polygon
#         # polygon_vertices = [1.0, 1.0,  4.0, 1.0,  4.0, 3.0,  1.0, 3.0,  1.0, 1.0]

#         # # Construct Float64MultiArray
#         # vertex_array = Float64MultiArray()
#         # vertex_array.layout = MultiArrayLayout(
#         #     dim=[MultiArrayDimension(label='vertices', size=len(polygon_vertices), stride=len(polygon_vertices))],
#         #     data_offset=0
#         # )
#         # vertex_array.data = polygon_vertices

#         # # Create the UnsafeSetState message
#         # unsafe_set_msg = UnsafeSetState()
#         # unsafe_set_msg.header = Header()
#         # unsafe_set_msg.header.stamp = rclpy.time.Time().to_msg()  # Assuming rclpy.init() has already been called
#         # unsafe_set_msg.mission_tag = "test_mission"
#         # unsafe_set_msg.vertices = vertex_array
    
#         # waypoints_pub.publish(waypoints_update)
#         agent_pub.publish(agent_update)
#         # obstacles_pub.publish(obstacles_update)
#         # unsafe_set_pub.publish(unsafe_set_msg)

#         time.sleep(0.1)
#     except KeyboardInterrupt:
#         pass

# rclpy.shutdown()
