import numpy as np

def quaternion_to_heading(qx, qy, qz, qw):
    """
    Convert quaternion to 2D heading (yaw angle in radians, normalized to [-π, π])
    
    Parameters:
        qx, qy, qz, qw: Quaternion components
        
    Returns:
        heading: yaw angle in radians
    """
    # Yaw (Z-axis rotation) from quaternion
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy**2 + qz**2)
    heading = np.arctan2(siny_cosp, cosy_cosp)
    
    # Normalize to [-π, π]
    heading = (heading + np.pi) % (2 * np.pi) - np.pi
    
    return heading