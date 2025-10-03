# Remember to update whenever a new function/file is added

# TODO:
# add a third level
# have at least 5 waves to each level
# upgrade towers?
# more towers and enemies?
# add search algo selection on sidebar
# MapScene.update()
# incoming wave
# victory screen, press any key to move back to map
# show levels not yet unlocked as gray/locked
# sound effects, music, assets

# main.py
class Game:
    def change_scene(self, new_scene):
        """Replace current scene with a new one."""
    def run(self):
        """Main game loop."""

# scenes/scene_menu.py
class Button:
    pass
class MenuScene:
    def handle_input(self, event):
        """Handles input events from user."""
    def update(self, dt):
        """Updates game state."""
    def render(self, screen):
        """Renders the game scene."""

# scenes/scene_map.py
class MapScene:
    def handle_input(self, event):
        """Handles input events from user."""
    def update(self, dt):
        """Updates map state."""
    def render(self, screen):
        """Renders the map scene."""

# scenes/scene_fight.py
class FightScene:
    # Core Logic
    def handle_input(self, events):
        """Handles all user input for the fight scene."""
    def update(self, dt):
        """Updates game state (enemies, towers, projectiles)."""
    def render(self, screen):
        """Renders the entire fight scene."""
    # Piece & Tower Placement
    def select_new_piece(self):
        """Selects the next piece from the deck."""
    def place_piece(self, gx, gy):
        """Attempts to place the current piece at a grid location."""
    def place_tower(self, gx, gy):
        """Attempts to place the selected tower at a grid location."""
    def _handle_sidebar_click(self, mx, my):
        """Handles clicks on the sidebar UI. Returns True if a sidebar element was
        clicked, False otherwise."""
    def select_cell_in_grid(self, mx, my):
        """Handles a click on the main grid for placement or selection."""
    def select_existing_tower(self, gx, gy):
        """Selects a tower at a grid location to show its stats."""
    # Camera & Coordinates
    def screen_to_grid(self, sx, sy):
        """Maps screen pixel to grid coordinate, taking camera into account."""
    def grid_to_screen(self, gx, gy):
        """Maps grid coordinate to screen pixel center, taking camera into account."""
    def start_panning(self, mx, my):
        """Begins a camera pan operation."""
    def update_panning(self, e):
        """Updates camera position during a pan."""
    def stop_panning(self):
        """Stops a camera pan operation."""
    def zoomimg(self, e):
        """Zooms the camera in or out."""
    # Misc Helpers
    def spawn_wave(self):
        """Initializes the spawning sequence for the current wave."""
    def show_tower_range(self, e):
        """Sets the tower to be hovered for displaying its range."""
class Camera:
    pass
class Phase(Enum): # type: ignore
    pass

# level.py
class Level:
    """Contains data for a single level, including its waves."""
class EnemyGroup:
    """Defines a group of enemies within a wave."""

# run_state.py
class Player:
    """Tracks player stats that persist across a run."""
class RunState:
    """Manages the state of a single game run, including player stats and level progression."""
def create_run_state():
    """Initializes core HP, gold, level map, player position, etc. for a new run."""
def advance_to_next_level(run_state, level_id):
    """Moves player to the chosen level and loads its data."""

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
def load_map_layout(map_id): # currently empty
    """Loads fixed obstacles layout for given map id as non-placeable cells."""

# piece.py
def get_piece_shapes():
    """Returns dictionary of tetris-shaped pieces (list of relative coords)."""
def rotate_piece(cells, rotation):
    """Rotates a piece's relative cell coordinates by 90° increments."""
def can_place_piece(grid, gx, gy, cells, start, goal):
    """Checks if piece fits legally at grid position (in bounds, no collision, doesn't block path)."""
def is_path_blocked(grid, cells, start, goal):
    """Check if placing cells on grid would block path from start to goal."""
def get_absolute_cells(gx, gy, cells):
    """Converts relative piece coords into absolute grid coords for placement."""

# pathfinding.py
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
        """True if the enemy's HP is at or below zero."""
def create_enemy(etype, start, goal):
    """Factory function to create an enemy instance from its type ID."""
def update_enemies(enemies, dt, goal):
    """Update all enemies; return list of enemies that reached the goal."""
def recompute_enemy_paths(enemies, grid, goal):
    """Recompute paths for all enemies, typically after the grid changes."""
def enemy_data():
    """Exposes raw enemy data from JSON."""

# tower.py
class Tower:
    def in_range(self, enemy):
        """Distance uses grid units (cells). Enemy.pos is (x,y) in grid coords."""
    def get_stats(self):
        """Returns a dictionary of the tower's display-friendly stats."""
    def update(self, enemies, dt):
        """Called each frame. If cooldown finished and there is a target, produce a Projectile instance (not applied to enemies directly).
        Returns: Projectile instance or None."""
class CannonTower(Tower):
    pass
def create_tower(tower_id, x, y):
    """Factory function to create a tower instance from its type ID."""
def can_place_tower(grid, x, y):
    """Checks if a tower can be placed at a given grid coordinate."""
def update_towers(towers, enemies, dt, projectiles):
    """Update towers; append spawned projectiles into projectiles list."""
def tower_data():
    """Exposes raw tower data from JSON."""

# projectile.py
class Projectile:
    def update(self, dt):
        """Moves the projectile towards its target and handles collision."""

# render/render_menu.py
def draw_menu(surf):
    """Draws the main menu screen, including title and background."""
def draw_button(surf, btn):
    """Draws a single interactive button."""
def make_rainbow_surface(size):
    """Creates a rainbow gradient surface for the menu background effect."""
def draw_grid_background(surf, cell_size=64):
    """Draws a subtle gray grid background."""

# render/render_map.py
def draw_map(surf, level):
    """Draws the level selection map screen."""

# render/render_fight.py
def cell_rect(x, y, cell_size):
    """Returns the rect tuple for a cell at (x, y)."""
def draw_grid(surf, grid, cell_size):
    """Draws the grid cells (empty, obstacle, tower) on the surface using given cell_size."""
def draw_zoomed_map(surf, grid, camera, **kwargs):
    """Draw the fight grid, enemies, towers, projectiles at zoomed scale with camera offset."""
def draw_tower_preview(surf, gx, gy, tower, cell_size, valid, camera):
    """Draws a ghost/preview of a tower at the mouse position."""
def draw_piece_preview(surf, gx, gy, rotated_cells, cell_size, valid, camera):
    """Draws a ghost/preview of a piece at the mouse position."""
def draw_tower_range(surf, tower, cell_size, camera, color):
    """Draws a circle indicating a tower's attack range."""
def draw_projectiles(surf, projectiles, cell_size, camera):
    """Draws all active projectiles."""
def draw_sidebar(surf, level, player, placement_mode, selected_tower=None):
    """Draws the UI sidebar with game state info, tower selection, etc."""
def sidebar_click_test(surf, mx, my):
    """Returns the name of the sidebar element that was clicked."""
def tower_list_click_test(surf, mx, my):
    """Returns the index of the tower in the list that was clicked."""