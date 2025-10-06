# !/usr/bin/env python3

""" 
Layer one of the hybraut navigation stack: the global planner.
This node subscribes to global cost map updates, goal poses, and agent states, this operates on a timer, when a new goal is received it will plan a global path which can be passed to layer two (the local planner hybrid automaton), 
which is the passed to a controller.
"""

import rclpy
from rclpy.node import Node
import threading
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped

# hybraut_interfaces should contain agent state 
from colav_interfaces.msg import AgentState
import sys
import os
from rclpy.qos import QoSProfile, QoSDurabilityPolicy

qos_profile = QoSProfile(depth=10)
qos_profile.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from path_planning import RRTStar, RRT, Dijkstra, AStar, Planner, Grid as PlannerGrid, Point as PlannerPoint

from rcl_interfaces.msg import ParameterDescriptor
from enum import Enum
from hybraut_interfaces.srv import SendPose
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.timer import Timer
from std_srvs.srv import Trigger

class PlannerState(Enum):
    """Enumeration for planner states"""
    INACTIVE = "inactive"
    ACTIVE = "active"

class PlannerType(Enum):
    ASTAR = 'A*'
    DIJKSTRA = 'Dijkstra'
    RRT = 'RRT'
    RRTSTAR = 'RRT*'
    
    @staticmethod
    def from_string(planner_type_str: str) -> 'PlannerType':
        """Return the PlannerType enum member matching the given string."""
        for pt in PlannerType:
            if pt.value == planner_type_str:
                return pt
        raise ValueError(f'Unknown planner type string: {planner_type_str}')

    @staticmethod
    def initialize_planner(planner_type: 'PlannerType') -> object:
        match planner_type:
            case PlannerType.ASTAR:
                return AStar()
            case PlannerType.DIJKSTRA:
                return Dijkstra()
            case PlannerType.RRT:
                return RRT()
            case PlannerType.RRTSTAR:
                return RRTStar()
            case _:
                raise ValueError(f'Unknown planner type: {planner_type}')

