import math

class Projectile:
    """
    Projectile tracks a moving projectile from a source (world coords x,y)
    to a target enemy object. Coordinates are in grid-space (cells),
    not pixels. FightScene will use camera.cell_size to turn into pixels.
    """
    def __init__(self, x, y, target, damage, speed=8.0, lifetime=5.0, origin_tower=None):
        # x,y are floats in grid coordinates (cell units)
        self.x = float(x)
        self.y = float(y)
        self.target = target  # reference to Enemy instance
        self.damage = damage
        self.speed = speed  # cell units per second
        self.dead = False
        self.lifetime = lifetime
        self.age = 0.0
        self.origin_tower = origin_tower

    def update(self, dt, enemies):
        """Move toward target. On hit, mark dead and apply damage (caller may apply)."""
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True
            return

        if not self.target or self.target.is_dead():
            self.dead = True
            return

        tx, ty = self.target.pos
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist <= 0.1:
            self._on_hit(enemies)
            return

        nx = dx / dist
        ny = dy / dist
        travel = self.speed * dt
        # if travel overshoots, snap and apply damage
        if travel >= dist:
            self._on_hit(enemies)
        else:
            self.x += nx * travel
            self.y += ny * travel

    def _on_hit(self, enemies):
        """Apply damage to target and any enemies within splash radius."""
        self.dead = True
        impact_pos = self.target.pos

        # Apply splash damage if the attribute exists
        if hasattr(self, "splash_radius") and self.splash_radius > 0:
            for enemy in enemies:
                if not enemy.is_dead():
                    ex, ey = enemy.pos
                    dist_to_impact = math.hypot(ex - impact_pos[0], ey - impact_pos[1])
                    if dist_to_impact <= self.splash_radius:
                        enemy.hp -= self.damage
        else:
            # single target damage
            self.target.hp -= self.damage