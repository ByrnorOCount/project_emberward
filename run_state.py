import json, os
from level import Level, EnemyGroup

STARTING_HP = 10

class Player:
    """Tracks player stats that persist across a run."""
    def __init__(self, hp=STARTING_HP):
        self.hp = hp
        self.gold = 0

class RunState:
    """Manages the state of a single game run, including player stats and level progression."""
    def __init__(self):
        self.player = Player(hp=STARTING_HP)
        self.current_level_id = 0
        self.levels = [
            {"id": 0, "name": "First Level", "cleared": False},
            {"id": 1, "name": "Second Level", "cleared": False}
        ]
        self.phase = "map"

        # These are temporary for a single fight, not part of the persistent run state
        self.wave_index = 0
        self.wave_total = 0
        self.deck_count = 0

def create_run_state():
    """Initializes core HP, gold, level map, player position, etc. for a new run."""
    return RunState()

def advance_to_next_level(run_state, level_id):
    """Moves player to the chosen level and loads its data."""
    run_state.current_level_id = level_id
    # mark as not yet cleared if not present
    for n in run_state.levels:
        if n["id"] == level_id:
            n["cleared"] = False
            break
    run_state.phase = "fight"
    with open(os.path.join("data", "levels.json")) as f:
        levels_data = json.load(f)["levels"]
        # Find the level data that matches the ID from the map node.
        # The map nodes have id 0 and 1, but the json has id 1 and 2.
        # We'll assume a +1 mapping for now.
        json_level_id = level_id + 1
        level_data = next((l for l in levels_data if l["id"] == json_level_id), None)
        if not level_data:
            raise ValueError(f"Could not find level with id {json_level_id} in data/levels.json")
        return Level(
            name=level_data["name"],
            gold=level_data["gold"],
            waves=[[
                EnemyGroup(g["type"], g["count"], g.get("spawn_interval", 0.5))
                for g in w["sequence"]
            ] for w in level_data["waves"]]
        )