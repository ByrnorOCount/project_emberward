import pygame
from constants import *
from .render_menu import draw_grid_background

def draw_map(surf, run_state):
    """Draws roguelite map nodes, connections, and player progress (simple single-node)."""
    surf.fill((30, 30, 30))
    w, h = surf.get_size()
    draw_grid_background(surf, 48)
    # single big node in center
    cx, cy = w // 2, h // 2
    node_r = 48
    pygame.draw.circle(surf, (100, 160, 240), (cx, cy), node_r)
    pygame.draw.circle(surf, (220, 220, 220), (cx, cy), node_r, 4)
    font = pygame.font.SysFont(DEFAULT_FONT_NAME, 22, bold=True)
    name = run_state.get("nodes", [{}])[0].get("name", "Node")
    txt = font.render(name, True, (255,255,255))
    txt_r = txt.get_rect(center=(cx, cy))
    surf.blit(txt, txt_r)
    # small instruction
    f2 = pygame.font.SysFont(DEFAULT_FONT_NAME, 16)
    hint = f2.render("Click the node to start the run", True, (200,200,200))
    surf.blit(hint, (cx - hint.get_width()//2, cy + node_r + 10))