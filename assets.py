import os
import random
import pygame

# Initialize Pygame display early (if not already)
if not pygame.get_init():
    pygame.init()
    if not pygame.display.get_init():
        pygame.display.set_mode((1, 1))  # tiny hidden window

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images")

# Helper to load and convert images
def load_image(path, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

# ======================
# Load all images
# ======================
def load_assets():
    assets = {
        "enemies": {},
        "towers": {},
        "projectiles": {},
        "obstacles": [],
        "background": [],
    }

    # --- Enemies ---
    enemies_dir = os.path.join(IMAGE_DIR, "enemies")
    for fname in os.listdir(enemies_dir):
        if fname.endswith(".png"):
            key = os.path.splitext(fname)[0]  # e.g. "basic"
            assets["enemies"][key] = load_image(os.path.join(enemies_dir, fname))

    # --- Towers ---
    # towers_dir = os.path.join(IMAGE_DIR, "towers")
    # for fname in os.listdir(towers_dir):
    #     if fname.endswith(".png"):
    #         key = os.path.splitext(fname)[0]
    #         assets["towers"][key] = load_image(os.path.join(towers_dir, fname))

    # --- Projectiles ---
    # proj_dir = os.path.join(IMAGE_DIR, "projectiles")
    # for fname in os.listdir(proj_dir):
    #     if fname.endswith(".png"):
    #         key = os.path.splitext(fname)[0]
    #         assets["projectiles"][key] = load_image(os.path.join(proj_dir, fname))

    # --- Obstacles ---
    obstacles_dir = os.path.join(IMAGE_DIR, "obstacles")
    if os.path.exists(obstacles_dir):
        for fname in os.listdir(obstacles_dir):
            if fname.endswith(".png"):
                img = load_image(os.path.join(obstacles_dir, fname))
                assets["obstacles"].append(img)

    # --- Background ---
    bg_path = os.path.join(IMAGE_DIR, "background.png")
    if os.path.exists(bg_path):
        assets["background"] = pygame.image.load(bg_path).convert()
    else:
        assets["background"] = None

    return assets

def get_random_obstacle_image():
    assets = get_assets()
    if assets["obstacles"]:
        return random.choice(assets["obstacles"])
    return None

# Global cache (optional lazy load)
_ASSETS = None

def get_assets():
    global _ASSETS
    if _ASSETS is None:
        _ASSETS = load_assets()
    return _ASSETS
