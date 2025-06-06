import numpy as np
from typing import Tuple
import numpy.typing as npt


def generate_circle_points(x: float,
                           y: float,
                           radius: float,
                           num_points: int = 100) -> Tuple[npt.NDArray[np.float64],
                                                           npt.NDArray[np.float64]]:
    """
    generate_circle_points:
    Generate a discretised 2D circle.

    Args:
        x (float): x-coordinate of the center
        y (float): y-coordinate of the center
        radius (float): radius of the circle
        num_points (int): number of points to generate along the circle

    Returns:
        Tuple[np.ndarray, np.ndarray]: Arrays of x and y points on the circle
    """
    theta = np.linspace(0, 2 * np.pi, num_points)
    x_points = x + radius * np.cos(theta)
    y_points = y + radius * np.sin(theta)
    return x_points, y_points
