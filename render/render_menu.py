import pygame, time
from constants import *

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

def draw_menu(surf):
    """Draws start menu with subtle diagonal rainbow overlay and interactive buttons."""
    surf.fill((30, 30, 30))

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
    font_title = pygame.font.SysFont(DEFAULT_FONT_NAME, 72, bold=True)
    title_surf = font_title.render("Emberward Clone", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(w // 2, h // 4))
    surf.blit(title_surf, title_rect)

def draw_button(surf, btn):
    mx, my = pygame.mouse.get_pos()
    hovered = btn.rect.collidepoint(mx, my)

    color = (200,200,200) if hovered else (160,160,160)
    border = (255,255,255) if hovered else (60,60,60)

    rect = btn.rect.copy()
    if hovered:
        rect.inflate_ip(10, 10)

    pygame.draw.rect(surf, color, rect, border_radius=12)
    pygame.draw.rect(surf, border, rect, 4, border_radius=12)

    txt = btn.font.render(btn.text, True, (0,0,0))
    txt_rect = txt.get_rect(center=rect.center)
    surf.blit(txt, txt_rect)