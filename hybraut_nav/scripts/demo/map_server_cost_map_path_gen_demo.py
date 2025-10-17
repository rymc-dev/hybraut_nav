
def create_test_cost_map(grid_size: int = 100, resolution: float = 1.0, 
                        node: Node = None) -> OccupancyGrid:
    """
    Create a test cost map with various obstacles.
    
    Args:
        grid_size: Size of the grid (grid_size x grid_size)
        resolution: Resolution in meters per cell
        node: ROS node for getting current time
        
    Returns:
        OccupancyGrid message with obstacles
    """
    import numpy as np
    from std_msgs.msg import Header
    
    cost_map = OccupancyGrid()
    cost_map.header = Header(
        stamp=node.get_clock().now().to_msg() if node else None,
        frame_id='map'
    )
    cost_map.info.resolution = resolution
    cost_map.info.width = grid_size
    cost_map.info.height = grid_size
    cost_map.info.origin.position.x = 0.0
    cost_map.info.origin.position.y = 0.0
    cost_map.info.origin.position.z = 0.0
    cost_map.info.origin.orientation.w = 1.0

    # Initialize grid with free space
    grid_data = [0] * (grid_size * grid_size)

    # Mark unknown borders
    for i in range(grid_size):
        for j in range(grid_size):
            if i == 0 or i == grid_size-1 or j == 0 or j == grid_size-1:
                grid_data[i * grid_size + j] = -1

    # Define obstacles
    obstacles = []
    
    # Vertical wall (30-70, 50)
    obstacles.extend([(i, 50) for i in range(30, 70)])
    
    # Horizontal wall (20, 30-80)
    obstacles.extend([(20, j) for j in range(30, 80)])
    
    # Small square (70-90, 20-40)
    obstacles.extend([(i, j) for i in range(70, 90) for j in range(20, 40)])
    
    # Diagonal island
    obstacles.extend([(50 + k, 70 + k) for k in range(5) 
                     if 50 + k < grid_size and 70 + k < grid_size])
    
    # Random scattered obstacles
    np.random.seed(42)
    for _ in range(10):
        i = np.random.randint(1, grid_size - 1)
        j = np.random.randint(1, grid_size - 1)
        obstacles.append((i, j))

    # Mark obstacles
    for i, j in obstacles:
        idx = i * grid_size + j
        grid_data[idx] = 100

    # Inflate obstacles with decaying cost
    inflation_radius = 3
    for i, j in obstacles:
        for di in range(-inflation_radius, inflation_radius + 1):
            for dj in range(-inflation_radius, inflation_radius + 1):
                ni, nj = i + di, j + dj
                if 0 <= ni < grid_size and 0 <= nj < grid_size:
                    distance = np.sqrt(di**2 + dj**2)
                    if distance <= inflation_radius:
                        idx = ni * grid_size + nj
                        if grid_data[idx] == 0:  # Only inflate free cells
                            cost = int(100 * (inflation_radius - distance) / inflation_radius)
                            grid_data[idx] = max(grid_data[idx], cost)

    cost_map.data = grid_data
    return cost_map


def create_test_poses(grid_size: int = 100, 
                     frame_id: str = 'map') -> tuple[PoseStamped, PoseStamped]:
    """
    Create test start and goal poses.
    
    Args:
        grid_size: Size of the grid
        frame_id: Frame ID for poses
        
    Returns:
        Tuple of (start_pose, goal_pose)
    """
    from geometry_msgs.msg import Point, Quaternion
    from std_msgs.msg import Header
    
    header = Header(frame_id=frame_id)
    
    start_pose = PoseStamped()
    start_pose.header = header
    start_pose.pose.position = Point(x=1.5, y=1.5, z=0.0)
    start_pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

    goal_pose = PoseStamped()
    goal_pose.header = header
    goal_pose.pose.position = Point(x=grid_size - 2.5, y=grid_size - 2.5, z=0.0)
    goal_pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
    
    return start_pose, goal_pose


