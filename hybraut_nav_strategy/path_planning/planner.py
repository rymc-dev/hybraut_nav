import numpy as np
from typing import List
from nav_msgs.msg import OccupancyGrid, Path as ROSPath
from geometry_msgs.msg import PoseStamped
from dataclasses import dataclass


class Grid:
    """ 
    Grid representation for path planning.
    """
    def __init__(self, width, height, resolution=1.0, origin=(0, 0, 0)):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin = origin  # (x, y, z)
        self.data = np.zeros((height, width), dtype=np.uint8)

    @classmethod
    def from_ros_msg(cls, msg: OccupancyGrid):
        width = msg.info.width
        height = msg.info.height
        resolution = msg.info.resolution
        origin = (msg.info.origin.position.x, msg.info.origin.position.y, msg.info.origin.position.z)
        data = np.array(msg.data, dtype=np.int8).reshape((height, width))
        grid = cls(width, height, resolution, origin)
        grid.data = data
        return grid

    def set_cell(self, x, y, value):
        self.data[y, x] = value

    def get_cell(self, x: int, y: int) -> int:
        return self.data[y, x]
    
class Path: 
    """ 
    Path representation for path planning.
    """
    def __init__(self, points: List['Point']):
        self.points = points
        
    
    def to_ros_path(self, frame_id="map"):
        ros_path = ROSPath()
        ros_path.header.frame_id = frame_id
        for pt in self.points:
            pose = PoseStamped()
            pose.header.frame_id = frame_id
            pose.pose.position.x = pt.x
            pose.pose.position.y = pt.y
            pose.pose.position.z = 0
            pose.pose.orientation.w = 1.0
            ros_path.poses.append(pose)
        return ros_path
  
@dataclass
class Point:
    """ 
    Point representation in 2D space.
    """ 
    x: float
    y: float 
    
    @classmethod
    def from_ros_msg(cls, msg: PoseStamped):
        return cls(msg.pose.position.x, msg.pose.position.y)
    

class Planner:
    """ 
    Base class for path planners.
    """ 
    def __init__(self, obstacle_threshold: float = 200.0): 
        self.obstacle_threshold = obstacle_threshold
    
    def plan_path(self, grid: Grid, start: Point, end: Point) -> Path:
        """ 
         Plan a path from start to end on the given grid.
         This method should be overridden by subclasses.
         """
        raise NotImplementedError("This method should be overridden by subclasses")

 


