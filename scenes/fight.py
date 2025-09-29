import sys, pygame, random
from grid import cell_center, create_grid, set_cells, OBSTACLE, TOWER
from piece import get_piece_shapes, rotate_piece, can_place_piece, get_absolute_cells
from astar import astar
from enemy import Enemy, update_enemies, spawn_wave, recompute_enemy_paths
from tower import can_place_tower, place_tower, update_towers
from renderer import draw_grid, draw_piece_preview, draw_enemies, draw_towers, draw_dashed_path, draw_zoomed_map, draw_info_bars
from run_state import create_run_state

class FightScene:
    def __init__(self, game, run_state):
        self.game = game
        self.run_state = run_state

        # grid and start/goal
        self.grid = create_grid(30, 20)
        # choose the center of the map as core/goal
        gw, gh = len(self.grid[0]), len(self.grid)
        self.start = (0, gh // 2)
        self.goal = (gw // 2, gh // 2)

        self.enemies = []
        self.towers = []

        # camera
        self.camera = {
            "offset_x": 0,
            "offset_y": 0,
            "zoom": 1.0,
            "cell_size": 32
        }

        # pieces / deck: 10 pieces randomly selected from available shapes
        self.pieces = get_piece_shapes()
        self.piece_keys = list(self.pieces.keys())
        # deck is a list of piece keys
        self.deck = [random.choice(self.piece_keys) for _ in range(10)]
        self.current_piece_key = None
        self._select_new_piece()
        self.rotation = 0
        self.placing_tower = False

        # tower selection: 0,1,2
        self.selected_tower_type = 0

        # waves: 3 waves, with at least two enemy types
        self.waves = [
            # wave 1: light fast enemies
            [{"hp": 50, "speed": 5, "gold": 3, "etype": "fast"} for _ in range(8)],
            # wave 2: basic + 1 tank
            [{"hp": 100, "speed": 3, "gold": 6, "etype": "basic"} for _ in range(6)] +
            [{"hp": 250, "speed": 1, "gold": 20, "etype": "tank"} for _ in range(2)],
            # wave 3: mixed heavier set
            [{"hp": 80, "speed": 5, "gold": 4, "etype": "fast"} for _ in range(6)] +
            [{"hp": 200, "speed": 2, "gold": 12, "etype": "tank"} for _ in range(4)]
        ]
        self.current_wave_index = 0
        self.wave_spawned = False

        # put wave info into run_state so HUD can read it
        self.run_state["wave_total"] = len(self.waves)
        self.run_state["wave_index"] = self.current_wave_index
        self.run_state["phase"] = "prep"
        self.run_state["deck_count"] = len(self.deck)

        self.phase = "prep"  # "prep", "running", "victory"

    def _select_new_piece(self):
        if self.deck:
            self.current_piece_key = self.deck[0]
        else:
            self.current_piece_key = None

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
                elif event.key == pygame.K_1:
                    self.selected_tower_type = 0
                elif event.key == pygame.K_2:
                    self.selected_tower_type = 1
                elif event.key == pygame.K_3:
                    self.selected_tower_type = 2
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.camera["zoom"] = min(2.5, self.camera["zoom"] + 0.1)
                elif event.key == pygame.K_MINUS:
                    self.camera["zoom"] = max(0.5, self.camera["zoom"] - 0.1)
                elif event.key == pygame.K_ESCAPE:
                    # return to map
                    from map import MapScene
                    self.game.change_scene(MapScene(self.game, self.run_state))
            elif event.type == pygame.MOUSEWHEEL:
                # zoom around mouse
                if event.y > 0:
                    self.camera["zoom"] = min(2.5, self.camera["zoom"] + 0.1)
                elif event.y < 0:
                    self.camera["zoom"] = max(0.5, self.camera["zoom"] - 0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # right-click drag begin
                if event.button == 3:
                    self._panning = True
                    self._pan_start = (mx, my)
                    self._cam_start = (self.camera["offset_x"], self.camera["offset_y"])
                elif event.button == 1:
                    # check if clicking the Start Wave button on the right sidebar
                    w, h = self.game.screen.get_size()
                    sidebar_w = 260
                    btn_rect = pygame.Rect(w - sidebar_w + 20, h - 80, sidebar_w - 40, 48)
                    if btn_rect.collidepoint(mx, my):
                        # start next wave if available
                        if self.current_wave_index < len(self.waves) and not self.wave_spawned:
                            cfg = self.waves[self.current_wave_index]
                            new_en = spawn_wave([self.start], self.goal, cfg)
                            # compute initial path for each enemy
                            for e in new_en:
                                e.set_path(astar(self.grid, e.pos, self.goal))
                                self.enemies.append(e)
                            self.wave_spawned = True
                            self.phase = "running"
                            self.run_state["phase"] = "running"
                        continue

                    # one-click: either place tower or place piece
                    gwx, gwy = self.screen_to_grid(mx, my)
                    if gwx is None:
                        continue
                    gx, gy = gwx, gwy
                    if self.placing_tower:
                        if can_place_tower(self.grid, gx, gy):
                            place_tower(self.grid, gx, gy, self.towers, tower_type=self.selected_tower_type)
                            # recompute all paths for enemies
                            recompute_enemy_paths(self.enemies, self.grid, self.goal)
                    else:
                        if self.current_piece_key is None:
                            # no piece left
                            continue
                        current_shape = self.pieces[self.current_piece_key]
                        rotated = rotate_piece(current_shape, self.rotation)
                        if can_place_piece(self.grid, gx, gy, rotated, self.start, self.goal):
                            cells = get_absolute_cells(gx, gy, rotated)
                            set_cells(self.grid, cells, OBSTACLE)
                            # consume piece from deck
                            if self.deck:
                                self.deck.pop(0)
                            self._select_new_piece()
                            self.run_state["deck_count"] = len(self.deck)
                            recompute_enemy_paths(self.enemies, self.grid, self.goal)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self._panning = False
            elif event.type == pygame.MOUSEMOTION:
                if getattr(self, "_panning", False):
                    mx, my = event.pos
                    dx = mx - self._pan_start[0]
                    dy = my - self._pan_start[1]
                    self.camera["offset_x"] = self._cam_start[0] + dx
                    self.camera["offset_y"] = self._cam_start[1] + dy

    def screen_to_grid(self, sx, sy):
        """Map screen pixel to grid coordinate, taking camera into account.
           returns (gx, gy) or (None, None) if outside grid area.
        """
        cs = int(self.camera["cell_size"] * self.camera["zoom"])
        wx = sx - self.camera["offset_x"]
        wy = sy - self.camera["offset_y"]
        if wx < 0 or wy < 0:
            return (None, None)
        gx = int(wx // cs)
        gy = int(wy // cs)
        if 0 <= gy < len(self.grid) and 0 <= gx < len(self.grid[0]):
            return gx, gy
        return (None, None)

    def update(self, dt):
        # update enemies movement
        reached = update_enemies(self.enemies, dt, self.goal)
        for e in reached:
            # lose core HP
            self.run_state["core_hp"] -= 1
            if e in self.enemies:
                self.enemies.remove(e)

        # towers attack
        update_towers(self.towers, self.enemies, dt)

        # remove dead enemies, add gold
        for e in list(self.enemies):
            if e.is_dead():
                self.run_state["gold"] += e.gold
                if e in self.enemies:
                    self.enemies.remove(e)

        # check wave completion
        if self.wave_spawned and not self.enemies:
            # this wave was spawned and is now cleared
            self.wave_spawned = False
            self.current_wave_index += 1
            self.run_state["wave_index"] = self.current_wave_index
            if self.current_wave_index >= len(self.waves):
                # all waves cleared -> victory
                self.phase = "victory"
                self.run_state["phase"] = "victory"
            else:
                self.phase = "prep"
                self.run_state["phase"] = "prep"

    def render(self, screen):
        screen.fill((30, 30, 30))

        # left: zoomed map (we keep it anchored at 0,0 and camera offset controls pan)
        draw_zoomed_map(screen, self.grid, self.camera, enemies=self.enemies, towers=self.towers, draw_path=(self.enemies[0].path if self.enemies else None))

        # draw core icon at goal cell (center)
        cs = int(self.camera["cell_size"] * self.camera["zoom"])
        gx, gy = self.goal
        cx, cy = cell_center(gx, gy, cs)
        # transform world pos by camera offset for on-screen coords
        screen_x = cx + self.camera["offset_x"]
        screen_y = cy + self.camera["offset_y"]
        pygame.draw.circle(screen, (180, 60, 60), (int(screen_x), int(screen_y)), max(6, cs//4))
        # core HP number
        font = pygame.font.SysFont("arial", 16, bold=True)
        txt = font.render(str(self.run_state.get("core_hp", 0)), True, (255,255,255))
        screen.blit(txt, (int(screen_x - txt.get_width()//2), int(screen_y - txt.get_height()//2)))

        # piece preview (mouse) - show on top of zoomed map
        mx, my = pygame.mouse.get_pos()
        gx, gy = self.screen_to_grid(mx, my)
        if not self.placing_tower and self.current_piece_key is not None and gx is not None:
            current_shape = self.pieces[self.current_piece_key]
            rotated = rotate_piece(current_shape, self.rotation)
            valid = can_place_piece(self.grid, gx, gy, rotated, self.start, self.goal)
            # draw preview - but draw_piece_preview uses cell_size, so create a temp surface and draw at world coords
            # We'll call draw_piece_preview directly on screen but its cell calculations assume top-left at 0, so we need to offset
            # Instead, create a tiny helper to draw with camera transforms:
            for x, y in rotated:
                rx = (gx + x) * cs + self.camera["offset_x"]
                ry = (gy + y) * cs + self.camera["offset_y"]
                color = (0,255,0) if valid else (255,0,0)
                pygame.draw.rect(screen, color, (rx, ry, cs, cs), 2)

        # right: info bars / HUD
        # update run_state keys so renderer can read them
        self.run_state["wave_index"] = self.current_wave_index
        self.run_state["wave_total"] = len(self.waves)
        self.run_state["phase"] = self.phase
        self.run_state["deck_count"] = len(self.deck)
        draw_info_bars(screen, self.run_state)

        # victory overlay
        if self.phase == "victory":
            w, h = screen.get_size()
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0,0,0,150))
            screen.blit(overlay, (0,0))
            font = pygame.font.SysFont("arial", 36, bold=True)
            txt = font.render("Victory! Click to return to map", True, (255,255,255))
            screen.blit(txt, (w//2 - txt.get_width()//2, h//2 - txt.get_height()//2))
            # allow click anywhere to return
            mx, my = pygame.mouse.get_pos()
            for e in pygame.event.get([pygame.MOUSEBUTTONDOWN]):
                if e.type == pygame.MOUSEBUTTONDOWN:
                    from map import MapScene
                    self.game.change_scene(MapScene(self.game, self.run_state))
                    return

        pygame.display.flip()
