from grid import OBSTACLE, TOWER
import math

class Tower:
    def __init__(self, x, y, damage=10, range_=3, fire_rate=1.0):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range_
        self.fire_rate = fire_rate
        self.cooldown = 0.0

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
                target = targets[0]  # simple: attack first in range
                target.hp -= self.damage
                self.cooldown = 1.0 / self.fire_rate

# --- Placement helpers ---
def can_place_tower(grid, x, y):
    return grid[y][x] == OBSTACLE

def place_tower(grid, x, y, towers):
    grid[y][x] = TOWER
    tower = Tower(x, y)
    towers.append(tower)
    return tower

def update_towers(towers, enemies, dt):
    for t in towers:
        t.update(enemies, dt)