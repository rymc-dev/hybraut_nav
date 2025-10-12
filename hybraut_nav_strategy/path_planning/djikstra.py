#!/usr/bin/env python3
"""
Dijkstra's algorithm implementation for path planning.
"""
import heapq
from typing import List, Tuple, Optional, Dict, Set
from .planner import Path, Point, Grid, Planner


class Dijkstra(Planner):
    """
    Dijkstra's shortest path algorithm implementation.
    """

    def __init__(self, obstacle_threshold: int = 200):
        super().__init__(obstacle_threshold)
        self.grid: Optional[Grid] = None

    def plan_path(self, grid: Grid, start: Point, end: Point) -> Tuple[Optional[Path], Optional[float]]:
        """
        Plan a path from start to end using Dijkstra's algorithm.
        Returns (Path, total_cost) if found, otherwise (None, None).
        """
        self.grid = grid
        
        # Validate start and end
        if not self.is_valid_point(start):
            print(f"Start point ({start.x}, {start.y}) is invalid")
            return None, None
        if not self.is_valid_point(end):
            print(f"End point ({end.x}, {end.y}) is invalid")
            return None, None

        # Priority queue: (cost, x, y)
        pq = [(0.0, start.x, start.y)]
        
        # Distance map: (x, y) -> cost
        distances: Dict[Tuple[int, int], float] = {(start.x, start.y): 0.0}
        
        # Parent map for path reconstruction: (x, y) -> (parent_x, parent_y)
        parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {(start.x, start.y): None}
        
        # Visited set
        visited: Set[Tuple[int, int]] = set()

        while pq:
            current_cost, x, y = heapq.heappop(pq)
            
            # Skip if already visited
            if (x, y) in visited:
                continue
            
            visited.add((x, y))
            
            # Check if we reached the goal
            if x == end.x and y == end.y:
                return self.reconstruct_path(parents, start, end)
            
            # Explore neighbors (8-connected)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), 
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = x + dx, y + dy
                neighbor = Point(nx, ny)
                
                # Skip if invalid or visited
                if not self.is_valid_point(neighbor) or (nx, ny) in visited:
                    continue
                
                # Calculate cost (diagonal moves cost sqrt(2), orthogonal cost 1)
                move_cost = 1.414 if (dx != 0 and dy != 0) else 1.0
                
                # Add penalty based on cell value (optional - can tune or remove)
                cell_val = grid.get_cell(nx, ny)
                if cell_val < 254:
                    # Small penalty for being near obstacles
                    move_cost += (254 - cell_val) * 0.01
                
                new_cost = current_cost + move_cost
                
                # Update if we found a better path
                if (nx, ny) not in distances or new_cost < distances[(nx, ny)]:
                    distances[(nx, ny)] = new_cost
                    parents[(nx, ny)] = (x, y)
                    heapq.heappush(pq, (new_cost, nx, ny))
        
        # No path found
        return None, None

    def is_valid_point(self, point: Point) -> bool:
        """Check if a point is valid (within bounds and not an obstacle)."""
        x, y = point.x, point.y
        
        # Check bounds
        if x < 0 or x >= self.grid.width or y < 0 or y >= self.grid.height:
            return False
        
        # Check cell value
        cell = self.grid.get_cell(x, y)
        
        # 0 = lethal obstacle
        if cell == 0:
            return False
        
        # 255 = unknown (treat as obstacle)
        if cell == 255:
            return False
        
        # 1-254 are traversable
        return True

    def reconstruct_path(self, parents: Dict[Tuple[int, int], Optional[Tuple[int, int]]], 
                        start: Point, end: Point) -> Tuple[Path, float]:
        """Reconstruct path from parent map."""
        path_points = []
        current = (end.x, end.y)
        
        while current is not None:
            path_points.append(Point(current[0], current[1]))
            current = parents[current]
        
        # Reverse to get start -> end
        path_points.reverse()
        
        # Calculate total cost
        total_cost = 0.0
        for i in range(len(path_points) - 1):
            p1, p2 = path_points[i], path_points[i + 1]
            dx = abs(p2.x - p1.x)
            dy = abs(p2.y - p1.y)
            if dx > 0 and dy > 0:
                total_cost += 1.414  # diagonal
            else:
                total_cost += 1.0  # orthogonal
        
        return Path(path_points), total_cost


# Test code
import matplotlib.pyplot as plt
import numpy as np

def main():
    width, height = 50, 30
    g = Grid(width, height, resolution=1.0)

    # Initialize the costmap with 254 = free space
    g.data[:, :] = 254

    # 1. Horizontal obstacle stripe
    for x in range(10, 40):
        g.set_cell(x, 15, 0)

    # 2. Vertical obstacle stripe
    for y in range(5, 25):
        g.set_cell(25, y, 0)

    # 3. A small block obstacle
    for x in range(5, 10):
        for y in range(20, 25):
            g.set_cell(x, y, 0)

    # 4. Diagonal "fence" obstacle
    for i in range(0, 15):
        x = 35 + i
        y = 5 + i
        if x < width and y < height:
            g.set_cell(x, y, 0)

    # 5. Add some unknown space (255)
    for x in range(40, 45):
        for y in range(10, 15):
            g.set_cell(x, y, 255)

    # Start and goal
    start = Point(5, 5)
    goal = Point(45, 25)

    # Run Dijkstra
    dijkstra = Dijkstra(obstacle_threshold=200)
    path, cost = dijkstra.plan_path(g, start, goal)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title("Dijkstra Path on Costmap (0=obstacle, 254=free, 255=unknown)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Show costmap
    ax.imshow(
        g.data,
        cmap="gray",
        origin="lower",
        extent=[0, width, 0, height],
        vmin=0,
        vmax=255
    )

    # Plot start and goal
    ax.plot(start.x, start.y, "go", markersize=10, label="Start")
    ax.plot(goal.x, goal.y, "ro", markersize=10, label="Goal")

    # Plot path if found
    if path is not None and path.points:
        xs = [p.x for p in path.points]
        ys = [p.y for p in path.points]
        ax.plot(xs, ys, "b-", linewidth=2, label=f"Dijkstra Path (cost={cost:.1f})")
        print(f"Found path with {len(path.points)} points, cost {cost:.2f}")
        
        # Verify no obstacles in path
        for i, p in enumerate(path.points):
            cell_val = g.get_cell(p.x, p.y)
            if cell_val == 0 or cell_val == 255:
                print(f"WARNING: Path point {i} at ({p.x}, {p.y}) has cell value {cell_val}!")
    else:
        print("No path found")

    ax.legend()
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()