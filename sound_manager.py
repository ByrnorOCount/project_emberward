import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")

pygame.mixer.init()
_sound_cache = {}

def play_music(filename, volume=0.5, loop=True):
    path = os.path.join(SOUND_DIR, filename)
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1 if loop else 0)

def play_sound(filename, volume=1.0):
    """Play a sound effect once, using cache."""
    path = os.path.join(SOUND_DIR, filename)
    if path not in _sound_cache:
        _sound_cache[path] = pygame.mixer.Sound(path)
    sound = _sound_cache[path]
    sound.set_volume(volume)
    sound.play()
