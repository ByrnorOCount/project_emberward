from grid import OBSTACLE, TOWER
import math

# We'll import Projectile lazily in the update to avoid circular imports.
# Tower.update will return a Projectile instance (or None) which the fight scene
# will append into its projectile list.

class Tower:
    def __init__(self, x, y, damage=10, range_=3.0, fire_rate=1.0, name="Tower", color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = float(range_)
        self.fire_rate = float(fire_rate)
        self.cooldown = 0.0
        self.kills = 0
        self.name = name
        self.color = color

    def in_range(self, enemy):
        """Distance uses grid units (cells). Enemy.pos is (x,y) in grid coords."""
        ex, ey = enemy.pos
        dx = self.x - ex
        dy = self.y - ey
        return math.hypot(dx, dy) <= self.range

    def get_stats(self):
        return {
            "Name": self.name,
            "Type": self.tower_type,
            "Damage": self.damage,
            "Range": round(self.range, 2),
            "Fire Rate": round(self.fire_rate, 2),
            "Kills": getattr(self, "kills", 0)
        }

    def update(self, enemies, dt):
        """
        Called each frame. If cooldown finished and there is a target,
        produce a Projectile instance (not applied to enemies directly).
        Returns: Projectile instance or None.
        """
        # lazy import to avoid cycles
        from projectile import Projectile

        self.cooldown -= dt
        if self.cooldown > 0:
            return None

        # target selection: nearest enemy within range (or prefer lowest hp / earliest)
        targets = [e for e in enemies if not e.is_dead() and self.in_range(e)]
        if not targets:
            return None

        # simple: choose enemy closest to tower
        target = min(targets, key=lambda e: math.hypot(e.pos[0] - self.x, e.pos[1] - self.y))

        # spawn projectile at tower center (grid coords)
        proj = Projectile(self.x, self.y, target, damage=self.damage, speed=8.0, origin_tower=self)
        # reset cooldown
        self.cooldown = 1.0 / self.fire_rate
        return proj

# Placement helpers
def can_place_tower(grid, x, y):
    if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
        return False
    return grid[y][x] == OBSTACLE

def update_towers(towers, enemies, dt, projectiles):
    """Update towers; append spawned projectiles into projectiles list."""
    for tower in towers:
        p = tower.update(enemies, dt)
        if p:
            projectiles.append(p)


class BoltTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=12, range_=3.0, fire_rate=1.0, name="Bolt", color=(220, 40, 40))


class SwiftTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=6, range_=2.6, fire_rate=2.0, name="Swift", color=(40, 180, 40))


class CannonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, damage=30, range_=5, fire_rate=0.6, name="Cannon", color=(40, 120, 220))

    def update(self, enemies, dt):
        proj = super().update(enemies, dt)
        if proj:
            proj.splash_radius = 1.5
        return proj