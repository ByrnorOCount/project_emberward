from grid import OBSTACLE, TOWER

def can_place_tower(grid, x, y):
    """Checks if a tower can be placed on given cell (must be a placeable obstacle aka the tetris pieces)."""
    return grid[y][x] == OBSTACLE

def place_tower(grid, x, y, towers):
    """Marks cell as TOWER and creates tower object."""
    grid[y][x] = TOWER
    towers.append((x, y))

def get_enemies_in_range(tower, enemies):
    """Returns a list of enemies within a tower's attack range."""
    
def update_towers(towers, enemies, dt):
    """Handles tower logic: target enemies, shoot projectiles, etc."""

def upgrade_tower(tower):
    """Upgrades tower stats if player has enough gold."""
