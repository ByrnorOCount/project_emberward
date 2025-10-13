import sys, pygame
from constants import *
from render.render_menu import draw_menu, draw_button
from .scene_map import MapScene
from run_state import create_run_state
from sound_manager import play_music, play_sound

class Button:
    def __init__(self, text, action, center, size=(300, 70)):
        self.text = text
        self.action = action
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.font = pygame.font.SysFont(DEFAULT_FONT_NAME, 42, bold=True)
    
class MenuScene:
    def __init__(self, game):
        self.game = game
        w, h = self.game.screen.get_size()
        start_y = h // 2
        spacing = 100
        btn_datas = [
            {"text": "Play", "action": "play"},
            {"text": "Options", "action": "options"},
            {"text": "Quit", "action": "quit"},
        ]
        self.btns = []
        for i, btn_data in enumerate(btn_datas):
            center = (w // 2, start_y + i * spacing)
            self.btns.append(Button(btn_data["text"], btn_data["action"], center))
        play_music("menu_bg.mp3")

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.btns:
                if btn.rect.collidepoint(event.pos):
                    action = btn.action
                    if action == "play":
                        self.game.run_state = create_run_state()
                        self.game.change_scene(MapScene(self.game))
                    elif action == "quit":
                        pygame.quit()
                        sys.exit()
                    elif action == "options":
                        print("Options button pressed")

    def update(self, dt):
        pass # not sure

    def render(self, screen):
        draw_menu(screen)
        for btn in self.btns:
            draw_button(screen, btn)  
        pygame.display.flip()
