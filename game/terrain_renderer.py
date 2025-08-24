"""
Terrain Renderer - Renders terrain tiles using TileCatalog.
"""

from typing import Dict, Optional, Tuple

import pygame

from .TileCatalog import TileCatalog


class TerrainRenderer:
    """Renders terrain tiles using TileCatalog."""

    def __init__(self, tile_catalog: TileCatalog):
        """Initialize the terrain renderer."""
        self.tile_catalog = tile_catalog
        self.terrain_mapping = {
            "G": "grass",  # Grass
            "F": "forest",  # Forest (using grass for now)
            "M": "stone",  # Mountain/Stone
            "W": "water",  # Water
            "R": "road",  # Road
            "#": "wall",  # Wall
        }

    def render_terrain(
        self,
        surface: pygame.Surface,
        terrain_map: list,
        camera_x: int = 0,
        camera_y: int = 0,
        tile_size: int = 32,
    ) -> None:
        """
        Render terrain tiles to the surface.

        Args:
            surface: Pygame surface to render to
            terrain_map: 2D list of terrain characters
            camera_x: Camera X offset
            camera_y: Camera Y offset
            tile_size: Size of each tile
        """
        for y, row in enumerate(terrain_map):
            for x, terrain_char in enumerate(row):
                if terrain_char in self.terrain_mapping:
                    alias = self.terrain_mapping[terrain_char]
                    tile_surface = self.tile_catalog.get_alias(alias)

                    if tile_surface:
                        # Calculate screen position
                        screen_x = x * tile_size - camera_x
                        screen_y = y * tile_size - camera_y

                        # Only render if tile is visible
                        if (
                            screen_x + tile_size > 0
                            and screen_x < surface.get_width()
                            and screen_y + tile_size > 0
                            and screen_y < surface.get_height()
                        ):
                            surface.blit(tile_surface, (screen_x, screen_y))
                    else:
                        # Debug: Print what's missing
                        print(f"Missing tile for alias '{alias}' (char '{terrain_char}')")
                        # Fallback to simple colored rectangle
                        placeholder = pygame.Surface((tile_size, tile_size))
                        placeholder.fill((128, 128, 128))  # Gray placeholder
                        screen_x = x * tile_size - camera_x
                        screen_y = y * tile_size - camera_y
                        surface.blit(placeholder, (screen_x, screen_y))

    def set_terrain_mapping(self, mapping: Dict[str, str]) -> None:
        """Set custom terrain character to alias mapping."""
        self.terrain_mapping = mapping.copy()

    def get_terrain_mapping(self) -> Dict[str, str]:
        """Get current terrain character to alias mapping."""
        return self.terrain_mapping.copy()

    def add_terrain_mapping(self, char: str, alias: str) -> None:
        """Add a single terrain character to alias mapping."""
        self.terrain_mapping[char] = alias
