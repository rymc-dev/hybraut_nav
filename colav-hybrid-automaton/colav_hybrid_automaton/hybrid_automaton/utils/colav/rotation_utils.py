import numpy as np
import math

def quaternion_to_heading(qx, qy, qz, qw) -> float:
    """Convert quaternion to heading angle in radians."""
    # Yaw (Z-axis rotation)
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)


def normalize_angle(angle: float):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def delta_heading(x_a, y_a, theta_a, x_w, y_w) -> float:
    """
    delta_heading
    calculates the difference in heading between an goal point and
    an agent position and orientation

    returns: float
    """
    # desired heading angle (from agent to waypoint)
    desired_theta = np.arctan2(y_w - y_a, x_w - x_a)
    # Heading error: difference between the desired and current orientation
    error = desired_theta - theta_a
    # Normalize to [-pi, pi]
    error = (error + np.pi) % (2 * np.pi) - np.pi

    return error
