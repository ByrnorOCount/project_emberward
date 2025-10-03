import pygame
from constants import *
from tower import tower_data
from piece import PIECE_COLORS
from grid import EMPTY, OBSTACLE, TOWER, FIXED_OBSTACLE, cell_center

# -----------------------------
# Grid & map drawing
# -----------------------------
def cell_rect(x, y, cell_size):
    """Returns the rect tuple for a cell at (x, y)."""
    return (x * cell_size, y * cell_size, cell_size, cell_size)

def draw_grid(surf, grid, cell_size, pieces):
    """Draws the grid cells (empty, obstacle, tower) on the surface using given cell_size."""
    colors = {
        EMPTY: (50, 50, 50),
        FIXED_OBSTACLE: (80, 80, 80)
    }
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if isinstance(val, str): # It's a piece key
                pygame.draw.rect(surf, PIECE_COLORS.get(val, (100,100,200)), cell_rect(x, y, cell_size))
            else:
                pygame.draw.rect(surf, colors.get(val, (60,60,60)), cell_rect(x, y, cell_size))
            pygame.draw.rect(surf, (80, 80, 80), cell_rect(x, y, cell_size), 1)

def draw_zoomed_map(surf, grid, camera, enemies=None, towers=None, projectiles=None, draw_path=None, is_path_valid=True):
    """Draw the fight grid, enemies, towers, projectiles at zoomed scale with camera offset."""
    cs = int(camera.cell_size * camera.zoom)
    gw, gh = len(grid[0]), len(grid)
    temp = pygame.Surface((gw * cs, gh * cs))
    from piece import get_piece_shapes
    draw_grid(temp, grid, cs, get_piece_shapes())

    # path
    if draw_path and len(draw_path) > 1:
        pts = [cell_center(x, y, cs) for x, y in draw_path]
        # Dashed line
        dash_len = 10
        gap_len = 6
        color = (255, 255, 0) if is_path_valid else (255, 60, 60)
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            dx, dy = x2 - x1, y2 - y1
            dist = (dx**2 + dy**2) ** 0.5
            if dist == 0:
                continue
            nx, ny = dx / dist, dy / dist
            seg = 0
            while seg < dist:
                start = (x1 + nx * seg, y1 + ny * seg)
                end = (x1 + nx * min(seg + dash_len, dist), y1 + ny * min(seg + dash_len, dist))
                pygame.draw.line(temp, color, start, end, 2)
                seg += dash_len + gap_len

    # towers - draw these after the grid but before path/enemies
    if towers:
        for tower in towers:
            rx, ry, rw, rh = cell_rect(tower.x, tower.y, cs)
            # shrink tower to ~60% of cell to show piece color underneath
            size = int(cs * 0.6)
            cx = rx + rw // 2
            cy = ry + rh // 2
            rect = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
            pygame.draw.rect(temp, tower.color, rect)
            pygame.draw.rect(temp, (0, 0, 0), rect, 2) # Black border

    # enemies
    if enemies:
        for e in enemies:
            px, py = cell_center(e.pos[0], e.pos[1], cs)
            r = max(4, cs // 3)
            pygame.draw.circle(temp, e.color, (px, py), r)

            # Draw health bar
            if e.hp < e.max_hp:
                bar_width = r * 2
                bar_height = max(2, r // 4)
                bar_x = px - r
                bar_y = py - r - bar_height - 2 # Position above the circle
                health_pct = max(0, e.hp / e.max_hp)
                
                pygame.draw.rect(temp, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(temp, (0, 200, 0), (bar_x, bar_y, bar_width * health_pct, bar_height))

    # projectiles
    if projectiles:
        for p in projectiles:
            px = p.x * cs + cs // 2
            py = p.y * cs + cs // 2
            pygame.draw.circle(temp, (255, 255, 255), (int(px), int(py)), max(2, cs // 8))

    # blit with camera offset
    surf.blit(temp, (camera.offset_x, camera.offset_y))

# -----------------------------
# Tower previews / range / projectiles
# -----------------------------
def draw_tower_preview(surf, gx, gy, tower_id, cell_size, valid, camera):
    """Draws a ghost/preview version of a tower at mouse position with color based on validity."""
    tower_stats = tower_data()[tower_id]
    cs = int(cell_size * camera.zoom)
    cx = gx * cs + cs // 2 + camera.offset_x
    cy = gy * cs + cs // 2 + camera.offset_y
    size = int(cs * 0.7)
    rect = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
    color = (0, 200, 0, 100) if valid else (200, 0, 0, 100)

    preview = pygame.Surface((size, size), pygame.SRCALPHA)
    preview.fill(color)
    surf.blit(preview, rect)

    font = pygame.font.SysFont(DEFAULT_FONT_NAME, 12, bold=True)
    txt = font.render(tower_stats["name"], True, (255, 255, 255))
    surf.blit(txt, (cx - txt.get_width() // 2, rect.top - 12))

def draw_piece_preview(surf, gx, gy, rotated_cells, cell_size, valid, camera):
    """Draws a ghost/preview version of a piece at mouse position with color based on validity."""
    cs = int(cell_size * camera.zoom)
    color = (0, 255, 0) if valid else (255, 0, 0)
    for x, y in rotated_cells:
        rx = (gx + x) * cs + camera.offset_x
        ry = (gy + y) * cs + camera.offset_y
        pygame.draw.rect(surf, color, (rx, ry, cs, cs), 2)

def draw_tower_range(surf, tower, cell_size, camera, color=(255,255,255,80)):
    cs = int(cell_size * camera.zoom)
    radius = int(tower.range * cs)
    cx = tower.x * cs + cs // 2 + camera.offset_x
    cy = tower.y * cs + cs // 2 + camera.offset_y
    overlay = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(overlay, color, (radius, radius), radius)
    surf.blit(overlay, (cx - radius, cy - radius))

def draw_projectiles(surf, projectiles, cell_size, camera):
    cs = int(cell_size * camera.zoom)
    for p in projectiles:
        px = p.x * cs + cs // 2 + camera.offset_x
        py = p.y * cs + cs // 2 + camera.offset_y
        pygame.draw.circle(surf, (255, 255, 255), (int(px), int(py)), max(2, cs // 8))

# -----------------------------
# Sidebar UI
# -----------------------------
_sidebar_rects = {
    "start_wave": None,
    "tower_list": [],
    "tower_panel": None,
    "sell_button": None,
    "algo_button": None,
}

# render/render_fight.py

import pygame
from constants import *
from tower import tower_data
from piece import PIECE_COLORS
from grid import EMPTY, OBSTACLE, TOWER, FIXED_OBSTACLE, cell_center

# ... (all other functions in the file remain the same) ...

# -----------------------------
# Sidebar UI
# -----------------------------
_sidebar_rects = {
    "start_wave": None,
    "tower_list": [],
    "tower_panel": None,
    "sell_button": None,
    "algo_button": None, # Add this for the new button
}

# added algo button
def draw_sidebar(surf, level, player, wave_index, deck_count, is_placing_tower, selected_tower=None, algorithm="astar"):
    w, h = surf.get_size()
    sidebar_w = 260
    rect = pygame.Rect(w - sidebar_w, 0, sidebar_w, h)
    pygame.draw.rect(surf, (26, 26, 26), rect)

    padding = 16
    x = rect.left + padding
    y = padding
    f = pygame.font.SysFont(DEFAULT_FONT_NAME, 20, bold=True)

    # Core / Gold / Wave
    gold = player.gold
    wave_i = wave_index
    wave_t = len(level.waves)
    surf.blit(f.render(f"HP: {player.hp}", True, (255,255,255)), (x, y)); y += 30
    surf.blit(f.render(f"Gold: {gold}", True, (255,220,100)), (x, y)); y += 30
    surf.blit(f.render(f"Wave: {wave_i}/{wave_t}", True, (255,255,255)), (x, y)); y += 40

    # Deck
    surf.blit(f.render(f"Deck left: {deck_count} pieces", True, (255,255,255)), (x, y)); y += 40

    # Towers list
    all_tower_data = tower_data()
    surf.blit(f.render("Towers (1/2/3):", True, (200,200,200)), (x, y)); y += 28
    _sidebar_rects["tower_list"].clear()
    tower_ids = ["bolt", "swift", "cannon"]
    font_tower = pygame.font.SysFont(DEFAULT_FONT_NAME, 16)
    for i, tid in enumerate(tower_ids):
        stats = all_tower_data[tid]
        box = pygame.Rect(x, y, 40, 40)
        pygame.draw.rect(surf, stats["color"], box)

        name_txt = font_tower.render(stats["name"], True, (255,255,255))
        cost_txt = font_tower.render(f"Cost: {stats['cost']}", True, (255, 220, 100))

        surf.blit(name_txt, (x + 50, y + 4))
        surf.blit(cost_txt, (x + 50, y + 22))

        _sidebar_rects["tower_list"].append((i, box.copy()))
        y += 50

    # Tower stats panel
    if selected_tower:
        panel_h = 160
        panel_rect = pygame.Rect(x, y, sidebar_w - 2*padding, panel_h)
        pygame.draw.rect(surf, (40,40,40), panel_rect)
        _sidebar_rects["tower_panel"] = panel_rect.copy()

        stats = selected_tower.get_stats()
        fy = y + 8
        for k, v in stats.items():
            surf.blit(pygame.font.SysFont(DEFAULT_FONT_NAME, 16).render(f"{k}: {v}", True, (255,255,255)), (x+6, fy))
            fy += 20

        refund = int(selected_tower.cost * 0.5)
        sell_rect = pygame.Rect(panel_rect.right-100, panel_rect.bottom-36, 80, 28)
        pygame.draw.rect(surf, (200,80,80), sell_rect, border_radius=6)
        txt = pygame.font.SysFont("arial", 16, bold=True).render(f"Sell ({refund})", True, (0,0,0))
        surf.blit(txt, (sell_rect.centerx - txt.get_width()//2, sell_rect.centery - txt.get_height()//2))
        _sidebar_rects["sell_button"] = sell_rect.copy()
    else:
        _sidebar_rects["sell_button"] = None
        surf.blit(f.render("P: Toggle Piece Mode", True, (2,255,255)), (x, y)); y += 24
        surf.blit(f.render("T: Toggle Tower Mode", True, (2,255,255)), (x, y)); y += 24
        surf.blit(f.render("Q/E: Rotate Piece", True, (2,255,255)), (x, y)); y += 24

    # NEW: Algorithm selection button
    algo_rect = pygame.Rect(x, h - 140, sidebar_w - 2*padding, 30)
    pygame.draw.rect(surf, (100, 100, 180), algo_rect, border_radius=6)
    algo_text = f.render(f"Algo: {algorithm.upper()}", True, (255, 255, 255)) # This now works
    surf.blit(algo_text, (algo_rect.centerx - algo_text.get_width()//2, algo_rect.centery - algo_text.get_height()//2))
    _sidebar_rects["algo_button"] = algo_rect.copy()

    # Start wave button
    btn_rect = pygame.Rect(x, h - 80, sidebar_w - 2*padding, 48)
    pygame.draw.rect(surf, (100,180,100), btn_rect, border_radius=8)
    txt = pygame.font.SysFont(DEFAULT_FONT_NAME, 20, bold=True).render("Start Wave", True, (0,0,0))
    surf.blit(txt, (btn_rect.centerx - txt.get_width()//2, btn_rect.centery - txt.get_height()//2))
    _sidebar_rects["start_wave"] = btn_rect.copy()

# -----------------------------
# Click detection helpers
# -----------------------------
def sidebar_click_test(surf, mx, my):
    """Returns the name of the sidebar element that was clicked."""
    if _sidebar_rects["sell_button"] and _sidebar_rects["sell_button"].collidepoint(mx, my):
        return "sell_button"
    if _sidebar_rects.get("algo_button") and _sidebar_rects["algo_button"].collidepoint(mx, my): # MODIFIED
        return "algo_button"
    if _sidebar_rects["start_wave"] and _sidebar_rects["start_wave"].collidepoint(mx, my):
        return "start_wave"
    if _sidebar_rects["tower_panel"] and _sidebar_rects["tower_panel"].collidepoint(mx, my):
        return "sidebar_tower_panel"
    for idx, rect in _sidebar_rects["tower_list"]:
        if rect.collidepoint(mx, my):
            return "tower_list"
    return None

# ... (rest of the file is the same)
# -----------------------------
# Click detection helpers
# -----------------------------
def sidebar_click_test(surf, mx, my):
    """Returns the name of the sidebar element that was clicked."""
    if _sidebar_rects["sell_button"] and _sidebar_rects["sell_button"].collidepoint(mx, my):
        return "sell_button"
    if _sidebar_rects.get("algo_button") and _sidebar_rects["algo_button"].collidepoint(mx, my):
        return "algo_button"
    if _sidebar_rects["start_wave"] and _sidebar_rects["start_wave"].collidepoint(mx, my):
        return "start_wave"
    if _sidebar_rects["tower_panel"] and _sidebar_rects["tower_panel"].collidepoint(mx, my):
        return "sidebar_tower_panel"
    for idx, rect in _sidebar_rects["tower_list"]:
        if rect.collidepoint(mx, my):
            return "tower_list"
    return None

def tower_list_click_test(surf, mx, my):
    """Returns the index of the tower that was clicked."""
    for idx, rect in _sidebar_rects["tower_list"]:
        if rect.collidepoint(mx, my):
            return idx
    return None