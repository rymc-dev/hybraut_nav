from hybraut_aci import ResetInterface, IOSpec
from geometry_msgs.msg import Pose
from typing import Dict, Any
from geometry_msgs.msg import Point, Quaternion


class PoseReset(ResetInterface):
    """
    Reset that updates robot target pose or reference frame.

    Used when switching between different navigation targets or
    coordinate frames during operation.
    """

    _init_input_spec = [
        IOSpec.create_io_spec("target_frame", str),
        IOSpec.create_io_spec("position_tolerance", float),
        IOSpec.create_io_spec("orientation_tolerance", float),
    ]

    _state_input_spec = [
        IOSpec.create_io_spec("new_target_pose", Pose),
        IOSpec.create_io_spec("current_pose", Pose),
    ]

    _reset_targets_spec = [
        IOSpec.create_io_spec("target_position", tuple),
        IOSpec.create_io_spec("target_orientation", tuple),
        IOSpec.create_io_spec("reference_frame", str),
        IOSpec.create_io_spec("pose_tolerance", tuple),
    ]

    def _evaluate(self, **state_kwargs) -> Dict[str, Any]:

        new_target_pose = state_kwargs["new_target_pose"]

        # Extract position and orientation
        target_position = (
            new_target_pose.position.x,
            new_target_pose.position.y,
            new_target_pose.position.z,
        )

        target_orientation = (
            new_target_pose.orientation.x,
            new_target_pose.orientation.y,
            new_target_pose.orientation.z,
            new_target_pose.orientation.w,
        )

        pose_tolerance = (self.position_tolerance, self.orientation_tolerance)

        return {
            "target_position": target_position,
            "target_orientation": target_orientation,
            "reference_frame": self.target_frame,
            "pose_tolerance": pose_tolerance,
        }


def main():
    # Instantiate the PoseReset with init parameters
    pose_reset = PoseReset(
        target_frame="map", position_tolerance=0.1, orientation_tolerance=0.05
    )

    # Create dummy new target pose
    new_pose = Pose()
    new_pose.position = Point(x=5.0, y=3.0, z=0.0)
    new_pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

    # Create dummy current pose (not used in __call__, but required by interface)
    current_pose = Pose()
    current_pose.position = Point(x=1.0, y=1.0, z=0.0)
    current_pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

    # Call the reset method
    output = pose_reset(new_target_pose=new_pose, current_pose=current_pose)

    # Print the outputs
    print("PoseReset Output:")
    for key, value in output.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
