# This files determines the dynamics of the system/ aka the mode behavior/control policies
# while in each mode.

from colav_interfaces.msg import AgentState, WaypointsState
import math
from colav_hybrid_automaton.automaton.utils import quaternion_to_heading
from typing import NamedTuple
from colav_interfaces.msg import Waypoint
from typing import Deque, Any

class ControlOutput(NamedTuple):
    velocity: float
    yaw_rate: float

class PIDYawVelocityController:
    """
    PIDYawVelocityController
    A PID controller for velocity and yaw rate based on heading and position error
    relative to the target waypoint.
    """

    def __init__(
        self,
        target_velocity: float = 30 * 0.514444,
        yaw_kp: float = 0.8,
        yaw_ki: float = 0.05,
        yaw_kd: float = 0.2,
        vel_kp: float = 1.0,
        vel_ki: float = 0.1,
        vel_kd: float = 0.1,
        error_tolerance: float = 0.01,
        max_yaw_rate: float = 0.2,
        dt: float = 0.1,
        **kwargs
    ):
        if dt < 0.01:
            raise ValueError("dt must be >= 0.01")

        self.target_velocity = target_velocity
        self.dt = dt
        self.error_tolerance = error_tolerance
        self.max_yaw_rate = max_yaw_rate

        # PID gains
        self.yaw_kp = yaw_kp
        self.yaw_ki = yaw_ki
        self.yaw_kd = yaw_kd

        self.vel_kp = vel_kp
        self.vel_ki = vel_ki
        self.vel_kd = vel_kd

        # PID state (integrals & previous errors)
        self.heading_error_integral = 0.0
        self.prev_heading_error = 0.0

        self.velocity_error_integral = 0.0
        self.prev_velocity_error = 0.0

    def __call__(self, status_buffer: Deque[AgentState], current_waypoints: WaypointsState, **kwargs) -> ControlOutput:
        if not status_buffer or not isinstance(status_buffer[-1], AgentState):
            raise ValueError("status_buffer must contain at least one AgentState as its latest entry.")

        current_state = status_buffer[-1]

        if not isinstance(current_waypoints, WaypointsState):
            raise ValueError("current_waypoints")
        
        if not isinstance(current_waypoints.current_waypoint, Waypoint): 
            raise ValueError("current waypoint not set in waypointsstate")

        try:
            wp: Waypoint = current_waypoints.current_waypoint
        except IndexError:
            raise ValueError("No waypoint to navigate to")

        # Compute desired heading
        dx = wp.position.x - current_state.pose.position.x
        dy = wp.position.y - current_state.pose.position.y
        desired_heading = math.atan2(dy, dx)

        # Get current heading
        current_heading = quaternion_to_heading(
            qx=current_state.pose.orientation.x,
            qy=current_state.pose.orientation.y,
            qz=current_state.pose.orientation.z,
            qw=current_state.pose.orientation.w,
        )

        # Yaw PID
        heading_error = math.atan2(
            math.sin(desired_heading - current_heading),
            math.cos(desired_heading - current_heading)
        )

        self.heading_error_integral += heading_error * self.dt
        heading_error_derivative = (heading_error - self.prev_heading_error) / self.dt
        self.prev_heading_error = heading_error

        raw_yaw_rate = (
            self.yaw_kp * heading_error +
            self.yaw_ki * self.heading_error_integral +
            self.yaw_kd * heading_error_derivative
        )
        target_yaw_rate = max(-self.max_yaw_rate, min(raw_yaw_rate, self.max_yaw_rate))

        # Velocity PID
        current_velocity = current_state.velocity
        velocity_error = self.target_velocity - current_velocity
        self.velocity_error_integral += velocity_error * self.dt
        velocity_error_derivative = (velocity_error - self.prev_velocity_error) / self.dt
        self.prev_velocity_error = velocity_error

        velocity_command = (
            self.vel_kp * velocity_error +
            self.vel_ki * self.velocity_error_integral +
            self.vel_kd * velocity_error_derivative
        )

        # Final target velocity = current + PID adjustment
        final_velocity = current_velocity + velocity_command

        return final_velocity, target_yaw_rate

class NoOpController:
    """
    NoOpController
    A placeholder controller that outputs zero velocity and yaw rate
    regardless of input. Useful for disabling control or as a fallback.
    """

    def __init__(self) -> None:
        """Initialize the NoOpController (no state needed)."""
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> ControlOutput:
        """
        Return a no-operation control command.

        Returns:
            ControlOutput: velocity = 0.0, yaw_rate = 0.0
        """
        return ControlOutput(velocity=0.0, yaw_rate=0.0)

