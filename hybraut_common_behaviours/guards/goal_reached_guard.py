from hybraut_aci_interfaces import GuardInterface, IOSpec
from geometry_msgs.msg import PoseStamped


class GoalReachedGuard(GuardInterface):
    _init_input_spec = [
        IOSpec.create_io_spec("tolerance", float)
    ]
    _state_input_spec = [
        IOSpec.create_io_spec("current_pose", PoseStamped),
        IOSpec.create_io_spec("goal_pose", PoseStamped)
    ]

    def _evaluate(self, **state_kwargs) -> bool:
        current_pose: PoseStamped = state_kwargs["current_pose"]
        goal_pose: PoseStamped = state_kwargs["goal_pose"]
        tolerance: float = self.tolerance

        dx = goal_pose.pose.position.x - current_pose.pose.position.x
        dy = goal_pose.pose.position.y - current_pose.pose.position.y
        distance = (dx**2 + dy**2) ** 0.5

        return distance <= tolerance


def main():
    guard: GuardInterface = GoalReachedGuard(tolerance=10.0)
    result:bool = guard(current_pose=PoseStamped(), goal_pose=PoseStamped())
    print(f"GoalReached Guard Result: {result}")

if __name__ == '__main__':
    main()