import pygame
import math
from run_state import advance_to_next_level
from render.render_map import draw_map
from .scene_fight import FightScene
from sound_manager import play_music, play_sound

class MapScene:
    def __init__(self, game):
        self.game = game
        self.run_state = game.run_state
        self.hovered_node_id = None
        
        w, h = self.game.screen.get_size()
        self.level_nodes = []
        if self.run_state and self.run_state.levels:
            num_levels = len(self.run_state.levels)
            for i, level_info in enumerate(self.run_state.levels):
                is_accessible = (i == 0) or self.run_state.is_level_cleared(self.run_state.levels[i-1]["id"])
                pos_x = w * (i + 1) // (num_levels + 1)
                self.level_nodes.append({
                    "id": level_info["id"],
                    "name": level_info["name"],
                    "pos": (pos_x, h // 2),
                    "radius": 48,
                    "accessible": is_accessible
                })

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from .scene_menu import MenuScene
                self.game.change_scene(MenuScene(self.game))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                mx, my = event.pos
                for node in self.level_nodes:
                    dist = math.hypot(mx - node["pos"][0], my - node["pos"][1])
                    if dist <= node["radius"] and node.get("accessible", True):
                        level = advance_to_next_level(self.run_state, node["id"])
                        self.game.change_scene(FightScene(self.game, level))

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.hovered_node_id = None
        for node in self.level_nodes:
            dist = math.hypot(mx - node["pos"][0], my - node["pos"][1])
            if dist <= node["radius"]:
                self.hovered_node_id = node["id"]
                break

    def render(self, screen):
        draw_map(screen, self.level_nodes, self.hovered_node_id)
        pygame.display.flip()