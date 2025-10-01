import pygame, random
from enum import Enum
from level import Level, Player, level1
from constants import *
from grid import cell_center, create_grid, set_cells, OBSTACLE, TOWER
from piece import get_piece_shapes, rotate_piece, can_place_piece, get_absolute_cells
from astar import astar
from enemy import update_enemies, recompute_enemy_paths
from enemy import FastEnemy, BasicEnemy, TankEnemy
from tower import BoltTower, SwiftTower, CannonTower, can_place_tower, update_towers
from render.render_fight import draw_zoomed_map, draw_tower_preview, draw_piece_preview, tower_list_click_test, sidebar_click_test, draw_projectiles, draw_sidebar, draw_tower_range

class FightScene:
    def __init__(self, game, level):
        self.game = game

        self.grid = create_grid(30, 20)
        self.gw = len(self.grid[0])
        self.gh = len(self.grid)

        self.start = (0, self.gh // 2)
        self.goal = (self.gw // 2, self.gh // 2)
        
        self.enemies = []
        self.towers = []
        self.projectiles = []

        self.camera = Camera(0, 0, 1.0, 36)

        # pieces / deck: 20 pieces randomly selected from available shapes
        self.pieces = get_piece_shapes()
        self.piece_keys = list(self.pieces.keys())
        # deck is a list of piece keys
        self.deck = [random.choice(self.piece_keys) for _ in range(20)]
        self.current_piece_key = None
        self.select_new_piece()
        self.rotation = 0
        self.is_placing_tower = False

        # tower selection: 0,1,2
        self.selected_tower = BoltTower  # 0/1/2 for 3 towers
        self.clicked_tower = None     # tower object clicked for stats panel
        self.hover_tower = None       # tower object currently hovered (for range display)
        
        self.current_wave_index = 0
        self.wave_spawned = False

        self.level = level
        self.player = Player(self.level.core_hp, self.level.gold, self.current_wave_index, len(self.deck))
        self.phase = Phase.Prepare

        # input helpers
        self.is_panning = False
        self._pan_start = (0,0)
        self._cam_start = (0,0)

    def select_new_piece(self):
        self.current_piece_key = self.deck[0] if self.deck else None
    
    def screen_to_grid(self, sx, sy):
        """Map screen pixel to grid coordinate, taking camera into account.
           returns (gx, gy) or (None, None) if outside grid area.
        """
        cs = int(self.camera.cell_size * self.camera.zoom)
        wx = sx - self.camera.offset_x
        wy = sy - self.camera.offset_y
        if wx < 0 or wy < 0:
            return (None, None)
        gx = int(wx // cs)
        gy = int(wy // cs)
        if 0 <= gx < self.gw and 0 <= gy < self.gh:
            return gx, gy
        return (None, None)

    def grid_to_screen(self, gx, gy):
        cs = int(self.camera.cell_size * self.camera.zoom)
        sx = gx * cs + cs//2 + self.camera.offset_x
        sy = gy * cs + cs//2 + self.camera.offset_y
        return sx, sy
    
    def handle_input(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q:
                self.rotation = (self.rotation - 1) % 4
            elif e.key == pygame.K_e:
                self.rotation = (self.rotation + 1) % 4
            elif e.key == pygame.K_t:
                self.is_placing_tower = not self.is_placing_tower
            elif e.key == pygame.K_1:
                self.selected_tower = BoltTower
            elif e.key == pygame.K_2:
                self.selected_tower = SwiftTower
            elif e.key == pygame.K_3:
                self.selected_tower = CannonTower
            elif e.key == pygame.K_EQUALS or e.key == pygame.K_PLUS:
                self.camera.zoom = min(2.5, self.camera.zoom + 0.1)
            elif e.key == pygame.K_MINUS:
                self.camera.zoom = max(0.6, self.camera.zoom - 0.1)
            elif e.key == pygame.K_ESCAPE:
                from scenes.scene_map import MapScene
                self.game.change_scene(MapScene(self.game, self.level))

        elif e.type == pygame.MOUSEWHEEL:
            self.zoomimg(e)

        elif e.type == pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            if e.button == pygame.BUTTON_RIGHT:
                self.start_panning(mx, my)
            elif e.button == pygame.BUTTON_LEFT:
                self.select_sidebar(mx, my)
                self.select_cell_in_grid(mx, my)

        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == pygame.BUTTON_RIGHT:
                self.stop_panning()

        elif e.type == pygame.MOUSEMOTION:
            self.update_panning(e)
            self.show_tower_range(e)

    def update(self, dt):
        # update enemies movement
        reached = update_enemies(self.enemies, dt, self.goal)
        for e in reached:
            self.player.hp -= 1
            if e in self.enemies:
                self.enemies.remove(e)

        # towers spawn projectiles via update_towers (appends to self.projectiles)
        update_towers(self.towers, self.enemies, dt, self.projectiles)

        # update projectiles (move & apply damage on hit)
        for p in list(self.projectiles):
            p.update(dt)
            if p.dead:
                # optionally, if the projectile's origin tower wants to count kills:
                # if p.target.is_dead(): increment kills on origin_tower
                if hasattr(p, "origin_tower") and p.origin_tower and p.target.is_dead():
                    p.origin_tower.kills = getattr(p.origin_tower, "kills", 0) + 1
                self.projectiles.remove(p)

        # remove dead enemies and award gold
        for e in list(self.enemies):
            if e.is_dead():
                self.player.gold += e.gold
                if e in self.enemies:
                    self.enemies.remove(e)

        # check wave completion
        if self.wave_spawned and not self.enemies and not any(not p.dead for p in self.projectiles):
            # wave was spawned and there are no enemies and no in-flight projectiles
            self.wave_spawned = False
            self.current_wave_index += 1
            self.player.wave_index = self.current_wave_index
            if self.current_wave_index >= len(self.level.waves):
                self.phase = Phase.Victory
            else:
                self.phase = Phase.Prepare

    def render(self, screen):
        screen.fill((18, 18, 18))

        # Step 1: compute preview path/validity
        preview_path = astar(self.grid, self.start, self.goal)  # default: current path
        preview_valid = True
            
        mx, my = pygame.mouse.get_pos()
        mouse_gx, mouse_gy = self.screen_to_grid(mx, my)
        if self.phase is Phase.Prepare and mouse_gx is not None and not self.is_placing_tower and self.current_piece_key is not None:
            shape = self.pieces[self.current_piece_key]
            rotated = rotate_piece(shape, self.rotation)
            valid = can_place_piece(self.grid, mouse_gx, mouse_gy, rotated, self.start, self.goal)
            if valid:
                from copy import deepcopy
                test_grid = deepcopy(self.grid)
                cells = get_absolute_cells(mouse_gx, mouse_gy, rotated)
                set_cells(test_grid, cells, OBSTACLE)
                new_path = astar(test_grid, self.start, self.goal)
                if new_path:
                    preview_path = new_path
                    preview_valid = True
                else:
                    preview_valid = False

        # Step 2: draw map with path
        draw_zoomed_map(screen, self.grid, self.camera,
            enemies=self.enemies, towers=self.towers,
            projectiles=self.projectiles,
            path=preview_path, is_path_valid=preview_valid
        )

        # Step 3: draw core icon
        cs = int(self.camera.cell_size * self.camera.zoom)
        goal_gx, goal_gy = self.goal
        cx, cy = cell_center(goal_gx, goal_gy, cs)
        sx = cx + self.camera.offset_x
        sy = cy + self.camera.offset_y
        pygame.draw.circle(screen, (180, 60, 60), (int(sx), int(sy)), max(6, cs//4))
        font = pygame.font.SysFont(DEFAULT_FONT_NAME, 16, bold=True)
        txt = font.render(str(self.player.hp), True, (255,255,255))
        screen.blit(txt, (int(sx - txt.get_width()//2), int(sy - txt.get_height()//2)))

        # Step 4: draw preview overlays
        if self.phase is Phase.Prepare and mouse_gx is not None:
            if self.is_placing_tower:
                valid = can_place_tower(self.grid, mouse_gx, mouse_gy)
                tmp_tower = self.selected_tower(mouse_gx, mouse_gy)
                draw_tower_preview(screen, mouse_gx, mouse_gy, tmp_tower,
                                   cell_size=self.camera.cell_size, valid=valid, camera=self.camera)
                if valid:
                    tmp_t = self.selected_tower(mouse_gx, mouse_gy)
                    draw_tower_range(screen, tmp_t, cell_size=self.camera.cell_size,
                                     camera=self.camera, color=(255,255,255,80))
            elif self.current_piece_key is not None:
                shape = self.pieces[self.current_piece_key]
                rotated = rotate_piece(shape, self.rotation)
                valid = can_place_piece(self.grid, mouse_gx, mouse_gy, rotated, self.start, self.goal)
                draw_piece_preview(screen, mouse_gx, mouse_gy, rotated,
                                   cell_size=self.camera.cell_size,
                                   valid=valid,
                                   camera=self.camera)

        # Step 5: range circles
        if self.hover_tower:
            draw_tower_range(screen, self.hover_tower,
                             cell_size=self.camera.cell_size,
                             camera=self.camera, color=(255,255,255,90))
        if self.clicked_tower and self.clicked_tower is not self.hover_tower:
            draw_tower_range(screen, self.clicked_tower,
                             cell_size=self.camera.cell_size,
                             camera=self.camera, color=(255,220,80,110))

        # Step 6: projectiles
        draw_projectiles(screen, self.projectiles,
                         cell_size=self.camera.cell_size, camera=self.camera)

        # Step 7: sidebar
        self.player.deck_count = len(self.deck)

        draw_sidebar(screen, self.level, self.player, self.is_placing_tower, selected_tower=self.clicked_tower)

        # Step 8: flip
        pygame.display.flip()

    def select_sidebar(self, mx, my):
        # left click: check sidebar Start Wave button
        sw_clicked = sidebar_click_test(self.game.screen, mx, my)  # helper in renderer
        if sw_clicked == "start_wave":
            if not self.wave_spawned and self.current_wave_index < len(self.level.waves):
                cfg = self.level.waves[self.current_wave_index]
                new_en = self.spawn_wave([self.start], self.goal, cfg)
                for en in new_en:
                    en.set_path(astar(self.grid, en.pos, self.goal))
                    self.enemies.append(en)
                self.wave_spawned = True
                self.phase = Phase.Running
        elif sw_clicked == "tower_list":
            # renderer can return which tower type region was clicked; we ask for a type id
            clicked_type = tower_list_click_test(self.game.screen, mx, my)
            if clicked_type is not None:
                self.selected_tower_type = clicked_type
        elif sw_clicked == "sidebar_tower_panel":
            # clicking the tower-stats section will deselect the tower
            self.clicked_tower = None

    def select_cell_in_grid(self, mx, my):
        if self.phase is not Phase.Prepare:
            return
        gx, gy = self.screen_to_grid(mx, my)
        outside_grid = gx is None or gy is None
        if outside_grid:
            return
        
        if self.is_placing_tower:
            self.place_tower(gx, gy)
        elif self.current_piece_key:
            self.place_piece(gx, gy)
        else:
            self.select_existing_tower(gx, gy)

    def place_tower(self, gx, gy):
        # if placing_tower, attempt to place tower on that cell
        if can_place_tower(self.grid, gx, gy):
            tower = self.selected_tower(gx, gy)
            self.towers.append(tower)
            self.grid[gy][gx] = TOWER
            recompute_enemy_paths(self.enemies, self.grid, self.goal)

    def place_piece(self, gx, gy):
        # if not placing tower and there's a current piece -> try place piece
        shape = self.pieces[self.current_piece_key]
        rotated = rotate_piece(shape, self.rotation)
        if can_place_piece(self.grid, gx, gy, rotated, self.start, self.goal):
            cells = get_absolute_cells(gx, gy, rotated)
            set_cells(self.grid, cells, OBSTACLE)
            if self.deck:
                self.deck.pop(0)
            self.select_new_piece()
            self.player.deck_count = len(self.deck)
            recompute_enemy_paths(self.enemies, self.grid, self.goal)

    def select_existing_tower(self, gx, gy):
        self.clicked_tower = None
        for tower in self.towers:
            if tower.x == gx and tower.y == gy:
                self.clicked_tower = tower
                break
        self.hover_tower = self.clicked_tower

    def zoomimg(self, e):
        if e.y > 0:
            self.camera.zoom = min(2.5, self.camera.zoom + 0.1)
        else:
            self.camera.zoom = max(0.6, self.camera.zoom - 0.1)

    def start_panning(self, mx, my):
        self.is_panning = True
        self._pan_start = (mx, my)
        self._cam_start = (self.camera.offset_x, self.camera.offset_y)

    def stop_panning(self):
        self.is_panning = False

    def update_panning(self, e):
        if not self.is_panning:
            return
        mx, my = e.pos
        dx = mx - self._pan_start[0]
        dy = my - self._pan_start[1]
        self.camera.offset_x = self._cam_start[0] + dx
        self.camera.offset_y = self._cam_start[1] + dy

    def show_tower_range(self, e):
        mx, my = e.pos
        gx, gy = self.screen_to_grid(mx, my)
        self.hover_tower = None
        if gx is not None:
            for t in self.towers:
                if t.x == gx and t.y == gy:
                    self.hover_tower = t
                    break

    def spawn_wave(self, spawn_points, goal, wave_config):
        """
        Create a wave of enemies.
        """
        enemies = []
        for sp in spawn_points:
            for EnemyClass in wave_config:
                e = EnemyClass(sp, goal)
                enemies.append(e)
        return enemies
    
class Camera:
    def __init__(self, offset_x, offset_y, zoom, cell_size):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
        self.cell_size = cell_size
    
class Phase(Enum):
    Prepare = 1
    Running = 2
    Victory = 3