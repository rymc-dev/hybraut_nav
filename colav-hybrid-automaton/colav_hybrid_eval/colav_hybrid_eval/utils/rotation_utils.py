import numpy as np


def quaternion_to_heading(qx: float, qy: float, qz: float, qw: float) -> float:
    """
    Convert quaternion to 2D heading (yaw angle in radians, normalized to [-π, π])

    Args:
        qx, qy, qz, qw: Quaternion components

    Returns:
        heading: yaw angle in radians
    """
    if not all(np.isfinite([qx, qy, qz, qw])):
        raise ValueError("Quaternion components must be finite numbers.")

    # Yaw (Z-axis rotation) from quaternion
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy**2 + qz**2)
    heading = np.arctan2(siny_cosp, cosy_cosp)

    # Normalize to [-π, π]
    heading = (heading + np.pi) % (2 * np.pi) - np.pi

    return heading


def normalize_angle(angle):
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
