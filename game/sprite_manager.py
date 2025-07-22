import os

import pygame


class SpriteManager:
    def __init__(self):
        self.asset_path = "assets"
        self.sprites = {
            "tile": {},
            "unit": {},
            "ui": {},
        }

    def load_assets(self):
        self.sprites["tile"] = {
            "grass": self._load("tiles/grass.png"),
            "wall": self._load("tiles/wall.png"),
            "water": self._load("tiles/water.png"),
        }
        self.sprites["unit"] = {
            "knight": self._load("units/knight.png"),
            "goblin": self._load("units/goblin.png"),
        }
        self.sprites["ui"] = {
            "cursor": self._load("ui/cursor.png"),
            "healthbar": self._load("ui/healthbar.png"),
        }

    def _load(self, relative_path):
        full_path = os.path.join(self.asset_path, relative_path)
        try:
            return pygame.image.load(full_path).convert_alpha()
        except pygame.error as e:
            raise FileNotFoundError(f"Failed to load image at {full_path}: {e}") from e

    def get_sprite(self, category, name):
        return self.sprites.get(category, {}).get(name)
