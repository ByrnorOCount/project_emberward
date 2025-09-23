import pygame, sys
from grid import create_grid, set_cells, EMPTY, OBSTACLE, TOWER
from piece import get_piece_shapes, rotate_piece, can_place_piece, get_absolute_cells
from astar import astar
from enemy import create_enemy, update_enemy, set_enemy_path
from tower import can_place_tower, place_tower
from renderer import draw_grid, draw_piece_preview, draw_enemies, draw_towers, draw_dashed_path

CELL_SIZE = 32
GRID_W, GRID_H = 20, 15
SCREEN_W, SCREEN_H = GRID_W * CELL_SIZE, GRID_H * CELL_SIZE

def show_start_menu(screen):
    """Displays a start screen until user presses a key or clicks."""
    font_big = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)
    
    title = font_big.render("Emberward Clone", True, (255, 255, 255))
    instructions = font_small.render("Press any key or click to start", True, (200, 200, 200))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
            
        screen.fill((30, 30, 30))
        # Draw centered text
        screen.blit(title, (SCREEN_W//2 - title.get_width()//2, SCREEN_H//2 - 100))
        screen.blit(instructions, (SCREEN_W//2 - instructions.get_width()//2, SCREEN_H//2))
        pygame.display.flip()

def show_map_screen(screen, run_state):
    """Displays roguelite map with nodes and paths; lets player pick next node."""

def start_new_run():
    """Initializes run state: core HP, gold, node map, starting node."""

def main():
    """Main entry: sets up pygame, run loop, handles flow between menu/map/fights."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Emberward Clone")
    clock = pygame.time.Clock()

    show_start_menu(screen)

    grid = create_grid(GRID_W, GRID_H)
    pieces = get_piece_shapes()
    current_piece = pieces['T']
    rotation = 0

    start, goal = (0, 0), (GRID_W - 1, GRID_H - 1)
    enemy = create_enemy(start, goal)

    towers = []
    placing_tower = False

    while True:
        dt = clock.tick(60) / 1000
        mouse_x, mouse_y = pygame.mouse.get_pos()
        gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    rotation = (rotation - 1) % 4
                elif event.key == pygame.K_e:
                    rotation = (rotation + 1) % 4
                elif event.key == pygame.K_t:
                    placing_tower = not placing_tower
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if placing_tower:
                    if can_place_tower(grid, gx, gy):
                        place_tower(grid, gx, gy, towers)
                        set_enemy_path(enemy, astar(grid, start, goal))
                else:
                    rotated = rotate_piece(current_piece,rotation)
                    if can_place_piece(grid, gx, gy, rotated):
                        cells = get_absolute_cells(gx, gy, rotated)
                        set_cells(grid, cells, OBSTACLE)
                        set_enemy_path(enemy, astar(grid, start, goal))

        update_enemy(enemy, dt)

        screen.fill((30, 30, 30))
        draw_grid(screen, grid, CELL_SIZE)
        draw_enemies(screen, [enemy], CELL_SIZE)
        draw_towers(screen, towers, CELL_SIZE)

        if enemy['path']:
            draw_dashed_path(screen, enemy['path'], CELL_SIZE)

        rotated = rotate_piece(current_piece, rotation)
        valid = can_place_piece(grid, gx, gy, rotated)
        if not placing_tower:
            draw_piece_preview(screen, gx, gy, rotated, CELL_SIZE, valid)

        pygame.display.flip()
    
def handle_input(events, game):
    """Processes mouse/keyboard events for piece/tower placement, zoom, quitting."""
    
def update(game, dt):
    """Updates enemies, towers, paths, run state transitions, etc."""
    
def render(screen, game):
    """Draws current scene (menu/map/fight) based on game state."""

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()