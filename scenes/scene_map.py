import pygame
import math
from run_state import advance_to_next_level
from render.render_map import draw_map
from .scene_fight import FightScene

class MapScene:
    def __init__(self, game):
        self.game = game
        self.run_state = game.run_state
        
        w, h = self.game.screen.get_size()
        self.level_nodes = []
        if self.run_state and self.run_state.levels:
            num_levels = len(self.run_state.levels)
            for i, level_info in enumerate(self.run_state.levels):
                # Only show levels that are cleared, or the first uncleared one.
                # If a level is not the first one, and the one before it is not cleared, stop.
                if i > 0 and not self.run_state.is_level_cleared(self.run_state.levels[i-1]["id"]):
                    break
                pos_x = w * (i + 1) // (num_levels + 1)
                self.level_nodes.append({
                    "id": level_info["id"],
                    "name": level_info["name"],
                    "pos": (pos_x, h // 2),
                    "radius": 48
                })

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                mx, my = event.pos
                for node in self.level_nodes:
                    dist = math.hypot(mx - node["pos"][0], my - node["pos"][1])
                    if dist <= node["radius"]:
                        level = advance_to_next_level(self.run_state, node["id"])
                        self.game.change_scene(FightScene(self.game, level))

    def update(self, dt):
        pass # later: node selection, rewards

    def render(self, screen):
        draw_map(screen, self.level_nodes)
        pygame.display.flip()