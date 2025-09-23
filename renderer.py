import pygame
from grid import EMPTY, OBSTACLE, TOWER, cell_center

def cell_rect(x, y, cell_size):
    """Returns the rect tuple for a cell at (x, y)."""
    return (x * cell_size, y * cell_size, cell_size, cell_size)

def draw_grid(surf, grid, cell_size):
    """Draws the grid cells (empty, obstacle, tower) on the screen."""
    colors = {
        EMPTY: (50, 50, 50),
        OBSTACLE: (100, 100, 200),
        TOWER: (200, 100, 100)
    }
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            pygame.draw.rect(surf, colors[val], cell_rect(x, y, cell_size))
            pygame.draw.rect(surf, (80, 80, 80), cell_rect(x, y, cell_size), 1)
    
def draw_piece_preview(surf, gx, gy, cells, cell_size, valid):
    """Draws a ghost/preview version of a piece at mouse position with color based on validity."""
    color = (0, 255, 0) if valid else (255, 0, 0)
    for x, y in cells:
        pygame.draw.rect(surf, color, ((gx + x) * cell_size, (gy + y) * cell_size, cell_size, cell_size), 2)
    
def draw_enemies(surf, enemies, cell_size):
    """Draws all enemies as circles or sprites on the grid."""
    for e in enemies:
        if not e['path']:
            continue
        x, y = e['path'][0]
        px, py = cell_center(x, y, cell_size)
        pygame.draw.circle(surf, (255, 200, 50), (px, py), cell_size // 3)
    
def draw_towers(surf, towers, cell_size):
    """Draws towers at their locations."""
    for x, y in towers:
        pygame.draw.rect(surf, (255, 0, 0), cell_rect(x, y, cell_size))
    
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

def draw_arrowhead(surf, start, end, color):
    """Draws a small arrowhead at the end of a path segment."""

def draw_menu(surf, buttons):
    """Draws start menu UI with clickable buttons."""

def draw_map_screen(surf, run_state):
    """Draws roguelite map nodes, connections, and player progress."""

def draw_info_bars(surf, run_state):
    """Draws sidebars with core HP, gold, wave info, etc."""

def draw_zoomed_map(surf, grid, camera):
    """Draws map with camera zoom and panning applied."""
