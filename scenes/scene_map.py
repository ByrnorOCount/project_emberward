import sys, pygame
from render.render_map import draw_map_screen
from .scene_fight import FightScene

class MapScene:
    def __init__(self, game, run_state):
        self.game = game
        self.run_state = run_state

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.game.change_scene(FightScene(self.game, self.run_state))

    def update(self, dt):
        pass  # later: node selection, rewards

    def render(self, screen):
        screen.fill((30, 30, 30))
        draw_map_screen(screen, self.run_state)
        pygame.display.flip()