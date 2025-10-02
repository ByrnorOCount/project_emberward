class Level:
    def __init__(self, name, waves, gold=50, total_wave=0):
        self.waves = waves
        self.name = name
        self.gold = gold
        self.total_wave = total_wave

class EnemyGroup:
    def __init__(self, name, count, spawn_interval=0.5):
        self.name = name
        self.count = count
        self.spawn_interval = spawn_interval
