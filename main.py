import sys
import pygame
import traceback
from scenes.scene_menu import MenuScene

CELL_SIZE = 32
GRID_W, GRID_H = 30, 20
SCREEN_W, SCREEN_H = GRID_W * CELL_SIZE, GRID_H * CELL_SIZE
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Emberward Clone")
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene = MenuScene(self)

    def change_scene(self, new_scene):
        """Replace current scene with a new one."""
        self.scene = new_scene

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.scene.handle_input(event)
            self.scene.update(dt)
            self.scene.render(self.screen)

def main():
    try:
        Game().run()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()