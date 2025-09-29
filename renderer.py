import pygame, time
from grid import EMPTY, OBSTACLE, TOWER, cell_center

# SEPARATE LATER INTO A FOLDER LIKE scene/

def cell_rect(x, y, cell_size):
    """Returns the rect tuple for a cell at (x, y)."""
    return (x * cell_size, y * cell_size, cell_size, cell_size)

def draw_grid(surf, grid, cell_size):
    """Draws the grid cells (empty, obstacle, tower) on the surface using given cell_size."""
    colors = {
        EMPTY: (50, 50, 50),
        OBSTACLE: (100, 100, 200),
        TOWER: (200, 100, 100)
    }
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            pygame.draw.rect(surf, colors.get(val, (60,60,60)), cell_rect(x, y, cell_size))
            pygame.draw.rect(surf, (80, 80, 80), cell_rect(x, y, cell_size), 1)
    
def draw_piece_preview(surf, gx, gy, cells, cell_size, valid):
    """Draws a ghost/preview version of a piece at mouse position with color based on validity."""
    color = (0, 255, 0) if valid else (255, 0, 0)
    for x, y in cells:
        pygame.draw.rect(surf, color, ((gx + x) * cell_size, (gy + y) * cell_size, cell_size, cell_size), 2)
    
def draw_enemies(surf, enemies, cell_size):
    """Draw enemies as circles or sprites on the grid."""
    for e in enemies:
        if not e.path and not e.pos:
            continue
        # use path[0] as rendering anchor if exists, else pos
        anchor = e.path[0] if e.path else e.pos
        px, py = cell_center(anchor[0], anchor[1], cell_size)
        radius = max(4, cell_size // 3)
        if getattr(e, "etype", "basic") == "fast":
            color = (255, 160, 40)  # orange
            pygame.draw.circle(surf, color, (px, py), radius)
            # little tail for fast
            pygame.draw.circle(surf, (255,220,140), (px, py), max(2, radius//2))
        elif getattr(e, "etype", "basic") == "tank":
            color = (160, 50, 200)  # purple
            pygame.draw.rect(surf, color, (px - radius, py - radius, radius*2, radius*2))
        else:
            color = (255, 200, 50)
            pygame.draw.circle(surf, color, (px, py), radius)

def draw_towers(surf, towers, cell_size):
    """Draw towers at their locations with different visuals by tower_type."""
    for t in towers:
        x, y = t.x, t.y
        rect = cell_rect(x, y, cell_size)
        cx = rect[0] + rect[2] // 2
        cy = rect[1] + rect[3] // 2
        # visuals by type
        if getattr(t, "tower_type", 0) == 0:
            pygame.draw.rect(surf, (220, 40, 40), rect)
            pygame.draw.circle(surf, (255,200,200), (cx, cy), cell_size//6)
        elif t.tower_type == 1:
            pygame.draw.rect(surf, (40, 180, 40), rect)
            pygame.draw.line(surf, (255,255,255), (rect[0]+4, rect[1]+4), (rect[0]+rect[2]-4, rect[1]+rect[3]-4), 3)
        elif t.tower_type == 2:
            pygame.draw.rect(surf, (40,120,220), rect)
            pygame.draw.circle(surf, (255,255,255), (cx, cy), cell_size//4, 2)
    
def draw_dashed_path(surf, path, cell_size, dash_len=8, gap_len=6):
    """Draws a dashed line along the enemy's A* path."""
    if len(path) < 2:
        return
    pts = [cell_center(x, y, cell_size) for x, y in path]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist == 0:
            continue
        nx, ny = dx / dist, dy / dist
        seg = 0
        while seg < dist:
            start = (x1 + nx * seg, y1 + ny * seg)
            end = (x1 + nx * min(seg + dash_len, dist), y1 + ny * min(seg + dash_len, dist))
            pygame.draw.line(surf, (255, 255, 0), start, end, 2)
            seg += dash_len + gap_len

def make_rainbow_surface(size):
    """Create a horizontal rainbow gradient surface, rotated diagonally"""
    w, h = size
    rainbow = pygame.Surface((w * 2, h * 2))
    for x in range(rainbow.get_width()):
        # Use half the width for the hue calculation to create one full 360-degree cycle
        hue = (x / (rainbow.get_width() / 2)) * 360 % 360
        color = pygame.Color(0)
        color.hsva = (hue, 70, 100, 100)  # 70 saturation = soft rainbow
        pygame.draw.line(rainbow, color, (x, 0), (x, rainbow.get_height()))
    return rainbow

_rainbow_cache = None

def draw_grid_background(surf, cell_size=64):
    """Draws a subtle gray grid background."""
    w, h = surf.get_size()
    base_color = (40, 40, 40)
    grid_color = (60, 60, 60)
    surf.fill(base_color)
    for x in range(0, w, cell_size):
        pygame.draw.line(surf, grid_color, (x, 0), (x, h))
    for y in range(0, h, cell_size):
        pygame.draw.line(surf, grid_color, (0, y), (w, y))

def draw_menu(surf, buttons):
    """Draws start menu with subtle diagonal rainbow overlay and interactive buttons."""
    global _rainbow_cache
    w, h = surf.get_size()
    t = time.time() * 40  # movement speed

    # gray bg
    draw_grid_background(surf, cell_size=64)

    # rainbow overlay
    if _rainbow_cache is None:
        _rainbow_cache = make_rainbow_surface((w, h))

    rw, rh = _rainbow_cache.get_size()
    offset_x = int(t) % rw
    offset_y = int(t * 0.5) % rh # Slower vertical scroll for a diagonal effect

    diag = int((w**2 + h**2)**0.5)
    temp_surf = pygame.Surface((diag, diag), pygame.SRCALPHA)
    
    # Tile the rainbow onto this larger temporary surface
    for x in range(-rw, w, rw):
        for y in range(-rh, h, rh):
            temp_surf.blit(_rainbow_cache, (x + offset_x, y + offset_y))

    rotated_rainbow = pygame.transform.rotate(temp_surf, -45)
    rotated_rainbow.set_alpha(70)
    surf.blit(rotated_rainbow, rotated_rainbow.get_rect(center=(w // 2, h // 2)))

    # title
    font_title = pygame.font.SysFont("arial", 72, bold=True)
    title_surf = font_title.render("Emberward Clone", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(w // 2, h // 4))
    surf.blit(title_surf, title_rect)

    # buttons
    font_btn = pygame.font.SysFont("arial", 42, bold=True)
    mx, my = pygame.mouse.get_pos()
    btn_w, btn_h = 300, 70
    start_y = h // 2
    spacing = 100

    for i, b in enumerate(buttons):
        rect = pygame.Rect(0, 0, btn_w, btn_h)
        rect.center = (w // 2, start_y + i * spacing)

        hovered = rect.collidepoint(mx, my)
        color = (200, 200, 200) if hovered else (160, 160, 160)
        border = (255, 255, 255) if hovered else (60, 60, 60)

        if hovered:
            rect.inflate_ip(10, 10)

        pygame.draw.rect(surf, color, rect, border_radius=12)
        pygame.draw.rect(surf, border, rect, 4, border_radius=12)

        txt = font_btn.render(b["text"], True, (0, 0, 0))
        txt_rect = txt.get_rect(center=rect.center)
        surf.blit(txt, txt_rect)

def draw_map_screen(surf, run_state):
    """Draws roguelite map nodes, connections, and player progress (simple single-node)."""
    w, h = surf.get_size()
    draw_grid_background(surf, 48)
    # single big node in center
    cx, cy = w // 2, h // 2
    node_r = 48
    pygame.draw.circle(surf, (100, 160, 240), (cx, cy), node_r)
    pygame.draw.circle(surf, (220, 220, 220), (cx, cy), node_r, 4)
    font = pygame.font.SysFont("arial", 22, bold=True)
    name = run_state.get("nodes", [{}])[0].get("name", "Node")
    txt = font.render(name, True, (255,255,255))
    txt_r = txt.get_rect(center=(cx, cy))
    surf.blit(txt, txt_r)
    # small instruction
    f2 = pygame.font.SysFont("arial", 16)
    hint = f2.render("Click the node to start the run", True, (200,200,200))
    surf.blit(hint, (cx - hint.get_width()//2, cy + node_r + 10))

def draw_info_bars(surf, run_state):
    """Draws sidebars with core HP, gold, wave info, etc."""
    w, h = surf.get_size()
    sidebar_w = 260
    rect = pygame.Rect(w - sidebar_w, 0, sidebar_w, h)
    pygame.draw.rect(surf, (26, 26, 26), rect)
    pygame.draw.rect(surf, (60, 60, 60), rect.inflate(-10, -10), 2)

    padding = 16
    x = w - sidebar_w + padding
    y = padding
    f = pygame.font.SysFont("arial", 20, bold=True)

    # Core HP
    core_hp = run_state.get("core_hp", 0)
    txt = f.render(f"Core HP: {core_hp}", True, (255, 255, 255))
    surf.blit(txt, (x, y))
    y += 36

    # Gold
    gold = run_state.get("gold", 0)
    txt = f.render(f"Gold: {gold}", True, (255, 255, 255))
    surf.blit(txt, (x, y))
    y += 36

    # Wave info
    idx = run_state.get("wave_index", 0)
    total = run_state.get("wave_total", 0)
    phase = run_state.get("phase", "map")
    txt = f.render(f"Wave: {idx}/{total}", True, (255, 255, 255))
    surf.blit(txt, (x, y))
    y += 36

    # Separator
    pygame.draw.line(surf, (70,70,70), (x, y), (w - padding, y), 1)
    y += 12

    # Tower list
    txt = f.render("Towers (1/2/3):", True, (200, 200, 200))
    surf.blit(txt, (x, y))
    y += 28

    # tower icons
    # type 0
    pygame.draw.rect(surf, (220, 40, 40), (x, y, 40, 40))
    surf.blit(pygame.font.SysFont("arial", 14).render("Basic", True, (0,0,0)), (x+46, y+12))
    y += 54
    pygame.draw.rect(surf, (40, 180, 40), (x, y, 40, 40))
    surf.blit(pygame.font.SysFont("arial", 14).render("Fast", True, (0,0,0)), (x+46, y+12))
    y += 54
    pygame.draw.rect(surf, (40,120,220), (x, y, 40, 40))
    surf.blit(pygame.font.SysFont("arial", 14).render("Heavy", True, (0,0,0)), (x+46, y+12))
    y += 54

    # Deck info (if present)
    deck = run_state.get("deck_count", None)
    if deck is not None:
        txt = f.render(f"Deck: {deck} pieces", True, (255,255,255))
        surf.blit(txt, (x, y))
        y += 36

    # Start wave button
    btn_rect = pygame.Rect(w - sidebar_w + 20, h - 80, sidebar_w - 40, 48)
    pygame.draw.rect(surf, (100, 180, 100), btn_rect, border_radius=8)
    txt = pygame.font.SysFont("arial", 20, bold=True).render("Start Wave", True, (10,10,10))
    surf.blit(txt, (btn_rect.centerx - txt.get_width()//2, btn_rect.centery - txt.get_height()//2))

def draw_zoomed_map(surf, grid, camera, enemies=None, towers=None, draw_path=None):
    """
    Draws the grid + enemies + towers into a temporary surface using scaled cell_size,
    and blits it to `surf` at camera offsets.
    camera = {"offset_x":..., "offset_y":..., "zoom":..., "cell_size": base_cell_size}
    """
    base = camera.get("cell_size", 32)
    zoom = camera.get("zoom", 1.0)
    cell_size = max(4, int(base * zoom))
    gw = len(grid[0])
    gh = len(grid)
    surf_w = gw * cell_size
    surf_h = gh * cell_size
    temp = pygame.Surface((surf_w, surf_h))
    # draw grid, enemies, towers on temp using scaled cell_size
    draw_grid(temp, grid, cell_size)
    if draw_path and len(draw_path) > 1:
        draw_dashed_path(temp, draw_path, cell_size)
    if enemies:
        draw_enemies(temp, enemies, cell_size)
    if towers:
        draw_towers(temp, towers, cell_size)

    # blit temp at camera offset onto surf
    surf.blit(temp, (camera.get("offset_x", 0), camera.get("offset_y", 0)))