class PlannerNode(Node):
    """
    Global planner for the hybrid navigation stack.
    Plans a global path from the agent's current position to a goal position using a specified planning algorithm.
    """

    def __init__(self, *args, **kwargs):
        super().__init__('planner', namespace='hybraut_nav', *args, **kwargs)

        self.state = PlannerState.INACTIVE
        self.current_cost_map = None
        self.current_agent_pose = None
        self.current_goal_pose = None

        # Declare parameters
        self.declare_parameter(
            'planner_frequency', 0.1, 
            ParameterDescriptor(description='Frequency to replan the global path in Hz, default is 0.1 Hz (every 10 seconds)')
        )
        self.declare_parameter(
            'planner_type', 'A*',
            ParameterDescriptor(description='Type of global planner to use, options are A*, Dijkstra, RRT, RRT*, default is A*')
        )
        self.declare_parameter(
            'max_planning_time', 5.0,
            ParameterDescriptor(description='Maximum time allowed for planning in seconds, default is 5.0 seconds')
        )
        self.declare_parameter(
            'description',
            "This node handles global path planning using various algorithms for the hybraut_nav stack."
        )

        # Set the initial planner
        planner_type_str = self.get_parameter('planner_type').get_parameter_value().string_value
        self.set_planner(PlannerType.from_string(planner_type_str))

        # Service to set goal pose
        self.create_service(
            SendPose,
            'send_goal',
            self.set_goal_callback,
            callback_group=MutuallyExclusiveCallbackGroup()
        )
        
        self.create_service(
            Trigger,
            'deactivate',
            self._deactivate_callback,
            callback_group=MutuallyExclusiveCallbackGroup()
        )

        # Parameter change callback
        self.add_on_set_parameters_callback(self.parameter_callback)

        # Subscriptions
        self.create_subscription(
            OccupancyGrid,
            '/map',
            self._cost_map_callback,
            10,
            callback_group=ReentrantCallbackGroup()
        )
        self.create_subscription(
            AgentState,
            '/agent_state',
            self._agent_state_callback,
            10,
            callback_group=ReentrantCallbackGroup()
        )

        # Publisher
        self.plan_publisher = self.create_publisher(
            Path,
            'plan',
            qos_profile=qos_profile,
            callback_group=ReentrantCallbackGroup()
        )
        self.goalpose_publisher = self.create_publisher(
            PoseStamped,
            'goalpose',
            qos_profile=qos_profile,
            callback_group=ReentrantCallbackGroup()
        )
        
        # Timer
        planner_frequency = self.get_parameter('planner_frequency').value
        self.planner_timer = self.create_timer(
            1.0 / planner_frequency,
            self.plan_path_callback,
            autostart=(self.state == PlannerState.ACTIVE),
            callback_group=ReentrantCallbackGroup()
        )

    def _deactivate_callback(self, request: Trigger.Request, response: Trigger.Response):
        """deactivate the planner, stopping any ongoing planning and setting state to INACTIVE."""
        self.state = PlannerState.INACTIVE
        self.planner_timer.cancel()
        self.current_goal_pose = None
        response.success = True
        return response

    def _cost_map_callback(self, msg):
        self.current_cost_map = msg

    def _agent_state_callback(self, msg):
        self.current_agent_pose = PoseStamped(header=msg.header, pose=msg.pose)

    def set_planner(self, planner_type: PlannerType):
        try:
            self.planner = PlannerType.initialize_planner(planner_type)
        except ValueError as e:
            self.get_logger().error(str(e))

    def parameter_callback(self, params):
        from rcl_interfaces.msg import SetParametersResult

        for param in params:
            if param.name == 'planner_frequency':
                self.planner_timer.cancel()
                self.planner_timer = self.create_timer(
                    1.0 / param.value,
                    self.plan_path_callback,
                    autostart=(self.state == PlannerState.ACTIVE)
                )
                self.get_logger().info(f'Replan frequency set to {param.value} Hz')
            elif param.name == 'planner_type':
                self.set_planner(PlannerType.from_string(param.value))
                self.get_logger().info(f'Planner type set to {param.value}')
            elif param.name == 'planner_active':
                old_state = self.state
                self.state = PlannerState.ACTIVE if param.value else PlannerState.INACTIVE
                self._handle_state_transition(old_state, self.state)
                self.get_logger().info(f'Planner state changed to: {self.state.value}')
            elif param.name == 'event_horizon':
                self.get_logger().info(f'Event horizon set to {param.value} meters')

        return SetParametersResult(successful=True)

    def set_goal_callback(self, request: SendPose.Request, response: SendPose.Response):
        self.current_goal_pose = request.pose
        if self.state == PlannerState.INACTIVE:
            self.state = PlannerState.ACTIVE
            self.planner_timer.reset()
        response.success = True
        return response

    def is_active(self):
        return self.state == PlannerState.ACTIVE

    def plan_path_callback(self):
        self.goalpose_publisher.publish(self.current_goal_pose)
        if not self.is_active():
            self.planner_timer.cancel()
            return

        if not all([self.current_agent_pose, self.current_goal_pose, self.current_cost_map]):
            self.get_logger().debug("Missing required data for planning")
            return

        try:
            path = self.plan_path(self.current_agent_pose, self.current_goal_pose)
            if path:
                self.publish_path(path)
        except Exception as e:
            self.get_logger().error(f"Planning failed: {str(e)}")

    def plan_path(self, start: PoseStamped, goal: PoseStamped) -> Path:
        grid = PlannerGrid.from_ros_msg(self.current_cost_map)
        start_pt = PlannerPoint.from_ros_msg(start)
        goal_pt = PlannerPoint.from_ros_msg(goal)
        return self.planner.plan_path(grid, start_pt, goal_pt)

    def publish_path(self, path: Path):
        self.plan_publisher.publish(path)


""" === code below is for testing the planner node independently === """

