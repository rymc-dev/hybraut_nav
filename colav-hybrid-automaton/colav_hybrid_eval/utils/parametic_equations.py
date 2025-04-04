import numpy as np

def generate_circle_points(x, y, radius, num_points=100):
    """generate a discretised 2d circle"""
    theta = np.linspace(0, 2 * np.pi, num_points)  # Generate angles
    x_points = x + radius * np.cos(theta)
    y_points = y + radius * np.sin(theta)
    return x_points, y_points