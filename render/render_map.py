import pygame
from constants import *
from .render_menu import draw_grid_background

def draw_map(surf, level_nodes, hovered_node_id=None):
    """Draws the level selection map screen."""
    surf.fill((30, 30, 30))
    w, h = surf.get_size()
    draw_grid_background(surf, 48)

    if not level_nodes:
        return

    # Draw lines between nodes
    if len(level_nodes) > 1:
        for i in range(len(level_nodes) - 1):
            start_pos = level_nodes[i]["pos"]
            end_pos = level_nodes[i+1]["pos"]
            pygame.draw.line(surf, (100, 100, 100), start_pos, end_pos, 4)

    for level_node in level_nodes:
        cx, cy = level_node["pos"]
        is_hovered = level_node["id"] == hovered_node_id
        is_accessible = level_node.get("accessible", True)
        radius = level_node["radius"] + 5 if is_hovered and is_accessible else level_node["radius"]

        if is_accessible:
            pygame.draw.circle(surf, (100, 160, 240), (cx, cy), radius)
            pygame.draw.circle(surf, (220, 220, 220), (cx, cy), radius, 4)
        else:
            pygame.draw.circle(surf, (80, 80, 80), (cx, cy), radius)
            pygame.draw.circle(surf, (120, 120, 120), (cx, cy), radius, 4)
        font = pygame.font.SysFont(DEFAULT_FONT_NAME, 22, bold=True)
        txt = font.render(level_node["name"], True, (255,255,255))
        txt_r = txt.get_rect(center=(cx, cy))
        surf.blit(txt, txt_r)
        # small instruction
        f2 = pygame.font.SysFont(DEFAULT_FONT_NAME, 16)
        hint = f2.render("Click a node to start the battle", True, (200,200,200))
        surf.blit(hint, (w // 2 - hint.get_width()//2, h - 40))