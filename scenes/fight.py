import sys, pygame
from grid import create_grid, set_cells, OBSTACLE
from piece import get_piece_shapes, rotate_piece, can_place_piece, get_absolute_cells
from astar import astar
from enemy import Enemy, update_enemies, spawn_wave
from tower import can_place_tower, place_tower, update_towers
from renderer import draw_grid, draw_piece_preview, draw_enemies, draw_towers, draw_dashed_path

class FightScene:
    def __init__(self, game, run_state):
        self.game = game
        self.run_state = run_state

        self.grid = create_grid(30, 20)
        self.start, self.goal = (0, 0), (15, 10)

        self.enemies = []
        self.towers = []

        # quick test wave: 3 basic enemies
        self.enemies = spawn_wave([self.start], self.goal, [{"hp": 100, "speed": 2, "gold": 5} for _ in range(3)])

        self.pieces = get_piece_shapes()
        self.rotation = 0
        self.placing_tower = False

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.rotation = (self.rotation - 1) % 4
                elif event.key == pygame.K_e:
                    self.rotation = (self.rotation + 1) % 4
                elif event.key == pygame.K_t:
                    self.placing_tower ^= True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // 32, my // 32
                if self.placing_tower:
                    if can_place_tower(self.grid, gx, gy):
                        place_tower(self.grid, gx, gy, self.towers)
                        # re-path all enemies
                        for e in self.enemies:
                            e.set_path(astar(self.grid, e.pos, self.goal))
                else:
                    rotated = rotate_piece(self.pieces['T'], self.rotation)
                    if can_place_piece(self.grid, gx, gy, rotated):
                        cells = get_absolute_cells(gx, gy, rotated)
                        set_cells(self.grid, cells, OBSTACLE)
                        # re-path all enemies
                        for e in self.enemies:
                            e.set_path(astar(self.grid, e.pos, self.goal))

    def update(self, dt):
        # enemies move
        reached = update_enemies(self.enemies, dt, self.goal)
        for e in reached:
            self.run_state["core_hp"] -= 1  # example: lose 1 HP per leak
            self.enemies.remove(e)

        # towers attack
        update_towers(self.towers, self.enemies, dt)

        # remove dead enemies, add gold
        for e in list(self.enemies):
            if e.is_dead():
                self.run_state["gold"] += e.gold
                self.enemies.remove(e)

    def render(self, screen):
        screen.fill((30, 30, 30))
        draw_grid(screen, self.grid, 32)

        draw_enemies(screen, self.enemies, 32)
        draw_towers(screen, self.towers, 32)

        # dashed path for the first enemy (optional)
        if self.enemies and self.enemies[0].path:
            draw_dashed_path(screen, self.enemies[0].path, 32)

        # piece preview
        mx, my = pygame.mouse.get_pos()
        gx, gy = mx // 32, my // 32
        rotated = rotate_piece(self.pieces['T'], self.rotation)
        valid = can_place_piece(self.grid, gx, gy, rotated)
        if not self.placing_tower:
            draw_piece_preview(screen, gx, gy, rotated, 32, valid)

        pygame.display.flip()