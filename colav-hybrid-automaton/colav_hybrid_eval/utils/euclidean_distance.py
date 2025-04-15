import numpy as np

def euclidean_distance(point1, point2) -> float:
    """
    euclidean_distance
    calculates the euclidean distance between two 2d points in an environment

    returns: euclidean_distance: float
    """
    return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)