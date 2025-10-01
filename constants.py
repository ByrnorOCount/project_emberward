import pygame

# Default font for the game
DEFAULT_FONT_NAME = "arial"
DEFAULT_FONT_SIZE = 24
DEFAULT_FONT_BOLD = False

# Pre-create a Pygame Font object
pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont(DEFAULT_FONT_NAME, DEFAULT_FONT_SIZE, bold=DEFAULT_FONT_BOLD)
