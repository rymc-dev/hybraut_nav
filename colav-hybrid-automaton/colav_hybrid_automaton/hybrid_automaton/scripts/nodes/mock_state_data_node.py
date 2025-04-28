import random
import rclpy
from rclpy.node import Node
from colav_interfaces.msg import ObstaclesUpdate, AgentUpdate, StaticObstacle, DynamicObstacle, UnsafeSet
from geometry_msgs.msg import Pose, Point, Quaternion
from std_msgs.msg import Header

class MockStateDataNode(Node):
    def __init__(self):
        super().__init__('mock_state_data', namespace='hybrid_automaton')

        self.update_frequency = 10  # 10 Hz

        # Create publishers for agent state, obstacles state, and unsafe set
        self.agent_state_pub = self.create_publisher(AgentUpdate, 'agent_update', 10)
        self.obstacle_state_pub = self.create_publisher(ObstaclesUpdate, 'obstacles_update', 10)
        self.unsafe_set_pub = self.create_publisher(UnsafeSet, 'unsafe_set', 10)

        # Initialize agent starting state (at 0,0, and moving with a constant velocity)
        self.agent_position = [0.0, 0.0]
        self.agent_velocity = 10.0  # m/s (constant velocity)
        self.agent_yaw = 0.0  # Initially moving along the positive x-axis

        # Create timer to publish updates at the specified frequency
        self.create_timer(
            timer_period_sec=float(1.0 / self.update_frequency),
            callback=self.state_update
        )

    def state_update(self):
        # Create a mock AgentUpdate message
        agent_state = AgentUpdate()
        agent_state.header = Header(stamp=self.get_clock().now().to_msg())
        agent_state.mission_tag = "MockMission"
        agent_state.agent_tag = "MockAgent"

        # Update agent position (moving along the x-axis)
        self.agent_position[0] += self.agent_velocity * 0.1  # Move every update (10 Hz update)
        agent_state.pose.position = Point(x=self.agent_position[0], y=self.agent_position[1], z=0.0)  # Corrected line
        agent_state.pose.orientation = Quaternion()  # Add a valid orientation (can be adjusted if needed)
        agent_state.velocity = self.agent_velocity
        agent_state.acceleration = 0.0
        agent_state.yaw_rate = 0.0
        agent_state.beam = 5.0  # Example beam width
        agent_state.loa = 10.0  # Example length overall
        agent_state.safety_radius = 20.0  # Example safety radius

        # Publish agent state
        self.agent_state_pub.publish(agent_state)

        # Create mock ObstaclesUpdate message
        obstacles_state = ObstaclesUpdate()
        obstacles_state.header = Header(stamp=self.get_clock().now().to_msg())
        obstacles_state.mission_tag = "MockMission"

        # Static obstacles (e.g., fixed positions)
        static_obstacles = []
        for _ in range(5):  # 5 static obstacles
            static_obstacles.append(StaticObstacle(
                position=Pose(
                    position=Point(x=self.random_position(500)[0], y=self.random_position(500)[1], z=0.0),  # Corrected line
                    orientation=Quaternion() # self.random_orientation()
                )
            ))
        obstacles_state.static_obstacles = static_obstacles

        # Dynamic obstacles (e.g., moving obstacles)
        dynamic_obstacles = []
        for _ in range(3):  # 3 dynamic obstacles
            dynamic_obstacles.append(DynamicObstacle(
                position=Pose(
                    position=Point(x=self.random_position(500)[0], y=self.random_position(500)[1], z=0.0),  # Corrected line
                    orientation=Quaternion() # self.random_orientation()
                ),
                velocity=self.random_velocity(),
                yaw_rate=self.random_yaw_rate()
            ))
        obstacles_state.dynamic_obstacles = dynamic_obstacles

        # Publish obstacles state
        self.obstacle_state_pub.publish(obstacles_state)

    def random_position(self, max_range):
        # Generate random position within the specified range
        return [random.uniform(-max_range, max_range), random.uniform(-max_range, max_range)]

    def random_orientation(self):
        # Generate random orientation between 0 and 2*pi
        return random.uniform(0, 6.28)

    def random_velocity(self):
        # Random velocity between 5 and 15 m/s
        return random.uniform(5.0, 15.0)

    def random_yaw_rate(self):
        # Random yaw rate between -1 and 1 rad/s
        return random.uniform(-1.0, 1.0)


def main():
    rclpy.init()
    node = MockStateDataNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Exception occurred: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
