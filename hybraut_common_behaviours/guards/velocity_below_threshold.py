
from hybraut_aci_interfaces import GuardInterface, IOSpec
from geometry_msgs.msg import TwistStamped
import math

class VelocityBelowThresholdGuard(GuardInterface):
    _init_input_spec = [
        IOSpec.create_io_spec("min_velocity", float)
    ]
    _state_input_spec = [
        IOSpec.create_io_spec("velocity", TwistStamped)
    ]

    def _evaluate(self, **state_kwargs) -> bool:
        velocity_msg: TwistStamped = state_kwargs["velocity"]
        v = velocity_msg.twist.linear
        speed = math.hypot(v.x, v.y)
        return speed < self.min_velocity
    

def main():
    vel_msg = TwistStamped()
    vel_msg.twist.linear.x = 0.1
    vel_msg.twist.linear.y = 0.1

    vel_guard = VelocityBelowThresholdGuard(min_velocity=0.5)
    result = vel_guard(velocity=vel_msg)
    print(f"VelocityBelowThresholdGuard result: {result}")

if __name__ == '__main__':
    main()