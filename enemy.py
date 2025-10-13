import json, os
from pathfinding import find_path
from assets import get_assets
from sound_manager import play_sound

# Load enemy archetypes
with open(os.path.join("data", "enemies.json")) as f:
    _ENEMY_DATA = {e["id"]: e for e in json.load(f)["enemies"]}

class Enemy:
    def __init__(self, start, goal, etype="basic"):
        data = _ENEMY_DATA[etype]
        self.pos = start       # current grid cell (x, y)
        self.goal = goal
        self.path = []         # list of cells from start → goal
        self.t = 0.0           # interpolation between path[0] and path[1]
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.speed = data["speed"]
        self.gold = data["gold"]
        self.etype = etype     # e.g. "fast", "tank", "basic"
        self.color = tuple(data["color"])
        assets = get_assets()
        self.image = assets["enemies"].get(etype)

    def set_path(self, path):
        """Assign a new path and reset progress."""
        self.path = path if path else []
        self.t = 0.0

    def update(self, dt):
        """Move along the path according to speed, smoothly interpolating."""
        if not self.path or len(self.path) < 2:
            return

        p0 = self.path[0]
        p1 = self.path[1]

        self.t += self.speed * dt
        if self.t >= 1.0:
            # Move to next cell
            self.pos = p1
            self.path.pop(0)
            self.t = 0.0
        else:
            # Smoothly interpolate between p0 and p1
            self.pos = (p0[0] + (p1[0] - p0[0]) * self.t,
                        p0[1] + (p1[1] - p0[1]) * self.t)

    def reached_goal(self):
        """True if this enemy has arrived at its goal."""
        return len(self.path) <= 1 and self.pos == self.goal

    def is_dead(self):
        isDead = self.hp <= 0
        if (isDead):
            play_sound("enemy_die.mp3")
            return True
        return False

ENEMY_CLASSES = {
    "basic": Enemy, 
    "fast": Enemy, 
    "tank": Enemy
}

# ===================
# Utilities
# ===================
def create_enemy(etype, start, goal):
    """Create enemy instance from JSON type."""
    return ENEMY_CLASSES.get(etype, Enemy)(start, goal, etype=etype)

def update_enemies(enemies, dt, goal):
    """Update all enemies; return list of enemies that reached the goal."""
    reached = []
    for e in enemies:
        e.update(dt)
        if e.reached_goal():
            reached.append(e)
    return reached

def recompute_enemy_paths(enemies, grid, goal, algorithm="astar"):
    """Recompute paths for all enemies."""
    for e in enemies:
        start_node = (round(e.pos[0]), round(e.pos[1]))
        # use find_path
        e.set_path(find_path(grid, start_node, goal, algorithm))

def enemy_data():
    """Exposes raw enemy data from JSON."""
    return _ENEMY_DATA