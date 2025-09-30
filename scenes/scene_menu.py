import sys, pygame
from render.render_menu import draw_menu
from run_state import create_run_state
from .scene_map import MapScene

class MenuScene:
    def __init__(self, game):
        self.game = game

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                w, h = self.game.screen.get_size()
                btn_w, btn_h = 300, 70
                start_y = h // 2
                spacing = 100
                buttons = [
                    {"text": "Play", "action": "play"},
                    {"text": "Options", "action": "options"},
                    {"text": "Quit", "action": "quit"},
                ]
                for i, b in enumerate(buttons):
                    rect = pygame.Rect(0, 0, btn_w, btn_h)
                    rect.center = (w // 2, start_y + i * spacing)
                    if rect.collidepoint(mx, my):
                        if b["action"] == "play":
                            run_state = create_run_state()
                            self.game.change_scene(MapScene(self.game, run_state))
                        elif b["action"] == "quit":
                            pygame.quit(); sys.exit()
                        elif b["action"] == "options":
                            print("Options clicked!")  # TODO: add options menu

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
