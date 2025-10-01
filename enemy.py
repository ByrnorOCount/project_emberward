import json, os
from astar import astar

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
        self.speed = data["speed"]
        self.gold = data["gold"]
        self.etype = etype     # e.g. "fast", "tank", "basic"
        self.color = tuple(data["color"])

    def set_path(self, path):
        """Assign a new path and reset progress."""
        self.path = path if path else []
        self.t = 0.0

    def update(self, dt):
        """Move along the path according to speed."""
        if not self.path or len(self.path) < 2:
            return
        p0, p1 = self.path[0], self.path[1]
        self.t += self.speed * dt
        if self.t >= 1.0:
            # Snap to next cell
            self.pos = p1
            self.path.pop(0)
            self.t = 0.0

    def reached_goal(self):
        """True if this enemy has arrived at its goal."""
        return len(self.path) <= 1 and self.pos == self.goal

    def is_dead(self):
        return self.hp <= 0

# --- Utilities for multiple enemies ---
def recompute_enemy_paths(enemies, grid, goal):
    """Recompute paths for all enemies."""
    for e in enemies:
        e.set_path(astar(grid, e.pos, goal))

def spawn_wave(spawn_points, goal, wave_seq):
    """Spawn enemies following ordered sequence from waves.json"""
    enemies = []
    for step in wave_seq:  # [{type, count}, ...]
        for _ in range(step["count"]):
            for sp in spawn_points:
                e = Enemy(sp, goal, etype=step["type"])
                enemies.append(e)
    return enemies

def update_enemies(enemies, dt, goal):
    """Update all enemies; return list of enemies that reached the goal."""
    reached = []
    for e in enemies:
        e.update(dt)
        if e.reached_goal():
            reached.append(e)
    return reached

def enemy_data():
    return _ENEMY_DATA
