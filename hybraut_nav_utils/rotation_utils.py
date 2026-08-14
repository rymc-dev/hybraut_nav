"""
a utility file containing several utility functions for
rotation calculations
"""

import numpy as np
import math


def quaternion_to_heading(qx, qy, qz, qw) -> float:
    """Convert quaternion to heading angle in radians."""
    # Yaw (Z-axis rotation)
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    return math.atan2(siny_cosp, cosy_cosp)


def normalize_angle(angle: float):
    """normalizes an angle between -pi - pi inclusive"""
    return (angle + np.pi) % (2 * np.pi) - np.pi
