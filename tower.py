import json, os, math

# Load tower data from JSON
with open(os.path.join("data", "towers.json")) as f:
    _TOWER_DATA = {t["id"]: t for t in json.load(f)["towers"]}

class Tower:
    def __init__(self, x, y, tower_id="bolt"):
        self.x = x
        self.y = y
        self.id = tower_id
        data = _TOWER_DATA[tower_id]

        self.name = data["name"]
        self.damage = data["damage"]
        self.range = float(data["range"])
        self.fire_rate = float(data["fire_rate"])
        self.cost = data["cost"]
        self.color = tuple(data["color"])
        self.cooldown = 0.0
        self.kills = 0

    def in_range(self, enemy):
        """Distance uses grid units (cells). Enemy.pos is (x,y) in grid coords."""
        ex, ey = enemy.pos
        dx = self.x - ex
        dy = self.y - ey
        return math.hypot(dx, dy) <= self.range

    def get_stats(self):
        """Returns a dictionary of the tower's display-friendly stats."""
        return {
            "Name": self.name,
            "Damage": self.damage,
            "Range": round(self.range, 2),
            "Fire Rate": round(self.fire_rate, 2),
            "Kills": self.kills,
            "Cost": self.cost
        }

    def update(self, enemies, dt):
        """Called each frame. If cooldown finished and there is a target, produce a Projectile instance (not applied to enemies directly).
        Returns: Projectile instance or None."""
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

class CannonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, tower_id="cannon")

    def update(self, enemies, dt):
        proj = super().update(enemies, dt)
        if proj:
            proj.splash_radius = 1.5
        return proj

TOWER_CLASSES = {
    "bolt": Tower, 
    "swift": Tower, 
    "cannon": CannonTower
}

# ===================
# Utilities
# ===================

def create_tower(tower_id, x, y):
    """Create tower instance from JSON ID."""
    TowerClass = TOWER_CLASSES.get(tower_id, Tower)
    if TowerClass is Tower:
        return Tower(x, y, tower_id=tower_id)
    return TowerClass(x, y)

def can_place_tower(grid, x, y, towers):
    """Checks if a tower can be placed at a given grid coordinate."""
    if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
        return False
    # Check if a tower already exists at this position
    if any(t.x == x and t.y == y for t in towers):
        return False
    cell_value = grid[y][x]
    # Can place on any cell that is a piece (represented by a string key)
    return isinstance(cell_value, str)

def update_towers(towers, enemies, dt, projectiles):
    """Update towers; append spawned projectiles into projectiles list."""
    for tower in towers:
        p = tower.update(enemies, dt)
        if p:
            projectiles.append(p)

def tower_data():
    """Exposes raw tower data from JSON."""
    return _TOWER_DATA