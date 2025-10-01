import sys, pygame, random, json, os
from grid import cell_center, create_grid, set_cells, OBSTACLE, TOWER
from piece import get_piece_shapes, rotate_piece, can_place_piece, get_absolute_cells
from astar import astar
from enemy import update_enemies, spawn_wave, recompute_enemy_paths
from tower import Tower, can_place_tower, place_tower, update_towers
from render.render_fight import draw_zoomed_map, draw_tower_preview, draw_piece_preview, tower_list_click_test, sidebar_click_test, draw_projectiles, draw_sidebar, draw_tower_range

with open(os.path.join("data", "waves.json")) as f:
    _WAVES = json.load(f)["waves"]

class FightScene:
    def __init__(self, game, run_state):
        self.game = game
        self.run_state = run_state

        self.grid = create_grid(30, 20)
        self.gw = len(self.grid[0])
        self.gh = len(self.grid)

        self.start = (0, self.gh // 2)
        self.goal = (self.gw // 2, self.gh // 2)
        
        self.enemies = []
        self.towers = []
        self.projectiles = []

        # camera
        self.camera = {
            "offset_x": 0,
            "offset_y": 0,
            "zoom": 1.0,
            "cell_size": 36
        }

        # pieces / deck: 20 pieces randomly selected from available shapes
        self.pieces = get_piece_shapes()
        self.piece_keys = list(self.pieces.keys())
        # deck is a list of piece keys
        self.deck = [random.choice(self.piece_keys) for _ in range(20)]
        self.current_piece_key = None
        self._select_new_piece()
        self.rotation = 0        
        self.placement_mode = "neutral" # "neutral", "piece", "tower"

        # tower selection: 0,1,2
        self.selected_tower_type = 0  # 0/1/2 for 3 towers
        self.clicked_tower = None     # tower object clicked for stats panel
        self.hover_tower = None       # tower object currently hovered (for range display)
        
        self.waves = _WAVES
        self.current_wave_index = 0
        self.wave_spawned = False

        # put wave info into run_state so HUD can read it
        self.run_state["wave_total"] = len(self.waves)
        self.run_state["wave_index"] = self.current_wave_index
        self.run_state["phase"] = "prep"
        self.run_state["deck_count"] = len(self.deck)
        self.phase = "prep"  # "prep", "running", "victory"

        # input helpers
        self._panning = False
        self._pan_start = (0,0)
        self._cam_start = (0,0)

    def _select_new_piece(self):
        self.current_piece_key = self.deck[0] if self.deck else None
    
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
        if 0 <= gx < self.gw and 0 <= gy < self.gh:
            return gx, gy
        return (None, None)

    def grid_to_screen(self, gx, gy):
        cs = int(self.camera["cell_size"] * self.camera["zoom"])
        sx = gx * cs + cs//2 + self.camera["offset_x"]
        sy = gy * cs + cs//2 + self.camera["offset_y"]
        return sx, sy
    
    def handle_input(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:   # counterclockwise rotation
                    self.rotation = (self.rotation - 1) % 4
                elif e.key == pygame.K_e: # clockwise rotation
                    self.rotation = (self.rotation + 1) % 4
                elif e.key == pygame.K_p: # piece placement
                    if self.placement_mode == "piece":
                        self.placement_mode = "neutral"
                    else:
                        self.placement_mode = "piece"
                elif e.key == pygame.K_t: # tower placement
                    if self.placement_mode == "tower":
                        self.placement_mode = "neutral"
                    else:
                        self.placement_mode = "tower"
                elif e.key == pygame.K_1: # tower hotkeys
                    self.selected_tower_type = 0
                elif e.key == pygame.K_2:
                    self.selected_tower_type = 1
                elif e.key == pygame.K_3:
                    self.selected_tower_type = 2
                elif e.key == pygame.K_EQUALS or e.key == pygame.K_PLUS:
                    self.camera["zoom"] = min(2.5, self.camera["zoom"] + 0.1)
                elif e.key == pygame.K_MINUS:
                    self.camera["zoom"] = max(0.6, self.camera["zoom"] - 0.1)
                elif e.key == pygame.K_ESCAPE:
                    from scenes.scene_map import MapScene
                    self.game.change_scene(MapScene(self.game, self.run_state))

            elif e.type == pygame.MOUSEWHEEL:
                if e.y > 0:
                    self.camera["zoom"] = min(2.5, self.camera["zoom"] + 0.1)
                else:
                    self.camera["zoom"] = max(0.6, self.camera["zoom"] - 0.1)

            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx,my = pygame.mouse.get_pos()

                # Ignore wheel as button 4/5 (bugfix attempt)
                if e.button in (4, 5):
                    continue

                # right click start panning
                if e.button == 3:
                    self._panning = True
                    self._pan_start = (mx,my)
                    self._cam_start = (self.camera["offset_x"], self.camera["offset_y"])
                    continue

                # left click: check sidebar Start Wave button
                sw_clicked = sidebar_click_test(self.game.screen, mx, my)
                if sw_clicked == "start_wave":
                    if not self.wave_spawned and self.current_wave_index < len(self.waves):
                        cfg = self.waves[self.current_wave_index]["sequence"]
                        new_en = spawn_wave([self.start], self.goal, cfg)
                        for en in new_en:
                            en.set_path(astar(self.grid, en.pos, self.goal))
                            self.enemies.append(en)
                        self.wave_spawned = True
                        self.phase = "running"
                        self.run_state["phase"] = "running"
                    continue

                elif sw_clicked == "tower_list":
                    # renderer can return which tower type region was clicked; we ask for a type id
                    clicked_type = tower_list_click_test(self.game.screen, mx, my)
                    if clicked_type is not None:
                        self.selected_tower_type = clicked_type
                    continue

                elif sw_clicked == "sidebar_tower_panel":
                    # clicking the tower-stats section will deselect the tower
                    self.clicked_tower = None
                    continue

                elif sw_clicked == "sell_button" and self.clicked_tower:
                    # sell tower
                    refund = int(self.clicked_tower.cost * 0.5)
                    self.run_state["gold"] += refund
                    self.grid[self.clicked_tower.y][self.clicked_tower.x] = OBSTACLE
                    if self.clicked_tower in self.towers:
                        self.towers.remove(self.clicked_tower)
                    self.clicked_tower = None
                    continue

                # otherwise clicking map area: place piece or tower, or select existing tower
                gx, gy = self.screen_to_grid(mx, my)
                if gx is None:
                    # click outside grid area (maybe in sidebar) — test for clicking tower list etc done above
                    continue

                # Place piece if in piece mode
                if self.placement_mode == "piece" and self.current_piece_key is not None:
                    shape = self.pieces[self.current_piece_key]
                    rotated = rotate_piece(shape, self.rotation)
                    if can_place_piece(self.grid, gx, gy, rotated, self.start, self.goal):
                        cells = get_absolute_cells(gx, gy, rotated)
                        set_cells(self.grid, cells, OBSTACLE)
                        if self.deck:
                            self.deck.pop(0)
                        self._select_new_piece()
                        self.run_state["deck_count"] = len(self.deck)
                        recompute_enemy_paths(self.enemies, self.grid, self.goal)
                    continue

                # Place tower if in tower mode
                if self.placement_mode == "tower":
                    tid = ["bolt", "swift", "cannon"][self.selected_tower_type]
                    from tower import tower_data
                    if self.run_state["gold"] >= tower_data()[tid]["cost"]:
                        if can_place_tower(self.grid, gx, gy):
                            t = place_tower(self.grid, gx, gy, self.towers, tower_id=tid)
                            self.run_state["gold"] -= t.cost
                            recompute_enemy_paths(self.enemies, self.grid, self.goal)
                    continue

                # otherwise, click selects an existing tower if present; find tower at clicked cell
                clicked = None
                for t in self.towers:
                    if t.x == gx and t.y == gy:
                        clicked = t
                        break
                self.clicked_tower = clicked
                # also update hover state to the clicked tower for immediate range display
                self.hover_tower = clicked
                continue

            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 3:
                    self._panning = False

            elif e.type == pygame.MOUSEMOTION:
                if self._panning:
                    mx,my = e.pos
                    dx = mx - self._pan_start[0]
                    dy = my - self._pan_start[1]
                    self.camera["offset_x"] = self._cam_start[0] + dx
                    self.camera["offset_y"] = self._cam_start[1] + dy
                # update hover_tower to show range when mouse over a tower
                mx,my = e.pos
                gx, gy = self.screen_to_grid(mx, my)
                self.hover_tower = None
                if gx is not None:
                    for t in self.towers:
                        if t.x == gx and t.y == gy:
                            self.hover_tower = t
                            break

    def update(self, dt):
        if self.run_state["core_hp"] <= 0:
            from scenes.scene_menu import MenuScene
            self.game.change_scene(MenuScene(self.game))
            return
        
        # update enemies movement
        reached = update_enemies(self.enemies, dt, self.goal)
        for e in reached:
            self.run_state["core_hp"] -= 1
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
                self.run_state["gold"] += e.gold
                if e in self.enemies:
                    self.enemies.remove(e)

        # check wave completion
        if self.wave_spawned and not self.enemies and not any(not p.dead for p in self.projectiles):
            # wave was spawned and there are no enemies and no in-flight projectiles
            self.wave_spawned = False
            self.current_wave_index += 1
            self.run_state["wave_index"] = self.current_wave_index
            if self.current_wave_index >= len(self.waves):
                self.phase = "victory"
                self.run_state["phase"] = "victory"
            else:
                self.phase = "prep"
                self.run_state["phase"] = "prep"

    def render(self, screen):
        screen.fill((18, 18, 18))

        # Step 1: compute preview path/validity
        preview_path = astar(self.grid, self.start, self.goal)  # default: current path
        preview_valid = True

        mx, my = pygame.mouse.get_pos()
        mouse_gx, mouse_gy = self.screen_to_grid(mx, my)
        if mouse_gx is not None and self.placement_mode == "piece" and self.current_piece_key is not None:
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
            else:
                preview_valid = False

        # Step 2: draw map with path
        draw_zoomed_map(screen, self.grid, self.camera,
            enemies=self.enemies, towers=self.towers,
            projectiles=self.projectiles,
            draw_path=preview_path, path_valid=preview_valid
        )

        # Step 3: draw core icon
        cs = int(self.camera["cell_size"] * self.camera["zoom"])
        goal_gx, goal_gy = self.goal
        cx, cy = cell_center(goal_gx, goal_gy, cs)
        sx = cx + self.camera["offset_x"]
        sy = cy + self.camera["offset_y"]
        pygame.draw.circle(screen, (180, 60, 60), (int(sx), int(sy)), max(6, cs//4))
        font = pygame.font.SysFont("arial", 16, bold=True)
        txt = font.render(str(self.run_state.get("core_hp", 0)), True, (255,255,255))
        screen.blit(txt, (int(sx - txt.get_width()//2), int(sy - txt.get_height()//2)))

        # Step 4: draw preview overlays
        if mouse_gx is not None:
            if self.placement_mode == "tower":
                valid = can_place_tower(self.grid, mouse_gx, mouse_gy)
                draw_tower_preview(screen, mouse_gx, mouse_gy, self.selected_tower_type,
                                   cell_size=self.camera["cell_size"], valid=valid, camera=self.camera)
                if valid:
                    tid = ["bolt", "swift", "cannon"][self.selected_tower_type]
                    tmp_t = Tower(mouse_gx, mouse_gy, tower_id=tid)
                    draw_tower_range(screen, tmp_t, cell_size=self.camera["cell_size"],
                                     camera=self.camera, color=(255, 255, 255, 80))
            elif self.current_piece_key is not None:
                shape = self.pieces[self.current_piece_key]
                rotated = rotate_piece(shape, self.rotation)
                valid = can_place_piece(self.grid, mouse_gx, mouse_gy, rotated, self.start, self.goal)
                draw_piece_preview(screen, mouse_gx, mouse_gy, rotated,
                                   cell_size=self.camera["cell_size"],
                                   valid=valid,
                                   camera=self.camera)

        # Step 5: range circles
        if self.hover_tower:
            draw_tower_range(screen, self.hover_tower,
                             cell_size=self.camera["cell_size"],
                             camera=self.camera, color=(255,255,255,90))
        if self.clicked_tower and self.clicked_tower is not self.hover_tower:
            draw_tower_range(screen, self.clicked_tower,
                             cell_size=self.camera["cell_size"],
                             camera=self.camera, color=(255,220,80,110))

        # Step 6: projectiles
        draw_projectiles(screen, self.projectiles,
                         cell_size=self.camera["cell_size"], camera=self.camera)

        # Step 7: sidebar
        self.run_state["wave_index"] = self.current_wave_index
        self.run_state["wave_total"] = len(self.waves)
        self.run_state["phase"] = self.phase
        self.run_state["deck_count"] = len(self.deck)
        self.run_state["selected_tower_type"] = self.selected_tower_type

        draw_sidebar(screen, self.run_state, selected_tower=self.clicked_tower)

        # Step 8: flip
        pygame.display.flip()