# pathfinding.py
# added algorithms to switch
import time

from heapq import heappush, heappop
from grid import is_walkable, get_neighbors4, get_cost

# A*
def astar(grid, start, goal):
    """Computes shortest path from start to goal using A* on grid."""
    # 0. Check if goal is walkable from the start
    if not is_walkable(grid, *goal):
        return None, 0

    # 1. Initialize data structure
    openq = []
    heappush(openq, (0, start)) # (f_score, node)
    came_from = {}
    g_score = {start: 0}
    visited_count = 0
    visited_nodes_set = {start}

    while openq:
        # 2. Get the most promising node
        _, current = heappop(openq)

        # 3. Goal reached: reconstruct and return the path
        if current == goal:
            path = []
            # ... backtrack using came_from ...
            c = goal
            while c in came_from:
                path.append(c)
                c = came_from[c]
            path.append(start)
            path.reverse()
            return path, visited_nodes_set

        # 4. Explore neighbors
        for neighbor in get_neighbors4(*current):
            if not is_walkable(grid, *neighbor):
                continue

            # 5. Calculate cost to this neighbor
            tentative_g_score = g_score.get(current, float('inf')) + get_cost(grid, *neighbor)

            # 6. If this path to neighbor is better, record it and add to queue
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heappush(openq, (f_score, neighbor))
                came_from[neighbor] = current
                visited_nodes_set.add(neighbor)
                visited_count += 1

    # 7. No path found
    return None, visited_nodes_set

# UCS (Uniform Cost Search) - Functionally identical to Dijkstra on a grid with uniform costs.
def ucs(grid, start, goal):
    """Computes the shortest path from start to goal using Uniform Cost Search."""
    if not is_walkable(grid, *goal):
        return None, 0
    openq = [(0, start)]
    came_from = {}
    g_score = {start: 0}
    visited_nodes_set = {start}
    while openq:
        current_cost, current_node = heappop(openq)
        if current_node == goal:
            path = []
            c = goal
            while c in came_from:
                path.append(c)
                c = came_from[c]
            path.append(start)
            path.reverse()
            return path, visited_nodes_set
        if current_cost > g_score.get(current_node, float('inf')):
            continue

        for neighbor in get_neighbors4(*current_node):
            if not is_walkable(grid, *neighbor):
                continue
            new_cost = g_score.get(current_node, float('inf')) + get_cost(grid, *neighbor)
            if new_cost < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = new_cost
                came_from[neighbor] = current_node
                visited_nodes_set.add(neighbor)
                heappush(openq, (new_cost, neighbor))
    return None, visited_nodes_set

# greedy BFS
def greedy_bfs(grid, start, goal):
    """Greedy Best-First Search. Chooses path based only on closeness to goal."""
    if not is_walkable(grid, *goal):
        return None, 0
    openq = []
    heappush(openq, (heuristic(start, goal), start))
    came_from = {}
    visited = {start}
    while openq:
        _, current = heappop(openq)
        if current == goal:
            path = []
            c = goal
            while c in came_from:
                path.append(c)
                c = came_from[c]
            path.append(start)
            path.reverse()
            return path, visited

        for neighbor in get_neighbors4(*current):
            if is_walkable(grid, *neighbor) and neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                heappush(openq, (heuristic(neighbor, goal), neighbor))
    return None, visited

# DFS
def dfs(grid, start, goal):
    """Depth-First Search. Finds a path, but it will be long and inefficient."""
    if not is_walkable(grid, *goal):
        return None, 0
    stack = [(start, [start])]
    visited = {start}
    while stack:
        current, path = stack.pop()
        if current == goal:
            return path, visited

        for neighbor in get_neighbors4(*current):
            if is_walkable(grid, *neighbor) and neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                stack.append((neighbor, new_path))
    return None, visited

def heuristic(a, b):
    """Manhattan distance heuristic for A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_path(grid, start, goal, algorithm="astar"):
    """
    General function to find a path using a specified algorithm.
    Returns a tuple: (path, stats_dict, visited_nodes_set)
    """
    start_time = time.perf_counter()
    path, visited_nodes_set = None, set()

    if algorithm == "astar":
        path, visited_nodes_set = astar(grid, start, goal)
    elif algorithm == "ucs":
        path, visited_nodes_set = ucs(grid, start, goal)
    elif algorithm == "greedy_bfs":
        path, visited_nodes_set = greedy_bfs(grid, start, goal)
    elif algorithm == "dfs":
        path, visited_nodes_set = dfs(grid, start, goal)
    else:
        print(f"Warning: Unknown algorithm '{algorithm}', defaulting to A*.")
        path, visited_nodes_set = astar(grid, start, goal)

    end_time = time.perf_counter()
    visited_count = len(visited_nodes_set) if visited_nodes_set else 0
    path_length = len(path) if path else 0
    stats = {"time_ms": (end_time - start_time) * 1000, "visited": visited_count, "length": path_length}
    return path, stats, visited_nodes_set