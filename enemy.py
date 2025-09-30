from astar import astar

class Enemy:
    def __init__(self, start, goal, hp=100, speed=3, gold=10, etype="basic"):
        self.pos = start       # current grid cell (x, y)
        self.goal = goal
        self.path = []         # list of cells from start → goal
        self.t = 0.0           # interpolation between path[0] and path[1]
        self.hp = hp
        self.speed = speed
        self.gold = gold
        self.etype = etype     # e.g. "fast", "tank", "basic"

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

def spawn_wave(spawn_points, goal, wave_config):
    """
    Create a wave of enemies.
    wave_config: list of dicts, e.g.
    [{"hp": 50, "speed": 4, "gold": 5, "etype": "fast"}, {"hp": 200, "speed": 2, "gold": 20, "etype": "tank"}]
    """
    enemies = []
    for sp in spawn_points:
        for cfg in wave_config:
            # Pull known kwargs, allow etype
            hp = cfg.get("hp", 100)
            speed = cfg.get("speed", 3)
            gold = cfg.get("gold", 10)
            etype = cfg.get("etype", "basic")
            e = Enemy(sp, goal, hp=hp, speed=speed, gold=gold, etype=etype)
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
