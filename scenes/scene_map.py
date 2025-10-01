import pygame
from render.render_map import draw_map
from run_state import create_run_state
from .scene_fight import FightScene

class MapScene:
    def __init__(self, game):
        self.game = game
        self.run_state = create_run_state()

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.game.change_scene(FightScene(self.game, self.run_state))

    def update(self, dt):
        pass  # later: node selection, rewards

    def render(self, screen):
        draw_map(screen, self.run_state)
        pygame.display.flip()