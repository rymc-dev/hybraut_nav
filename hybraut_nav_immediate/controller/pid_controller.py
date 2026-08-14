from .controller import Controller
from hybraut_nav_utils import normalize_angle


class PIDController(Controller):
    """
    Standard heading-hold PID controller.

    Drop-in alternative to `FiniteTimeController` for the immediate layer
    while `finite_time_control` (the external finite-time guidance package)
    isn't published/ready yet - see `ControllerType`. Implements the same
    `Controller` interface: `update_state`, `update_continous_dynamics`,
    `step`.
    """

    def __init__(
        self,
        kp: float = 1.0,
        ki: float = 0.0,
        kd: float = 0.0,
        dt: float = 0.01,
        max_yaw_rate: float = 0.2,
        integral_limit: float = 1.0,
    ):
        """
        Args:
            kp: proportional gain on heading error
            ki: integral gain on accumulated heading error
            kd: derivative gain on the rate of change of heading error
            dt: control loop period (s), used for the integral/derivative terms
            max_yaw_rate: symmetric clamp (rad/s) applied to the output command
            integral_limit: symmetric clamp applied to the accumulated integral
                term, to prevent windup
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt
        self.max_yaw_rate = max_yaw_rate
        self.integral_limit = integral_limit

        # State placeholders
        self.current_heading = 0.0
        self.desired_heading = 0.0
        self.time_derivative_of_desired_heading = 0.0

        self._integral = 0.0
        self._previous_error = 0.0

    def update_state(self, current_heading: float):
        """Update the current heading."""
        self.current_heading = current_heading

    def update_continous_dynamics(self, desired_heading: float, desired_heading_rate: float = 0.0):
        """Update the continous dynamics as defined in the tactical layer."""
        self.desired_heading = desired_heading
        self.time_derivative_of_desired_heading = desired_heading_rate

    def step(self) -> float:
        """
        Compute the PID control input (yaw rate command).

        Returns:
            yaw_rate_cmd (float): control input, clamped to +/- max_yaw_rate
        """
        # heading error normalized to [-pi, pi]
        error = normalize_angle(self.desired_heading - self.current_heading)

        self._integral = max(
            -self.integral_limit,
            min(self.integral_limit, self._integral + error * self.dt)
        )
        derivative = (error - self._previous_error) / self.dt if self.dt > 0 else 0.0
        self._previous_error = error

        yaw_rate_cmd = (
            self.time_derivative_of_desired_heading
            + self.kp * error
            + self.ki * self._integral
            + self.kd * derivative
        )

        return max(-self.max_yaw_rate, min(self.max_yaw_rate, yaw_rate_cmd))

    def reset(self):
        """Clears accumulated integral/derivative history - call this when
        resuming after a gap (e.g. immediate_node's control loop going
        active again after the tactical layer was idle) so a stale windup/
        derivative spike from before the gap doesn't leak into the first
        commands afterward. Leaves current_heading/desired_heading alone -
        those get refreshed by the normal update_state/update_continous_dynamics
        calls anyway."""
        self._integral = 0.0
        self._previous_error = 0.0

    def __repr__(self):
        return f"PIDController(kp={self.kp}, ki={self.ki}, kd={self.kd})"
