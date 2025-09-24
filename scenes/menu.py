import sys, pygame
from renderer import draw_menu
from run_state import create_run_state
from .map import MapScene

class MenuScene:
    def __init__(self, game):
        self.game = game

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                run_state = create_run_state()
                self.game.change_scene(MapScene(self.game, run_state))

    def update(self, dt):
        pass  # not sure

    def render(self, screen):
        buttons = [
            {"text": "Play", "action": "play"},
            {"text": "Options", "action": "options"},
            {"text": "Quit", "action": "quit"},
        ]
        screen.fill((30, 30, 30))
        draw_menu(screen, buttons)
        pygame.display.flip()
