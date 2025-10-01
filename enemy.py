from astar import astar

class Enemy:
    def __init__(self, start, goal, hp=100, speed=3, gold=10, name="Basic", color=(255, 255, 255)):
        self.pos = start       # current grid cell (x, y)
        self.goal = goal
        self.path = []         # list of cells from start → goal
        self.t = 0.0           # interpolation between path[0] and path[1]
        self.hp = hp
        self.speed = speed
        self.gold = gold
        self.name = name     # e.g. "fast", "tank", "basic"
        self.color = color

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
        return self.hp <= 0

# --- Utilities for multiple enemies ---
def recompute_enemy_paths(enemies, grid, goal):
    """Recompute paths for all enemies."""
    for e in enemies:
        e.set_path(astar(grid, e.pos, goal))

def update_enemies(enemies, dt, goal):
    """Update all enemies; return list of enemies that reached the goal."""
    reached = []
    for e in enemies:
        e.update(dt)
        if e.reached_goal():
            reached.append(e)
    return reached

class BasicEnemy(Enemy):
    def __init__(self, start, goal):
        super().__init__(start, goal, hp=100, speed=3, gold=6, color=(255, 200, 50), name="Basic")
        
class FastEnemy(Enemy):
    def __init__(self, start, goal):
        super().__init__(start, goal, hp=50, speed=5, gold=3, color=(255, 160, 40), name="Fast")

class TankEnemy(Enemy):
    def __init__(self, start, goal):
        super().__init__(start, goal, hp=250, speed=1, gold=20, color=(160, 50, 200), name="Tank")