from .controller import Controller
from dataclasses import dataclass
import numpy as np
import time

@dataclass
class Pose:
    @dataclass
    class Point:
        x: float
        y: float
    point: Point
    yaw: float

class FiniteTimeController(Controller):
    def __init__(
        self,
        control_gain: float = 1.0,
        present_convergence: float = 0.8,
        a: float = 1.0
    ):
        """
        Args:
            control_gain (k1): main tuning parameter affecting convergence speed
            present_convergence (alpha): fractional power term (0 < alpha < 1)
            a: vessel yaw dynamics parameter (optional, can be used for normalization)
        """
        self.control_gain = control_gain
        self.present_convergence = present_convergence
        self.a = a
        self.current_timer = time.time()

        # State placeholders
        self.current_heading = 0.0
        self.desired_heading = 0.0
        self.time_derivative_of_desired_heading = 0.0

    def update_state(self, current_heading: float):
        """Update the current heading."""
        self.current_heading = current_heading
        
    def update_continous_dynamics(self, desired_heading: float, desired_heading_rate: float = 0.0):
        """Update the continous dynamics as defined in the tactical layer."""
        self.desired_heading = desired_heading
        self.time_derivative_of_desired_heading = desired_heading_rate

    def step(self) -> float:
        """
        Compute the finite-time control input (yaw rate command).
        
        Returns:
            yaw_rate_cmd (float): control input (rudder angle proxy or yaw rate)
        """
        # heading error (normalized to [-pi, pi])
        e = np.arctan2(np.sin(self.desired_heading - self.current_heading),
                       np.cos(self.desired_heading - self.current_heading))

        # finite-time control law
        k1 = self.control_gain
        alpha = self.present_convergence
        psi_dot_d = self.time_derivative_of_desired_heading

        # control command (yaw rate or equivalent)
        yaw_rate_cmd = psi_dot_d + k1 * np.sign(e) * (abs(e) ** alpha)

        return yaw_rate_cmd

    def __repr__(self):
        return (
            f"FiniteTimeController(k1={self.control_gain}, "
            f"alpha={self.present_convergence}, a={self.a})"
        )

# Example usage
if __name__ == "__main__":
    ctrl = FiniteTimeController(control_gain=1.5, present_convergence=0.6)
    ctrl.update_state(current_heading=0.0, desired_heading=np.pi/2)  # 90° desired
    yaw_rate = ctrl.step()
    print(f"Yaw rate command: {yaw_rate:.3f} rad/s")
