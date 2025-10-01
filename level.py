from enemy import FastEnemy, BasicEnemy, TankEnemy

class Level:
    def __init__(self, name, waves, core_hp=10, gold=50, total_wave = 0, deck_count=20):
        self.waves = waves
        self.name = name
        self.core_hp =core_hp
        self.gold = gold
        self.total_wave = total_wave
        deck_count = deck_count
        
class Player:
    def __init__(self, hp, gold, wave_index, deck_count):
        self.current_node = 0
        self.hp = hp
        self.gold = gold
        self.wave_index = wave_index
        self.deck_count = deck_count


level1 = Level(
    name = "1",
    waves = [
        # wave 1: light fast enemies
        [FastEnemy for _ in range(8)],
        # wave 2: basic + 1 tank
        [BasicEnemy for _ in range(6)] + 
        [TankEnemy for _ in range(2)],
        # wave 3: mixed heavier set
        [FastEnemy for _ in range(6)] + 
        [TankEnemy for _ in range(4)] +
        [TankEnemy for _ in range(4)]
        ])    