def visualize_path(cost_map: OccupancyGrid, start_pose: PoseStamped, 
                  goal_pose: PoseStamped, path: Path):
    """
    Visualize the planned path on the cost map.
    
    Args:
        cost_map: The occupancy grid
        start_pose: Starting position
        goal_pose: Goal position
        path: Planned path
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    grid_size = cost_map.info.width
    grid_array = [cost_map.data[i * grid_size:(i + 1) * grid_size] 
                  for i in range(grid_size)]
    grid_np = np.array(grid_array)
    
    plt.figure(figsize=(10, 10))
    plt.imshow(grid_np, cmap=plt.cm.gray_r, origin='lower', 
               extent=[0, grid_size, 0, grid_size], alpha=0.5, vmin=-1, vmax=100)
    
    plt.plot(start_pose.pose.position.x, start_pose.pose.position.y, 
             'go', label='Start', markersize=12)
    plt.plot(goal_pose.pose.position.x, goal_pose.pose.position.y, 
             'ro', label='Goal', markersize=12)
    
    x = [pose.pose.position.x for pose in path.poses]
    y = [pose.pose.position.y for pose in path.poses]
    plt.plot(x, y, 'b-o', label='Planned Path', linewidth=2)
    
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.title('Global Path Planning Visualization')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    """Main function for standalone testing of the planner node."""
    import threading
    import time
    from rclpy.executors import MultiThreadedExecutor
    from colav_interfaces.msg import AgentState
    
    rclpy.init()
    
    # Create nodes
    planner_node = StrategyNode()
    mock_node = Node('mock_node')
    mock_node.received_path = None
    
    # Create publishers
    mock_cost_map_pub = mock_node.create_publisher(OccupancyGrid, '/map', 10)
    mock_agent_state_pub = mock_node.create_publisher(AgentState, '/agent_state', 10)
    
    # Create test data
    grid_size = 100
    cost_map = create_test_cost_map(grid_size, resolution=1.0, node=planner_node)
    start_pose, goal_pose = create_test_poses(grid_size)
    
    # Create agent state
    agent_state = AgentState()
    agent_state.header = start_pose.header
    agent_state.pose = start_pose.pose

    # Setup executor
    executor = MultiThreadedExecutor(num_threads=os.cpu_count())
    executor.add_node(planner_node)
    executor.add_node(mock_node)

    def path_callback(msg: Path):
        """Callback to capture received path."""
        print('Path received!')
        mock_node.received_path = msg

    try:
        # Start executor in background
        executor_thread = threading.Thread(target=executor.spin, daemon=True)
        executor_thread.start()
        time.sleep(1.0)
        
        # Setup path subscription
        mock_node.create_subscription(
            Path, '/hybraut_nav/plan', path_callback,
            qos_profile=qos_profile, callback_group=ReentrantCallbackGroup()
        )
        time.sleep(0.5)
        
        # Publish test data
        mock_cost_map_pub.publish(cost_map)
        time.sleep(1.0)
        mock_agent_state_pub.publish(agent_state)
        time.sleep(1.0)

        # Send goal via service
        client = mock_node.create_client(SendPose, '/hybraut_nav/send_goal')
        if not client.wait_for_service(timeout_sec=5.0):
            print("Service not available!")
            return
        
        future = client.call_async(SendPose.Request(pose=goal_pose))
        rclpy.spin_until_future_complete(mock_node, future)
        print(f"Goal set successfully: {future.result().success}")

        # Wait for path
        while mock_node.received_path is None:
            rclpy.spin_once(mock_node, timeout_sec=1.0)

        print("Path planning complete!")
        print(f"Path contains {len(mock_node.received_path.poses)} waypoints")

        # Visualize result
        visualize_path(cost_map, start_pose, goal_pose, mock_node.received_path)
        time.sleep(10.0)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        executor.shutdown()
        planner_node.destroy_node()
        mock_node.destroy_node()
        rclpy.shutdown()
        if executor_thread.is_alive():
            executor_thread.join(timeout=1.0)


if __name__ == '__main__':
    main()