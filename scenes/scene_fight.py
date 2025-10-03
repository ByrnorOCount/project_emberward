import pygame, random, sys
from enum import Enum
from constants import *
from grid import cell_center, create_grid, set_cells, OBSTACLE, TOWER, EMPTY, FIXED_OBSTACLE
from piece import get_piece_shapes, rotate_piece, can_place_piece, get_absolute_cells
from pathfinding import find_path
from enemy import update_enemies, create_enemy, recompute_enemy_paths
from tower import can_place_tower, update_towers, create_tower
from render.render_fight import draw_zoomed_map, draw_tower_preview, draw_piece_preview, tower_list_click_test, sidebar_click_test, draw_projectiles, draw_sidebar, draw_tower_range

class FightScene:
    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.run_state = game.run_state

        self.grid = create_grid(22, 20)
        self.gw = len(self.grid[0])
        self.gh = len(self.grid)

        # Pathfinding algorithm
        self.algorithms = ["astar", "dijkstra", "greedy_bfs", "dfs"]
        self.algo_index = 0
        self.pathfinding_algorithm = self.algorithms[self.algo_index]

        # Set spawn (top-left) and goal (center) points
        self.start = (0, 0)
        self.goal = (self.gw // 2, self.gh // 2)
        
        # Add random fixed obstacles
        obstacle_chance = 0.1
        for r in range(self.gh):
            for c in range(self.gw):
                if self.grid[r][c] == EMPTY and random.random() < obstacle_chance:
                    # Ensure start/goal and their neighbors are not blocked
                    if abs(r - self.start[1]) > 1 or abs(c - self.start[0]) > 1:
                        if abs(r - self.goal[1]) > 1 or abs(c - self.goal[0]) > 1:
                            self.grid[r][c] = FIXED_OBSTACLE

        self.enemies = []
        self.towers = []
        self.projectiles = []

        self.camera = Camera(0, 0, 1.0, 36)

        # pieces / deck: 20 pieces randomly selected from available shapes
        self.pieces = get_piece_shapes()
        self.piece_keys = list(self.pieces.keys())
        self.deck = [random.choice(self.piece_keys) for _ in range(20)]
        self.current_piece_key = None
        self.select_new_piece()
        self.rotation = 0        
        self.placement_mode = "neutral"  # "neutral", "piece", "tower"

        # tower selection: 0,1,2
        self.tower_types = ["bolt", "swift", "cannon"]
        self.selected_tower_type = 0
        self.selected_tower_id = self.tower_types[self.selected_tower_type]
        self.clicked_tower = None     # tower object clicked for stats panel
        self.hover_tower = None       # tower object currently hovered (for range display)
        
        # waves
        self.current_wave_index = 0
        self.wave_spawned = False

        # player
        self.player = self.run_state.player
        self.player.gold = self.level.gold # Set gold for this level
        self.wave_index = 0
        self.deck_count = len(self.deck)
        self.phase = Phase.Prepare

        # input helpers
        self.is_panning = False
        self._pan_start = (0,0)
        self._cam_start = (0,0)
        
        self.spawn_queue = []  # list of (EnemyClass, spawn_time)
        self.time_elapsed = 0.0
    
    # ===================
    # Core Logic 
    # ===================
    def handle_input(self, e):
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_q:   # counterclockwise rotation
                self.rotation = (self.rotation - 1) % 4
            elif e.key == pygame.K_e: # clockwise rotation
                self.rotation = (self.rotation + 1) % 4
            elif e.key == pygame.K_p: # piece placement
                self.placement_mode = "piece" if self.placement_mode != "piece" else "neutral"
            elif e.key == pygame.K_t: # tower placement
                self.placement_mode = "tower" if self.placement_mode != "tower" else "neutral"
            elif e.key == pygame.K_1: # tower hotkeys
                self.selected_tower_type = 0
                self.selected_tower_id = self.tower_types[0]
            elif e.key == pygame.K_2:
                self.selected_tower_type = 1
                self.selected_tower_id = self.tower_types[1]
            elif e.key == pygame.K_3:
                self.selected_tower_type = 2
                self.selected_tower_id = self.tower_types[2]
            elif e.key == pygame.K_EQUALS or e.key == pygame.K_PLUS:
                self.camera.zoom = min(2.5, self.camera.zoom + 0.1)
            elif e.key == pygame.K_MINUS:
                self.camera.zoom = max(0.6, self.camera.zoom - 0.1)
            elif e.key == pygame.K_ESCAPE:
                self.run_state.player.hp = self.player.hp  # Save HP
                from scenes.scene_map import MapScene
                self.game.change_scene(MapScene(self.game))
        elif e.type == pygame.MOUSEWHEEL:
            self.zoomimg(e)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            if e.button in (4, 5): # ignore wheel scroll (button 4/5)
                return
            if e.button == 3: # right click start panning
                self.start_panning(mx, my)
                return

            # Check for sidebar clicks first. If a click is not on the sidebar,
            # handle it as a grid click.
            if not self._handle_sidebar_click(mx, my):
                self.select_cell_in_grid(mx, my)

        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 3:
                self.is_panning = False
        elif e.type == pygame.MOUSEMOTION:
            if self.is_panning:
                self.update_panning(e)
            else:
                self.show_tower_range(e)
        
        # Handle game over input
        if self.phase == Phase.GameOver:
            if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                from scenes.scene_menu import MenuScene
                self.game.change_scene(MenuScene(self.game))

    def update(self, dt):
        if self.player.hp <= 0 and self.phase != Phase.GameOver:
            self.phase = Phase.GameOver
        
        if self.phase != Phase.Running:
            return
        self.time_elapsed += dt
        for info in list(self.spawn_queue):
            enemy_type, spawn_time = info
            if self.time_elapsed >= spawn_time:
                e = create_enemy(enemy_type, self.start, self.goal)
                e.set_path(find_path(self.grid, e.pos, self.goal, self.pathfinding_algorithm))
                self.enemies.append(e)
                self.spawn_queue.remove(info)
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
            p.update(dt, self.enemies)
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
            self.wave_index = self.current_wave_index
            if self.current_wave_index >= len(self.level.waves):
                # Mark level as cleared
                for level_node in self.run_state.levels:
                    if level_node["id"] == self.run_state.current_level_id:
                        level_node["cleared"] = True
                self.phase = Phase.Victory
            else:
                self.phase = Phase.Prepare

    def render(self, screen):
        screen.fill((18, 18, 18))
        # Step 1: compute preview path/validity
        preview_path = find_path(self.grid, self.start, self.goal, self.pathfinding_algorithm)  # added pathfinding_algorithm
        preview_valid = True
        mx, my = pygame.mouse.get_pos()
        mouse_gx, mouse_gy = self.screen_to_grid(mx, my)
        if mouse_gx is not None and self.placement_mode == "piece" and self.current_piece_key is not None:
            shape = self.pieces[self.current_piece_key]
            rotated = rotate_piece(shape, self.rotation)
            valid = can_place_piece(self.grid, mouse_gx, mouse_gy, rotated, self.start, self.goal, self.pathfinding_algorithm)
            if valid:
                from copy import deepcopy
                test_grid = deepcopy(self.grid)
                cells = get_absolute_cells(mouse_gx, mouse_gy, rotated)
                set_cells(test_grid, cells, OBSTACLE)
                new_path = find_path(test_grid, self.start, self.goal, self.pathfinding_algorithm)
                if new_path:
                    preview_path = new_path
                    preview_valid = True
                else:
                    preview_valid = False
        # Step 2: draw map with path
        draw_zoomed_map(screen, self.grid, self.camera,
            enemies=self.enemies, towers=self.towers,
            projectiles=self.projectiles,
            draw_path=preview_path, is_path_valid=preview_valid
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
        if mouse_gx is not None:
            if self.placement_mode == "tower":
                valid = can_place_tower(self.grid, mouse_gx, mouse_gy, self.towers)
                draw_tower_preview(screen, mouse_gx, mouse_gy, self.selected_tower_id,
                                   cell_size=self.camera.cell_size, valid=valid, camera=self.camera)
                if valid:
                    tid = ["bolt", "swift", "cannon"][self.selected_tower_type]
                    tmp_t = create_tower(tid, mouse_gx, mouse_gy)
                    draw_tower_range(screen, tmp_t, cell_size=self.camera.cell_size,
                                     camera=self.camera, color=(255, 255, 255, 80))
            elif self.placement_mode == "piece" and self.current_piece_key is not None:
                shape = self.pieces[self.current_piece_key]
                rotated = rotate_piece(shape, self.rotation)
                valid = can_place_piece(self.grid, mouse_gx, mouse_gy, rotated, self.start, self.goal, self.pathfinding_algorithm)
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
        self.deck_count = len(self.deck)
        draw_sidebar(screen, self.level, self.player, self.wave_index, self.deck_count,
                     self.placement_mode == "tower", selected_tower=self.clicked_tower,
                     algorithm=self.pathfinding_algorithm)
        # Step 8: flip
        if self.phase == Phase.GameOver:
            s = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            s.fill((0,0,0,180))
            screen.blit(s, (0,0))
            
            font_large = pygame.font.SysFont(DEFAULT_FONT_NAME, 72, bold=True)
            font_small = pygame.font.SysFont(DEFAULT_FONT_NAME, 24)
            
            go_text = font_large.render("Game Over", True, (255,255,255))
            hint_text = font_small.render("Press any key to return to menu", True, (200,200,200))
            screen.blit(go_text, (screen.get_width()//2 - go_text.get_width()//2, screen.get_height()//2 - go_text.get_height()//2 - 20))
            screen.blit(hint_text, (screen.get_width()//2 - hint_text.get_width()//2, screen.get_height()//2 + go_text.get_height()//2))
        pygame.display.flip()

    # ===================
    # Piece & Tower Placement
    # ===================
    def select_new_piece(self):
        """Selects the next piece from the deck."""
        self.current_piece_key = self.deck[0] if self.deck else None

    def place_piece(self, gx, gy):
        """Attempts to place the current piece at a grid location."""
        # if not placing tower and there's a current piece -> try place piece
        shape = self.pieces[self.current_piece_key]
        rotated = rotate_piece(shape, self.rotation)
        if can_place_piece(self.grid, gx, gy, rotated, self.start, self.goal, algorithm=self.pathfinding_algorithm):
            cells = get_absolute_cells(gx, gy, rotated)
            set_cells(self.grid, cells, self.current_piece_key)
            if self.deck:
                self.deck.pop(0)
            self.select_new_piece()
            self.deck_count = len(self.deck)
            recompute_enemy_paths(self.enemies, self.grid, self.goal, self.pathfinding_algorithm)

    def place_tower(self, gx, gy):
        """Attempts to place the selected tower at a grid location."""
        if can_place_tower(self.grid, gx, gy, self.towers):
            tower = create_tower(self.selected_tower_id, gx, gy)
            if self.player.gold < tower.cost:
                return # Not enough gold
            self.player.gold -= tower.cost
            self.towers.append(tower)
            recompute_enemy_paths(self.enemies, self.grid, self.goal, self.pathfinding_algorithm)

    def _handle_sidebar_click(self, mx, my):
        """Handles clicks on the sidebar UI. Returns True if a sidebar element was
        clicked, False otherwise."""
        clicked_element = sidebar_click_test(self.game.screen, mx, my)
        # added algo button
        if clicked_element == "algo_button":
            self.algo_index = (self.algo_index + 1) % len(self.algorithms)
            self.pathfinding_algorithm = self.algorithms[self.algo_index]
            recompute_enemy_paths(self.enemies, self.grid, self.goal, self.pathfinding_algorithm)
            return True
        elif clicked_element == "sell_button" and self.clicked_tower: # sell before deselect
            refund = int(self.clicked_tower.cost * 0.5)
            self.player.gold += refund
            self.towers.remove(self.clicked_tower)
            self.clicked_tower = None
            return True
        elif clicked_element == "start_wave":
            if not self.wave_spawned and self.current_wave_index < len(self.level.waves):
                self.spawn_wave()
                self.wave_spawned = True
                self.phase = Phase.Running
            return True
        elif clicked_element == "tower_list":
            clicked_type = tower_list_click_test(self.game.screen, mx, my)
            if clicked_type is not None:
                self.selected_tower_type = clicked_type
                self.selected_tower_id = self.tower_types[clicked_type]
            return True
        elif clicked_element == "sidebar_tower_panel":
            self.clicked_tower = None
            return True
        return False
    
    def select_cell_in_grid(self, mx, my):
        """Handles a click on the main grid for placement or selection."""
        if self.phase not in [Phase.Prepare, Phase.Running, Phase.Victory]:
            return
        gx, gy = self.screen_to_grid(mx, my)
        outside_grid = gx is None or gy is None
        if outside_grid:
            return
        if self.placement_mode == "tower":
            self.place_tower(gx, gy)
            recompute_enemy_paths(self.enemies, self.grid, self.goal)
        elif self.placement_mode == "piece" and self.current_piece_key:
            self.place_piece(gx, gy)
            recompute_enemy_paths(self.enemies, self.grid, self.goal)
        else: # neutral mode
            self.select_existing_tower(gx, gy)

    def select_existing_tower(self, gx, gy):
        """Selects a tower at a grid location to show its stats."""
        self.clicked_tower = None
        for tower in self.towers:
            if tower.x == gx and tower.y == gy:
                self.clicked_tower = tower
                break
        self.hover_tower = self.clicked_tower

    # ===================
    # Camera & Coordinates
    # ===================
    def screen_to_grid(self, sx, sy):
        """Map screen pixel to grid coordinate, taking camera into account."""
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
        """Maps grid coordinate to screen pixel center, taking camera into account."""
        cs = int(self.camera.cell_size * self.camera.zoom)
        sx = gx * cs + cs//2 + self.camera.offset_x
        sy = gy * cs + cs//2 + self.camera.offset_y
        return sx, sy

    def start_panning(self, mx, my):
        """Begins a camera pan operation."""
        self.is_panning = True
        self._pan_start = (mx, my)
        self._cam_start = (self.camera.offset_x, self.camera.offset_y)

    def update_panning(self, e):
        """Updates camera position during a pan."""
        if not self.is_panning:
            return
        mx, my = e.pos
        dx = mx - self._pan_start[0]
        dy = my - self._pan_start[1]
        self.camera.offset_x = self._cam_start[0] + dx
        self.camera.offset_y = self._cam_start[1] + dy

    def stop_panning(self):
        """Stops a camera pan operation."""
        self.is_panning = False

    def zoomimg(self, e):
        """Zooms the camera in or out."""
        if e.y > 0:
            self.camera.zoom = min(2.5, self.camera.zoom + 0.1)
        else:
            self.camera.zoom = max(0.6, self.camera.zoom - 0.1)

    # ===================
    # Misc Helper
    # ===================
    def spawn_wave(self):
        """Initializes the spawning sequence for the current wave."""
        wave = self.level.waves[self.current_wave_index]
        self.spawn_queue.clear()
        self.time_elapsed = 0.0
        randRange = 2.5
        for group in wave:
            for i in range(group.count):
                spawn_time = i * group.spawn_interval + random.uniform(-randRange, randRange)
                self.spawn_queue.append((group.name, self.time_elapsed + spawn_time))

    def show_tower_range(self, e):
        """Sets the tower to be hovered for displaying its range."""
        mx, my = e.pos
        gx, gy = self.screen_to_grid(mx, my)
        self.hover_tower = None
        if gx is not None:
            for t in self.towers:
                if t.x == gx and t.y == gy:
                    self.hover_tower = t
                    break

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
    GameOver = 4