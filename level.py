from enemy import FastEnemy, BasicEnemy, TankEnemy

class Level:
    def __init__(self, name, waves, gold=50, total_wave = 0):
        self.waves = waves
        self.name = name
        self.gold = gold
        self.total_wave = total_wave

class EnemyGroup:
    def __init__(self, name, count, spawn_interval=0.5):
        """
        enemy_type: class reference, e.g., FastEnemy
        count: number of enemies in this group
        spawn_interval: seconds between each spawn
        """
        self.name = name
        self.count = count
        self.spawn_interval = spawn_interval

        
class Player:
    def __init__(self, gold, wave_index, deck_count, hp = 100):
        self.current_node = 0
        self.hp = hp
        self.gold = gold
        self.wave_index = wave_index
        self.deck_count = deck_count


level1 = Level(
    name="1",
    waves=[
        # Wave 1
        [EnemyGroup(FastEnemy, count=8, spawn_interval=0.3)],

        # Wave 2
        [EnemyGroup(BasicEnemy, 6, 0.4),
         EnemyGroup(TankEnemy, 2, 0.6)],

        # Wave 3
        [EnemyGroup(FastEnemy, 6, 0.3),
         EnemyGroup(TankEnemy, 4, 0.5),
         EnemyGroup(TankEnemy, 4, 0.7)],
    ]
)