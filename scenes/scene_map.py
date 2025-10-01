import pygame
from level import level1
from render.render_map import draw_map
from .scene_fight import FightScene

class MapScene:
    def __init__(self, game):
        self.game = game
        self.level = level1

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.game.change_scene(FightScene(self.game, self.level))

    def update(self, dt):
        pass  # later: node selection, rewards

    def render(self, screen):
        draw_map(screen, self.level)
        pygame.display.flip()