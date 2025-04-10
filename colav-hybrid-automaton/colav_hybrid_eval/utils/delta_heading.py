import numpy as np

def delta_heading(x_a, y_a, theta_a, x_w, y_w):
    # desired heading angle (from agent to waypoint)
    desired_theta = np.arctan2(y_w - y_a, x_w - x_a)
    # Heading error: difference between the desired and current orientation
    error = desired_theta - theta_a
    # Normalize to [-pi, pi]
    error = (error + np.pi) % (2 * np.pi) - np.pi

    return error