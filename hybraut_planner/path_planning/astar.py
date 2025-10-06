#!/usr/bin/env python3
"""
A* algorithm implementation for path planning with ROS costmap convention.
Supports float coordinates for precise path planning.
"""
import heapq
import math
from typing import List, Tuple, Optional, Dict, Set
from .planner import Path, Point, Grid, Planner
import rclpy

class AStar(Planner):
    """
    A* shortest path algorithm implementation.
    Uses ROS costmap convention:
    - -1/255 = unknown space
    - 0 = free space (highest confidence)
    - 1-99 = traversable with increasing cost
    - 100 = guaranteed obstacle
    
    Works with float coordinates in world space.
    """

    def __init__(self, obstacle_threshold: int = 200, heuristic_weight: float = 1.0):
        super().__init__(obstacle_threshold)
        self.grid: Optional[Grid] = None
        self.heuristic_weight = heuristic_weight  # Weight for heuristic (1.0 = standard A*)

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        grid_x = round((x - self.grid.origin[0]) / self.grid.resolution)
        grid_y = round((y - self.grid.origin[1]) / self.grid.resolution)
        return grid_x, grid_y

    
    def grid_to_world(self, grid_x: int, grid_y: int, center_in_cell: bool = True) -> Tuple[float, float]:
        """
        Convert grid coordinates to world coordinates.
        
        Args:
            grid_x, grid_y: Grid cell coordinates (integers)
            center_in_cell: If True, return center of cell. If False, return cell corner.
        """
        offset = 0.5 if center_in_cell else 0.0
        world_x = (grid_x + offset) * self.grid.resolution + self.grid.origin[0]
        world_y = (grid_y + offset) * self.grid.resolution + self.grid.origin[1]
        return world_x, world_y

    def plan_path(self, grid: Grid, start: Point, end: Point):
        """
        Plan a path from start to end using A* algorithm.
        
        Args:
            grid: Grid object with costmap data
            start: Point with x, y in world coordinates (floats)
            end: Point with x, y in world coordinates (floats)
            
        Returns:
            ROS2 nav_msgs.msg.Path if found, otherwise None.
        """
        import nav_msgs.msg
        import geometry_msgs.msg

        self.grid = grid
        
        # Convert world coordinates to grid coordinates for planning
        start_grid_x, start_grid_y = self.world_to_grid(start.x, start.y)
        end_grid_x, end_grid_y = self.world_to_grid(end.x, end.y)
        
        start_grid = Point(start_grid_x, start_grid_y)
        end_grid = Point(end_grid_x, end_grid_y)
        
        # Validate start and end
        if not self.is_valid_point(start_grid):
            print(f"Start point ({start.x}, {start.y}) -> grid ({start_grid_x}, {start_grid_y}) is invalid")
            return None
        if not self.is_valid_point(end_grid):
            print(f"End point ({end.x}, {end.y}) -> grid ({end_grid_x}, {end_grid_y}) is invalid")
            return None

        h_start = self.heuristic(start_grid, end_grid)
        pq = [(h_start, 0.0, start_grid_x, start_grid_y)]
        g_scores: Dict[Tuple[int, int], float] = {(start_grid_x, start_grid_y): 0.0}
        parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {(start_grid_x, start_grid_y): None}
        visited: Set[Tuple[int, int]] = set()
        nodes_expanded = 0

        while pq:
            f_score, g_score, x, y = heapq.heappop(pq)
            if (x, y) in visited:
                continue
            visited.add((x, y))
            nodes_expanded += 1
            if x == end_grid_x and y == end_grid_y:
                # Reconstruct path in grid coordinates
                path_points_grid = []
                current = (end_grid_x, end_grid_y)
                while current is not None:
                    path_points_grid.append(current)
                    current = parents[current]
                path_points_grid.reverse()

                # Build ROS2 Path message with world coordinates
                ros_path = nav_msgs.msg.Path()
                ros_path.header.frame_id = "map"
                # ros_path.header.stamp = rclpy.time.Time().to_msg()
                
                for i, grid_pt in enumerate(path_points_grid):
                    pose = geometry_msgs.msg.PoseStamped()
                    pose.header.frame_id = "map"
                    
                    # Use exact start/end coordinates, grid-to-world for intermediate points
                    if i == 0:  # First point - use exact start coordinates
                        pose.pose.position.x = start.x
                        pose.pose.position.y = start.y
                    elif i == len(path_points_grid) - 1:  # Last point - use exact end coordinates
                        pose.pose.position.x = end.x
                        pose.pose.position.y = end.y
                    else:  # Intermediate points - use grid-to-world conversion (centered in cell)
                        world_x, world_y = self.grid_to_world(grid_pt[0], grid_pt[1], center_in_cell=True)
                        pose.pose.position.x = world_x
                        pose.pose.position.y = world_y
                    
                    pose.pose.position.z = 0.0
                    pose.pose.orientation.w = 1.0
                    ros_path.poses.append(pose)
                return ros_path

            # Explore neighbors (8-connected)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), 
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                neighbor = Point(nx, ny)
                if not self.is_valid_point(neighbor) or (nx, ny) in visited:
                    continue
                
                # Base movement cost (diagonal vs orthogonal)
                move_cost = 1.414 if (dx != 0 and dy != 0) else 1.0
                
                # Add cost based on cell value (0=free, 1-99=increasing cost)
                cell_val = grid.get_cell(nx, ny)
                if 0 <= cell_val < 100:
                    # Scale cost: 0 adds nothing, 99 adds significant cost
                    move_cost += cell_val * 0.01
                
                new_g_score = g_score + move_cost
                if (nx, ny) not in g_scores or new_g_score < g_scores[(nx, ny)]:
                    g_scores[(nx, ny)] = new_g_score
                    parents[(nx, ny)] = (x, y)
                    h_score = self.heuristic(neighbor, end_grid)
                    f_score = new_g_score + self.heuristic_weight * h_score
                    heapq.heappush(pq, (f_score, new_g_score, nx, ny))
        print(f"A* expanded {nodes_expanded} nodes (no path found)")
        return None

    def heuristic(self, point: Point, goal: Point) -> float:
        """
        Heuristic function (Euclidean distance).
        This estimates the cost from point to goal.
        """
        dx = abs(point.x - goal.x)
        dy = abs(point.y - goal.y)
        # Euclidean distance
        return math.sqrt(dx * dx + dy * dy)
        
        # Alternative: Diagonal distance (more accurate for 8-connected grid)
        # return max(dx, dy) + 0.414 * min(dx, dy)

    def is_valid_point(self, point: Point) -> bool:
        """
        Check if a point is valid (within bounds and not an obstacle).
        ROS costmap convention:
        - 0-99: traversable (0 = free, higher = more costly)
        - 100: obstacle
        - 255 (-1): unknown
        
        Args:
            point: Point with x, y in grid coordinates (integers)
        """
        x, y = int(point.x), int(point.y)
        
        # Check bounds
        if x < 0 or x >= self.grid.width or y < 0 or y >= self.grid.height:
            return False
        
        # Check cell value
        cell = self.grid.get_cell(x, y)
        
        # 100 = obstacle
        if cell == 100:
            return False
        
        # 255 (-1) = unknown
        if cell == 255:
            return False
        
        # 0-99 are traversable (0 = highest confidence free space, 99 = least confidence)
        return True


