# Remember to update whenever a new function/file is added

# main.py
def show_start_menu(screen):
    """Displays title, Play, Options, Quit buttons; handles clicks to transition."""
def show_map_screen(screen, run_state):
    """Displays roguelite map with nodes and paths; lets player pick next node."""
def start_new_run():
    """Initializes run state: core HP, gold, node map, starting node."""
def main():
    """Main entry: sets up pygame, run loop, handles flow between menu/map/fights."""
def handle_input(events, game):
    """Processes mouse/keyboard events for piece/tower placement, zoom, quitting."""
def update(game, dt):
    """Updates enemies, towers, paths, run state transitions, etc."""
def render(screen, game):
    """Draws current scene (menu/map/fight) based on game state."""

# grid.py
def create_grid(w, h):
    """Returns a 2D list initialized with EMPTY cells."""
def in_bounds(x, y, w, h):
    """Checks if a coordinate is inside the grid bounds."""
def is_walkable(grid, x, y):
    """Returns True if a cell is EMPTY and walkable."""
def set_cells(grid, cells, state):
    """Sets a list of (x,y) cells to the given state (EMPTY/OBSTACLE/TOWER)."""
def cell_center(x, y, cell_size):
    """Returns pixel center coordinates of a grid cell for drawing."""
def get_neighbors4(x, y):
    """Returns 4-neighbor coordinates for A* pathfinding."""
def load_map_layout(map_id):
    """Loads fixed obstacles layout for given map id as non-placeable cells."""
    
# piece.py
def get_piece_shapes():
    """Returns dictionary of tetris-shaped pieces (list of relative coords)."""
def rotate_piece(cells, rotation):
    """Rotates a piece's relative cell coordinates by 90° increments."""
def can_place_piece(grid, gx, gy, cells):
    """Checks if piece fits legally at grid position (inside bounds, no collision)."""
def get_absolute_cells(gx, gy, cells):
    """Converts relative piece coords into absolute grid coords for placement."""

# astar.py
def heuristic(a, b):
    """Manhattan distance for A*."""
def astar(grid, start, goal):
    """Computes shortest path from start to goal using A* on grid."""

# enemy.py
def create_enemy(start, goal):
    """Creates an enemy dict/object with position, path, speed."""
def set_enemy_path(enemy, path):
    """Assigns a new path to enemy and resets progress along it."""
def update_enemy(enemy, dt):
    """Moves enemy along its path over time."""
def enemy_reached_goal(enemy):
    """Returns True if enemy has arrived at goal cell."""
def recompute_enemy_paths(enemies, grid, goal):
    """Recomputes paths for all enemies after grid change."""
def spawn_wave(enemies, spawn_points, goal, wave_config):
    """Spawns a wave of enemies at multiple spawn points with given config."""
def update_enemies(enemies, dt, goal):
    """Moves all enemies; returns list of enemies reaching the goal."""

# tower.py
def can_place_tower(grid, x, y):
    """Checks if a tower can be placed on given cell (must be a placeable obstacle aka the tetris pieces)."""
def place_tower(grid, x, y, towers):
    """Marks cell as TOWER and creates tower object."""
def get_enemies_in_range(tower, enemies):
    """Returns a list of enemies within a tower's attack range."""
def update_towers(towers, enemies, dt):
    """Handles tower logic: target enemies, shoot projectiles, etc."""
def upgrade_tower(tower):
    """Upgrades tower stats if player has enough gold."""

# renderer.py
def cell_rect(x, y, cell_size):
    """Returns the rect tuple for a cell at (x, y)."""
def draw_grid(surf, grid, cell_size):
    """Draws the grid cells (empty, obstacle, tower) on the screen."""
def draw_piece_preview(surf, gx, gy, cells, cell_size, valid):
    """Draws a ghost/preview version of a piece at mouse position with color based on validity."""
def draw_enemies(surf, enemies, cell_size):
    """Draws all enemies as circles or sprites on the grid."""
def draw_towers(surf, towers, cell_size):
    """Draws towers at their locations."""
def draw_dashed_path(surf, path, cell_size, dash_len=8, gap_len=6):
    """Draws a dashed line along the enemy's A* path."""
def draw_arrowhead(surf, start, end, color):
    """Draws a small arrowhead at the end of a path segment."""
def draw_menu(surf, buttons):
    """Draws start menu UI with clickable buttons."""
def draw_map_screen(surf, run_state):
    """Draws roguelite map nodes, connections, and player progress."""
def draw_info_bars(surf, run_state):
    """Draws sidebars with core HP, gold, wave info, etc."""
def draw_zoomed_map(surf, grid, camera):
    """Draws map with camera zoom and panning applied."""

# run_state.py
def create_run_state():
    """Initializes core HP, gold, node map, player position, etc."""
def advance_to_next_node(run_state, node_id):
    """Moves player to the chosen node and loads its map layout."""