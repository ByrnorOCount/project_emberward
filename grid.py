EMPTY, OBSTACLE, FIXED_OBSTACLE = 0, 1, 2

def create_grid(w, h):
    """Returns a 2D list initialized with EMPTY cells."""
    return [[EMPTY for _ in range(w)] for _ in range(h)]
    
def in_bounds(x, y, w, h):
    """Checks if a coordinate is inside the grid bounds."""
    return 0 <= x < w and 0 <= y < h
    
def is_walkable(grid, x, y):
    """Returns True if a cell is EMPTY and walkable."""
    return in_bounds(x, y, len(grid[0]), len(grid)) and grid[y][x] == EMPTY
    
def set_cells(grid, cells, state):
    """Sets a list of (x,y) cells to the given state (EMPTY/OBSTACLE/TOWER)."""
    for x, y in cells:
        if in_bounds(x, y, len(grid[0]), len(grid)):
            grid[y][x] = state
    
def cell_center(x, y, cell_size):
    """Returns pixel center coordinates of a grid cell for drawing."""
    return x * cell_size + cell_size // 2, y * cell_size + cell_size // 2
    
def get_neighbors4(x, y):
    """Returns 4-neighbor coordinates for A* pathfinding."""
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]