# Test code
import matplotlib.pyplot as plt
import numpy as np

def main():
    width, height = 50, 30
    resolution = 0.5  # 0.5 meters per grid cell
    origin = (0.0, 0.0, 0.0)
    
    g = Grid(width, height, resolution=resolution, origin=origin)

    # Initialize the costmap with 0 = free space (ROS convention)
    g.data[:, :] = 0

    # 1. Horizontal obstacle stripe (100 = obstacle)
    for x in range(10, 40):
        g.set_cell(x, 15, 100)

    # 2. Vertical obstacle stripe
    for y in range(5, 25):
        g.set_cell(25, y, 100)

    # 3. A small block obstacle
    for x in range(5, 10):
        for y in range(20, 25):
            g.set_cell(x, y, 100)

    # 4. Diagonal "fence" obstacle
    for i in range(0, 15):
        x = 35 + i
        y = 5 + i
        if x < width and y < height:
            g.set_cell(x, y, 100)

    # 5. Add some unknown space (255)
    for x in range(40, 45):
        for y in range(10, 15):
            g.set_cell(x, y, 255)

    # 6. Add some moderate cost areas (demonstrating 1-99 range)
    for x in range(15, 20):
        for y in range(5, 10):
            g.set_cell(x, y, 50)  # Medium cost area

    # Start and goal in WORLD COORDINATES (floats)
    start = Point(2.5, 2.5)  # World coordinates
    goal = Point(22.5, 12.5)  # World coordinates
    
    print(f"Start: {start.x}, {start.y} (world coords)")
    print(f"Goal: {goal.x}, {goal.y} (world coords)")
    print(f"Resolution: {resolution} m/cell")

    # Run A*
    astar = AStar(obstacle_threshold=200, heuristic_weight=1.0)
    ros_path = astar.plan_path(g, start, goal)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title("A* Path on ROS Costmap (0=free, 1-99=cost, 100=obstacle, 255=unknown)")
    ax.set_xlabel("X (world coordinates, meters)")
    ax.set_ylabel("Y (world coordinates, meters)")

    # Show costmap with world coordinates
    world_width = width * resolution
    world_height = height * resolution
    
    display_data = g.data.copy().astype(float)
    
    ax.imshow(
        display_data,
        cmap="gray_r",  # Reverse gray so 0=white (free), 100=dark (obstacle)
        origin="lower",
        extent=[origin[0], origin[0] + world_width, origin[1], origin[1] + world_height],
        vmin=0,
        vmax=100
    )

    # Plot start and goal
    ax.plot(start.x, start.y, "go", markersize=10, label="Start")
    ax.plot(goal.x, goal.y, "ro", markersize=10, label="Goal")

    # Plot path if found
    if ros_path is not None and len(ros_path.poses) > 0:
        # Extract world coordinates from ROS path
        xs = [pose.pose.position.x for pose in ros_path.poses]
        ys = [pose.pose.position.y for pose in ros_path.poses]
        
        # Calculate path cost
        cost = 0.0
        for i in range(len(xs) - 1):
            dx = xs[i+1] - xs[i]
            dy = ys[i+1] - ys[i]
            cost += math.sqrt(dx*dx + dy*dy)
        
        ax.plot(xs, ys, "b-", linewidth=2, label=f"A* Path (cost={cost:.2f}m)")
        ax.plot(xs, ys, "b.", markersize=4)
        print(f"Found path with {len(ros_path.poses)} waypoints, cost {cost:.2f} meters")
        
        # Verify no obstacles in path
        for i, pose in enumerate(ros_path.poses):
            world_x = pose.pose.position.x
            world_y = pose.pose.position.y
            grid_x = int((world_x - origin[0]) / resolution)
            grid_y = int((world_y - origin[1]) / resolution)
            if 0 <= grid_x < width and 0 <= grid_y < height:
                cell_val = g.get_cell(grid_x, grid_y)
                if cell_val == 100 or cell_val == 255:
                    print(f"WARNING: Path waypoint {i} at ({world_x:.2f}, {world_y:.2f}) has cell value {cell_val}!")
    else:
        print("No path found")

    ax.legend()
    ax.set_xlim(origin[0], origin[0] + world_width)
    ax.set_ylim(origin[1], origin[1] + world_height)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    ax.set_aspect('equal')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()