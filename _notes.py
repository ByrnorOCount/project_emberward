# Remember to update whenever a new function/file is added

# main.py
class Game:
    def change_scene(self, new_scene):
        """Replace current scene with a new one."""
    def run(self):
        """Main game loop."""

# scenes/menu.py
class MenuScene:
    def handle_input(self, events):
        """Handles input events from user."""
    def update(self, dt):
        """Updates game state."""
    def render(self, screen):
        """Renders the game scene."""
# scenes/map.py
    # Same deal
# scenes/fight.py
    # Same deal

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
def is_path_blocked(grid, cells, start, goal):
    """Check if placing cells on grid would block path from start to goal."""
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
class Enemy:
    def set_path(self, path):
        """Assign a new path and reset progress."""
    def update(self, dt):
        """Move along the path according to speed."""
    def reached_goal(self):
        """True if this enemy has arrived at its goal."""
    def is_dead(self):
        pass
def recompute_enemy_paths(enemies, grid, goal):
    """Recompute paths for all enemies."""
def spawn_wave(spawn_points, goal, wave_config):
    """
    Create a wave of enemies.
    wave_config: list of dicts, e.g.
    [{"hp": 50, "speed": 4, "gold": 5, "etype": "fast"}, {"hp": 200, "speed": 2, "gold": 20, "etype": "tank"}]
    """
def update_enemies(enemies, dt, goal):
    """Update all enemies; return list of enemies that reached the goal."""

# tower.py
class Tower:
    def _name_for_type(self, t):
        pass
    def in_range(self, enemy):
        """Distance uses grid units (cells). Enemy.pos is (x,y) in grid coords."""
    def get_stats(self):
        pass
    def update(self, enemies, dt):
        """
        Called each frame. If cooldown finished and there is a target,
        produce a Projectile instance (not applied to enemies directly).
        Returns: Projectile instance or None.
        """
def can_place_tower(grid, x, y):
    pass
def place_tower(grid, x, y, towers):
    pass
def update_towers(towers, enemies, dt):
    """Update towers; append spawned projectiles into projectiles list."""

# render/fight.py
def cell_rect(x, y, cell_size):
    """Returns the rect tuple for a cell at (x, y)."""
def draw_grid(surf, grid, cell_size):
    """Draws the grid cells (empty, obstacle, tower) on the screen."""
def draw_zoomed_map(surf, grid, camera, enemies=None, towers=None, projectiles=None, draw_path=None):
    """Draws map with camera zoom and panning applied."""
def draw_tower_preview(surf, gx, gy, tower_type, cell_size, valid, camera):
    """Draws a ghost/preview version of a tower at mouse position with color based on validity."""
def draw_piece_preview(surf, gx, gy, rotated_cells, cell_size, valid, camera):
    """Draws a ghost/preview version of a piece at mouse position with color based on validity."""
def draw_tower_range(surf, tower, cell_size, camera, color=(255,255,255,80)):
    pass
def draw_projectiles(surf, projectiles, cell_size, camera):
    pass
def draw_sidebar(surf, run_state, selected_tower=None):
    pass
def sidebar_click_test(surf, mx, my):
    """Returns the name of the sidebar element that was clicked."""
def tower_list_click_test(surf, mx, my):
    """Returns the index of the tower that was clicked."""
# render/menu.py
def make_rainbow_surface(size):
    """Create a horizontal rainbow gradient surface, rotated diagonally."""
def draw_grid_background(surf, cell_size=64):
    """Draws a subtle gray grid background."""
def draw_menu(surf, buttons):
    """Draws animated start menu with title and interactive buttons."""
# render/map.py
def draw_map_screen(surf, run_state):
    """Draws roguelite map nodes, connections, and player progress."""

# run_state.py
def create_run_state():
    """Initializes core HP, gold, node map, player position, etc."""
def advance_to_next_node(run_state, node_id):
    """Moves player to the chosen node and loads its map layout."""

# projectile.py
class Projectile:
    """
    Projectile tracks a moving projectile from a source (world coords x,y)
    to a target enemy object. Coordinates are in grid-space (cells),
    not pixels. FightScene will use camera.cell_size to turn into pixels.
    """