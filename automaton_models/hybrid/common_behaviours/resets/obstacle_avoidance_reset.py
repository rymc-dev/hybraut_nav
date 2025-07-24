from automaton_models.hybrid.aci_interfaces import ResetInterface
from automaton.spec import IOSpec
from std_msgs.msg import Float64
from geometry_msgs.msg import Pose
from typing import Dict, Any
from geometry_msgs.msg import Point, Quaternion

class ObstacleAvoidanceReset(ResetInterface):
    """
    Reset that adjusts navigation parameters when obstacles are detected.
    
    Modifies safety distances, velocity limits, and avoidance behaviors
    when entering obstacle avoidance mode.
    """
    
    _init_input_spec = [
        IOSpec.create_io_spec("safe_distance", float),
        IOSpec.create_io_spec("reduced_speed_factor", float),
        IOSpec.create_io_spec("avoidance_timeout", float)
    ]
    
    _state_input_spec = [
        IOSpec.create_io_spec("obstacle_distance", Float64),
        IOSpec.create_io_spec("current_max_speed", Float64),
        IOSpec.create_io_spec("robot_pose", Pose)
    ]
    
    _reset_targets_spec = [
        IOSpec.create_io_spec("safety_distance", float),
        IOSpec.create_io_spec("max_velocity", float),
        IOSpec.create_io_spec("avoidance_active", bool),
        IOSpec.create_io_spec("avoidance_start_position", tuple)
    ]
    
    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:
        
        current_max_speed = state_kwargs["current_max_speed"].data
        robot_pose = state_kwargs["robot_pose"]
        
        # Reduce speed for obstacle avoidance
        reduced_speed = current_max_speed * self.reduced_speed_factor
        
        # Store position where avoidance started
        avoidance_start_position = (
            robot_pose.position.x,
            robot_pose.position.y,
            robot_pose.position.z
        )
        
        return {
            'safety_distance': self.safe_distance,
            'max_velocity': reduced_speed,
            'avoidance_active': True,
            'avoidance_start_position': avoidance_start_position
        }
    

def main():
    # Instantiate the reset logic with initialization parameters
    reset = ObstacleAvoidanceReset(
        safe_distance=2.5,
        reduced_speed_factor=0.5,
        avoidance_timeout=10.0
    )

    # Create dummy state inputs
    obstacle_distance = Float64(data=1.2)
    current_max_speed = Float64(data=3.0)

    pose = Pose()
    pose.position = Point(x=10.0, y=5.0, z=0.0)
    pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

    # Call the reset method
    output = reset(
        obstacle_distance=obstacle_distance,
        current_max_speed=current_max_speed,
        robot_pose=pose
    )

    # Print the reset outputs
    print("ObstacleAvoidanceReset Output:")
    for key, value in output.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()