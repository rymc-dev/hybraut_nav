#!/usr/bin/env python3
"""
RRT* (RRT Star) implementation for path planning.
"""
import math
import random
from typing import List, Tuple, Optional
import numpy as np
from .planner import Path, Point, Grid, Planner


class Node:
    """Node in the RRT* tree."""
    def __init__(self, x: int, y: int):
        self.x = int(x)
        self.y = int(y)
        self.parent: Optional[Node] = None
        self.cost: float = 0.0  # Cost from start to this node

    def __eq__(self, other):
        if other is None or not isinstance(other, Node):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class RRTStar(Planner):
    """
    RRT* (RRT Star) implementation - optimizing version of RRT.
    """

    def __init__(self, obstacle_threshold: int = 200, max_iter: int = 5000, 
                 step_size: int = 2, goal_sample_rate: float = 0.1,
                 search_radius: float = 10.0):
        super().__init__(obstacle_threshold)
        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.search_radius = search_radius  # Radius for finding neighbors
        self.grid: Optional[Grid] = None
        self.nodes: List[Node] = []

    def plan_path(self, grid: Grid, start: Point, end: Point) -> Tuple[Optional[Path], Optional[float]]:
        """
        Plan a path from start to end using RRT*.
        Returns (Path, total_cost) if found, otherwise (None, None).
        """
        self.grid = grid
        self.nodes = []
        
        # Validate start and end
        if not self.is_valid_point(start):
            print(f"Start point ({start.x}, {start.y}) is invalid")
            return None, None
        if not self.is_valid_point(end):
            print(f"End point ({end.x}, {end.y}) is invalid")
            return None, None

        # Initialize tree with start node
        start_node = Node(start.x, start.y)
        start_node.cost = 0.0
        self.nodes.append(start_node)
        
        best_goal_node = None
        
        for iteration in range(self.max_iter):
            # Sample random point (or goal with some probability)
            if random.random() < self.goal_sample_rate:
                random_node = Node(end.x, end.y)
            else:
                random_node = self.sample_random_node()
            
            # Find nearest node in tree
            nearest_node = self.find_nearest_node(random_node)
            
            # Steer from nearest toward random (limit by step_size)
            new_node = self.steer(nearest_node, random_node)
            
            # Check if path to new_node is collision-free
            if self.is_collision_free(nearest_node, new_node):
                # Find neighbors within search radius
                neighbors = self.find_neighbors(new_node, self.search_radius)
                
                # Choose best parent (minimize cost)
                best_parent = nearest_node
                min_cost = nearest_node.cost + self.distance(nearest_node, new_node)
                
                for neighbor in neighbors:
                    if self.is_collision_free(neighbor, new_node):
                        cost = neighbor.cost + self.distance(neighbor, new_node)
                        if cost < min_cost:
                            best_parent = neighbor
                            min_cost = cost
                
                # Add new node with best parent
                new_node.parent = best_parent
                new_node.cost = min_cost
                self.nodes.append(new_node)
                
                # Rewire tree - check if neighbors should use new_node as parent
                for neighbor in neighbors:
                    if neighbor == best_parent:
                        continue
                    
                    new_cost = new_node.cost + self.distance(new_node, neighbor)
                    if new_cost < neighbor.cost and self.is_collision_free(new_node, neighbor):
                        neighbor.parent = new_node
                        neighbor.cost = new_cost
                        # Update costs of all descendants (propagate)
                        self.propagate_cost_to_leaves(neighbor)
                
                # Check if we're close enough to goal
                if self.distance(new_node, Node(end.x, end.y)) <= self.step_size:
                    # Try to connect directly to goal
                    goal_node = Node(end.x, end.y)
                    if self.is_collision_free(new_node, goal_node):
                        goal_node.parent = new_node
                        goal_node.cost = new_node.cost + self.distance(new_node, goal_node)
                        
                        # Keep the best goal connection
                        if best_goal_node is None or goal_node.cost < best_goal_node.cost:
                            if best_goal_node is not None and best_goal_node in self.nodes:
                                self.nodes.remove(best_goal_node)
                            best_goal_node = goal_node
                            self.nodes.append(goal_node)
        
        if best_goal_node is not None:
            print(f"RRT* found path with cost {best_goal_node.cost:.2f}")
            return self.extract_path(best_goal_node)
        
        print(f"RRT* failed to find path after {self.max_iter} iterations")
        return None, None

    def sample_random_node(self) -> Node:
        """Sample a random node in the grid."""
        x = random.randint(0, self.grid.width - 1)
        y = random.randint(0, self.grid.height - 1)
        return Node(x, y)

    def find_nearest_node(self, target: Node) -> Node:
        """Find the nearest node in the tree to the target."""
        nearest = min(self.nodes, key=lambda node: self.distance(node, target))
        return nearest

    def find_neighbors(self, node: Node, radius: float) -> List[Node]:
        """Find all nodes within radius of the given node."""
        neighbors = []
        for n in self.nodes:
            if n != node and self.distance(n, node) <= radius:
                neighbors.append(n)
        return neighbors

    def steer(self, from_node: Node, to_node: Node) -> Node:
        """
        Steer from from_node toward to_node, limited by step_size.
        Returns a new node at most step_size away from from_node.
        """
        dist = self.distance(from_node, to_node)
        
        if dist <= self.step_size:
            return Node(to_node.x, to_node.y)
        
        # Move step_size in direction of to_node
        theta = math.atan2(to_node.y - from_node.y, to_node.x - from_node.x)
        new_x = from_node.x + self.step_size * math.cos(theta)
        new_y = from_node.y + self.step_size * math.sin(theta)
        
        # Clamp to grid bounds
        new_x = max(0, min(self.grid.width - 1, int(round(new_x))))
        new_y = max(0, min(self.grid.height - 1, int(round(new_y))))
        
        return Node(new_x, new_y)

    def distance(self, node1: Node, node2: Node) -> float:
        """Euclidean distance between two nodes."""
        return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    def propagate_cost_to_leaves(self, parent_node: Node):
        """Propagate cost changes to all descendants of parent_node."""
        for node in self.nodes:
            if node.parent is not None and node.parent == parent_node:
                node.cost = parent_node.cost + self.distance(parent_node, node)
                self.propagate_cost_to_leaves(node)

    def is_collision_free(self, from_node: Node, to_node: Node) -> bool:
        """
        Check if the path between two nodes is collision-free.
        Uses Bresenham's line algorithm to check every cell.
        """
        x0, y0 = from_node.x, from_node.y
        x1, y1 = to_node.x, to_node.y
        
        # Check both endpoints
        if not self.is_valid_point(Point(x0, y0)):
            return False
        if not self.is_valid_point(Point(x1, y1)):
            return False
        
        # Bresenham's line algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            # Check current cell
            if not self.is_valid_point(Point(x, y)):
                return False
            
            # Reached end?
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return True

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
        
        # 255 = unknown
        if cell == 255:
            return False
        
        # 1-254 are traversable
        return True

    def extract_path(self, goal_node: Node) -> Tuple[Path, float]:
        """Extract path from start to goal by following parent pointers."""
        path_nodes = []
        current = goal_node
        
        while current is not None:
            path_nodes.append(current)
            current = current.parent
        
        # Reverse to get start -> goal
        path_nodes.reverse()
        
        # Convert to Path
        path_points = [Point(node.x, node.y) for node in path_nodes]
        
        # Cost is already stored in goal_node
        total_cost = goal_node.cost
        
        return Path(path_points), total_cost


# Test code
import matplotlib.pyplot as plt

def main():
    random.seed(42)
    np.random.seed(42)
    
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

    # Run RRT*
    rrt_star = RRTStar(
        obstacle_threshold=200, 
        max_iter=5000, 
        step_size=2, 
        goal_sample_rate=0.1,
        search_radius=10.0
    )
    path, cost = rrt_star.plan_path(g, start, goal)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title("RRT* Path on Costmap (0=obstacle, 254=free, 255=unknown)")
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

    # Plot the tree (optional - shows exploration)
    for node in rrt_star.nodes:
        if node.parent is not None:
            ax.plot([node.x, node.parent.x], [node.y, node.parent.y], 
                   'c-', linewidth=0.5, alpha=0.3)

    # Plot start and goal
    ax.plot(start.x, start.y, "go", markersize=10, label="Start")
    ax.plot(goal.x, goal.y, "ro", markersize=10, label="Goal")

    # Plot path if found
    if path is not None and path.points:
        xs = [p.x for p in path.points]
        ys = [p.y for p in path.points]
        ax.plot(xs, ys, "b-", linewidth=2, label=f"RRT* Path (cost={cost:.1f})")
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