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
    
def rotate_piece(cells, rotation):
    """Rotates a piece's relative cell coordinates by 90° increments."""
    out = cells
    for _ in range(rotation):
        out = [(-y, x) for x, y in out]
        minx = min(x for x, _ in out)
        miny = min(y for _, y in out)
        out = [(x - minx, y - miny) for x, y in out]
    return out
    
def can_place_piece(grid, gx, gy, cells):
    """Checks if piece fits legally at grid position (inside bounds, no collision)."""
    h = len(grid); w = len(grid[0])
    for x, y in cells:
        ax, ay = gx + x, gy + y
        if ax < 0 or ay < 0 or ax >= w or ay >= h or grid[ay][ax] != 0:
            return False
    return True

def get_absolute_cells(gx, gy, cells):
    """Converts relative piece coords into absolute grid coords for placement."""
    return [(gx + x, gy + y) for x, y in cells]