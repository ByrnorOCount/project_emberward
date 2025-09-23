def create_enemy(start, goal, hp=100, speed=3, gold=10):
    """Creates an enemy dict/object with position, path, speed."""
    return {
        'pos': start,
        'goal': goal,
        'path': [],
        't': 0.0,
        'hp': hp,
        'speed': speed,
        'gold': gold
    }

def set_enemy_path(enemy, path):
    """Assigns a new path to enemy and resets progress along it."""
    enemy['path'] = path if path else []
    enemy['t'] = 0.0
    
def update_enemy(enemy, dt):
    """Moves enemy along its path over time."""
    if not enemy['path'] or len(enemy['path']) < 2: 
        return
    p0 = enemy['path'][0]
    p1 = enemy['path'][1]
    x0, y0 = p0
    x1, y1 = p1
    enemy['t'] += enemy['speed'] * dt
    if enemy['t'] >= 1.0:
        enemy['path'].pop(0)
        enemy['t'] = 0.0
    
def enemy_reached_goal(enemy):
    """Returns True if enemy has arrived at goal cell."""
    
def recompute_enemy_paths(enemies, grid, goal):
    """Recomputes paths for all enemies after grid change."""
    
def spawn_wave(enemies, spawn_points, goal, wave_config):
    """Spawns a wave of enemies at multiple spawn points with given config."""

def update_enemies(enemies, dt, goal):
    """Moves all enemies; returns list of enemies reaching the goal."""
