

from typing import Dict, Any, List
from geometry_msgs.msg import Point, Pose, Twist
from std_msgs.msg import Bool, Float64, Int32
from nav_msgs.msg import Path
from automaton_models.hybraut_model.aci_interfaces import ResetInterface
from automaton.spec.io_spec import IOSpec


class WaypointAdvanceReset(ResetInterface):
    """
    Reset that advances to the next waypoint in a navigation sequence.
    
    This reset is commonly used in path following systems when the robot
    reaches a waypoint and needs to target the next one in sequence.
    """
    
    _init_input_spec = [
        IOSpec.create_io_spec("wrap_around", bool),
        IOSpec.create_io_spec("increment_step", int)
    ]
    
    _state_input_spec = [
        IOSpec.create_io_spec("current_waypoint_index", Int32),
        IOSpec.create_io_spec("waypoint_path", Path),
        IOSpec.create_io_spec("robot_pose", Pose)
    ]
    
    _reset_targets_spec = [
        IOSpec.create_io_spec("current_waypoint_index", int),
        IOSpec.create_io_spec("target_waypoint_position", tuple),
        IOSpec.create_io_spec("waypoint_reached", bool)
    ]
    
    def _evaluate(self, **state_kwargs):
        current_index = state_kwargs["current_waypoint_index"].data
        waypoint_path = state_kwargs["waypoint_path"]
        
        # Calculate next waypoint index
        next_index = current_index + self.increment_step
        
        # Handle wrap around or clamp to last waypoint
        if next_index >= len(waypoint_path.poses):
            if self.wrap_around:
                next_index = 0
            else:
                next_index = len(waypoint_path.poses) - 1
        
        # Get target position
        target_pose = waypoint_path.poses[next_index].pose
        target_position = (
            target_pose.position.x,
            target_pose.position.y,
            target_pose.position.z
        )
        
        # Check if we've reached the final waypoint
        waypoint_reached = (next_index == len(waypoint_path.poses) - 1) and not self.wrap_around
        
        return {
            'current_waypoint_index': next_index,
            'target_waypoint_position': target_position,
            'waypoint_reached': waypoint_reached
        }

    
def main():
    from std_msgs.msg import Int32
    from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
    from nav_msgs.msg import Path

    # Create a test path with 3 waypoints
    path = Path()
    path.poses = []

    for i in range(3):
        pose_stamped = PoseStamped()
        pose_stamped.pose.position = Point(x=i * 1.0, y=i * 2.0, z=0.0)
        pose_stamped.pose.orientation = Quaternion(x=0, y=0, z=0, w=1)
        path.poses.append(pose_stamped)

    # Initial index: 0
    current_waypoint_index = Int32(data=0)

    # Robot pose (not used in logic, but required by interface)
    robot_pose = Pose(position=Point(x=0, y=0, z=0), orientation=Quaternion(x=0, y=0, z=0, w=1))

    # Instantiate the reset behavior
    waypoint_advance_reset = WaypointAdvanceReset(wrap_around=True, increment_step=1)

    # Call the reset
    result = waypoint_advance_reset(
        current_waypoint_index=current_waypoint_index,
        waypoint_path=path,
        robot_pose=robot_pose
    )

    print("Reset Result:")
    for key, val in result.items():
        print(f"  {key}: {val}")

if __name__ == '__main__':
    main()