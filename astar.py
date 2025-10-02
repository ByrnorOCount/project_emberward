# TODO Add option to switch between search algos to compare to A*
# add search algo selection on sidebar

from heapq import heappush, heappop
from grid import is_walkable, get_neighbors4

def heuristic(a, b):
    """Manhattan distance for A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
def astar(grid, start, goal):
    """Computes shortest path from start to goal using A* on grid."""
    if not is_walkable(grid, *goal):
        return None
    openq = []
    heappush(openq, (0, start))
    came = {}
    g = {start: 0}
    while openq:
        _, cur = heappop(openq)
        if cur == goal:
            break
        for nx, ny in get_neighbors4(*cur): 
            if not is_walkable(grid, nx, ny):
                continue
            ng = g[cur] + 1
            if ng < g.get((nx, ny), 1e9):
                g[(nx, ny)] = ng
                came[(nx, ny)] = cur
                heappush(openq, (ng + heuristic((nx, ny), goal), (nx, ny)))
    if goal not in came:
        return [start]
    path = []
    c = goal
    while c != start:
        path.append(c)
        c = came[c]
    path.append(start); path.reverse()
    return path
