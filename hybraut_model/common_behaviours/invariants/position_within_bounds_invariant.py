from automaton_models.hybraut_model.aci_interfaces import InvariantInterface
from automaton.spec import IOSpec
from geometry_msgs.msg import PoseStamped


class PositionWithinBoundsInvariant(InvariantInterface):
    _init_input_spec = [
        IOSpec.create_io_spec("x_min", float),
        IOSpec.create_io_spec("x_max", float),
        IOSpec.create_io_spec("y_min", float),
        IOSpec.create_io_spec("y_max", float),
    ]
    _state_input_spec = [
        IOSpec.create_io_spec("pose", PoseStamped)
    ]

    def _evaluate(self, **state_kwargs) -> bool:
        pose = state_kwargs["pose"].pose.position
        return (
            self.x_min <= pose.x <= self.x_max and
            self.y_min <= pose.y <= self.y_max
        )
    

def main():
    # Initialize invariant with bounds
    invariant: InvariantInterface = PositionWithinBoundsInvariant(
        x_min=0.0, x_max=10.0, y_min=0.0, y_max=10.0
    )

    # Create a sample pose
    pose_msg = PoseStamped()
    pose_msg.pose.position.x = 5.0
    pose_msg.pose.position.y = 7.0

    # Evaluate the invariant
    result = invariant(pose=pose_msg)

    # Print result
    print(f"PositionWithinBoundsInvariant holds: {result}")

if __name__ == '__main__':
    main()