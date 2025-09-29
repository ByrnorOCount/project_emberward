from grid import OBSTACLE, TOWER
import math

class Tower:
    def __init__(self, x, y, damage=10, range_=3, fire_rate=1.0, tower_type=0):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range_
        self.fire_rate = fire_rate
        self.cooldown = 0.0
        self.tower_type = tower_type  # 0,1,2 — different visuals / stats

        # quick tweak of stats by type
        if tower_type == 0:  # basic
            self.damage = 12
            self.range = 3
            self.fire_rate = 1.0
        elif tower_type == 1:  # fast
            self.damage = 6
            self.range = 2.5
            self.fire_rate = 2.0
        elif tower_type == 2:  # heavy
            self.damage = 30
            self.range = 2.8
            self.fire_rate = 0.6

    def in_range(self, enemy):
        """True if the enemy is in range of this tower."""
        ex, ey = enemy.pos
        dx, dy = self.x - ex, self.y - ey
        return math.sqrt(dx*dx + dy*dy) <= self.range

    def update(self, enemies, dt):
        """Attack enemies if cooldown is ready."""
        self.cooldown -= dt
        if self.cooldown <= 0:
            targets = [e for e in enemies if self.in_range(e) and not e.is_dead()]
            if targets:
                # simple targeting: first in list
                target = targets[0]
                target.hp -= self.damage
                self.cooldown = 1.0 / self.fire_rate

# --- Placement helpers ---
def can_place_tower(grid, x, y):
    # Only allow tower placement on player-placed OBSTACLE cells (tetris pieces)
    if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
        return False
    return grid[y][x] == OBSTACLE

def place_tower(grid, x, y, towers, tower_type=0):
    grid[y][x] = TOWER
    tower = Tower(x, y, tower_type=tower_type)
    towers.append(tower)
    return tower

def update_towers(towers, enemies, dt):
    for t in towers:
        t.update(enemies, dt)