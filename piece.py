from grid import OBSTACLE
from pathfinding import find_path
def get_piece_shapes():
    """Returns dictionary of tetris-shaped pieces (list of relative coords)."""
    return {
        'I': [(0,0),(1,0),(2,0),(3,0)],
        'O': [(0,0),(1,0),(0,1),(1,1)],
        'T': [(0,0),(1,0),(2,0),(1,1)],
        'L': [(0,0),(0,1),(0,2),(1,2)],
        'J': [(1,0),(1,1),(1,2),(0,2)],
        'S': [(1,0),(2,0),(0,1),(1,1)],
        'Z': [(0,0),(1,0),(1,1),(2,1)]
    }
    
PIECE_COLORS = {
    'I': (0, 240, 240),   # Cyan
    'O': (240, 240, 0),   # Yellow
    'T': (160, 0, 240),   # Purple
    'L': (240, 160, 0),   # Orange
    'J': (0, 0, 240),     # Blue
    'S': (0, 240, 0),     # Green
    'Z': (240, 0, 0),     # Red
}

def rotate_piece(cells, rotation):
    """Rotates a piece's relative cell coordinates by 90° increments."""
    out = cells
    for _ in range(rotation):
        out = [(-y, x) for x, y in out]
        minx = min(x for x, _ in out)
        miny = min(y for _, y in out)
        out = [(x - minx, y - miny) for x, y in out]
    return out

def can_place_piece(grid, gx, gy, cells, start, goal):
    """Checks if piece fits legally at grid position (inside bounds, no collision)."""
    h = len(grid); w = len(grid[0])
    absolute_cells = []
    for x, y in cells:
        ax, ay = gx + x, gy + y
        if ax < 0 or ay < 0 or ax >= w or ay >= h or grid[ay][ax] != 0:
            return False
        absolute_cells.append((ax, ay))
    
    if is_path_blocked(grid, absolute_cells, start, goal):
        return False
    return True

def is_path_blocked(grid, cells, start, goal):
    """Check if placing cells on grid would block path from start to goal."""
    temp_grid = [row[:] for row in grid]
    for x, y in cells:
        temp_grid[y][x] = OBSTACLE
    
    # A* returns a path of length > 1 if a path is found.
    # It returns [start] (length 1) or None if no path is found.
    path = find_path(temp_grid, start, goal)
    return not path or len(path) <= 1

def get_absolute_cells(gx, gy, cells):
    """Converts relative piece coords into absolute grid coords for placement."""
    return [(gx + x, gy + y) for x, y in cells]