def main():
    import rclpy
    from rclpy.node import Node
    from rclpy.executors import MultiThreadedExecutor
    from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped
    from std_msgs.msg import Header
    from nav_msgs.msg import OccupancyGrid, Path
    from colav_interfaces.msg import AgentState
    from hybraut_interfaces.srv import SendPose
    from rclpy.callback_groups import ReentrantCallbackGroup
    import threading
    import numpy as np
    import os
    import time

    rclpy.init()
    
    node = PlannerNode()
    
    mock_node = Node('mock_node')
    mock_node.__setattr__('received_path', None)
    mock_cost_map_publisher = mock_node.create_publisher(OccupancyGrid, '/map', 10)
    mock_agent_state_publisher = mock_node.create_publisher(AgentState, '/agent_state', 10)
    
    grid_size = 100
    resolution = 1.0
    cost_map = OccupancyGrid()
    cost_map.header = Header(stamp=node.get_clock().now().to_msg(), frame_id='map')
    cost_map.info.resolution = resolution
    cost_map.info.width = grid_size
    cost_map.info.height = grid_size
    cost_map.info.origin.position.x = 0.0
    cost_map.info.origin.position.y = 0.0
    cost_map.info.origin.position.z = 0.0
    cost_map.info.origin.orientation.w = 1.0

    # Initialize grid
    grid_data = [0] * (grid_size * grid_size)

    # Unknown border
    for i in range(grid_size):
        for j in range(grid_size):
            if i == 0 or i == grid_size-1 or j == 0 or j == grid_size-1:
                grid_data[i*grid_size + j] = -1

    # --- Place obstacles ---
    obstacles = []

    # Vertical wall
    for i in range(30, 70):
        for j in range(50, 51):
            idx = i*grid_size + j
            grid_data[idx] = 100
            obstacles.append((i, j))

    # Horizontal wall
    for i in range(20, 21):
        for j in range(30, 80):
            idx = i*grid_size + j
            grid_data[idx] = 100
            obstacles.append((i, j))

    # Small square
    for i in range(70, 90):
        for j in range(20, 40):
            idx = i*grid_size + j
            grid_data[idx] = 100
            obstacles.append((i, j))

    # Diagonal island
    for k in range(5):
        i = 50 + k
        j = 70 + k
        if i < grid_size and j < grid_size:
            idx = i*grid_size + j
            grid_data[idx] = 100
            obstacles.append((i, j))

    # Random scattered
    np.random.seed(42)
    for _ in range(10):
        i = np.random.randint(1, grid_size-1)
        j = np.random.randint(1, grid_size-1)
        idx = i*grid_size + j
        grid_data[idx] = 100
        obstacles.append((i, j))

    # --- Inflate obstacles properly (circular, decaying cost) ---
    inflation_radius = 3  # in cells
    for i, j in obstacles:
        for di in range(-inflation_radius, inflation_radius + 1):
            for dj in range(-inflation_radius, inflation_radius + 1):
                ni = i + di
                nj = j + dj
                if 0 <= ni < grid_size and 0 <= nj < grid_size:
                    distance = np.sqrt(di**2 + dj**2)
                    if distance <= inflation_radius:
                        idx = ni*grid_size + nj
                        if grid_data[idx] == 0:  # only inflate free cells
                            # linear decay: closer to obstacle -> higher cost
                            cost = int(100 * (inflation_radius - distance) / inflation_radius)
                            grid_data[idx] = max(grid_data[idx], cost)


    cost_map.data = grid_data

    # Start & goal poses
    start_pose = PoseStamped()
    start_pose.header = cost_map.header
    start_pose.pose.position = Point(x=1.5, y=1.5, z=0.0)
    start_pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

    goal_pose = PoseStamped()
    goal_pose.header = cost_map.header
    goal_pose.pose.position = Point(x=grid_size-2.5, y=grid_size-2.5, z=0.0)
    goal_pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

    # Agent state
    agent_state = AgentState()
    agent_state.header = start_pose.header
    agent_state.pose = start_pose.pose

    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(node)
    executor.add_node(mock_node)

    def path_callback(msg: Path):
        print('path received')
        mock_node.received_path = msg

    try:
        executor_thread = threading.Thread(target=executor.spin, daemon=True)
        executor_thread.start()
        time.sleep(1.0)
        mock_node.create_subscription(
            Path,
            '/hybraut_nav/plan',
            path_callback,
            qos_profile=qos_profile,
            callback_group=ReentrantCallbackGroup()
        )
        time.sleep(0.5)
        mock_cost_map_publisher.publish(cost_map)
        time.sleep(1.0)
        mock_agent_state_publisher.publish(agent_state)
        time.sleep(1.0)

        client = mock_node.create_client(SendPose, '/hybraut_nav/send_goal')
        if not client.wait_for_service(timeout_sec=5.0):
            print("Service not available!")
        else:
            future = client.call_async(SendPose.Request(pose=goal_pose))
            rclpy.spin_until_future_complete(mock_node, future)
            print(future.result().success)

        while mock_node.received_path is None:
            rclpy.spin_once(mock_node, timeout_sec=1.0)

        print("Received path:")
        print(mock_node.received_path)

        import matplotlib.pyplot as plt
        grid_array = [cost_map.data[i*grid_size:(i+1)*grid_size] for i in range(grid_size)]
        grid_np = np.array(grid_array)
        cmap = plt.cm.gray_r
        plt.imshow(grid_np, cmap=cmap, origin='lower', extent=[0, grid_size, 0, grid_size], alpha=0.5,
                   vmin=-1, vmax=100)
        plt.plot(start_pose.pose.position.x, start_pose.pose.position.y, 'go', label='Start', markersize=12)
        plt.plot(goal_pose.pose.position.x, goal_pose.pose.position.y, 'ro', label='Goal', markersize=12)
        x = [pose.pose.position.x for pose in mock_node.received_path.poses]
        y = [pose.pose.position.y for pose in mock_node.received_path.poses]
        plt.plot(x, y, 'b-o', label='Planned Path')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True)
        plt.axis('equal')
        plt.legend()
        plt.show()
        time.sleep(10.0)

    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()
        executor_thread.join()

if __name__ == '__main__':
    main()
