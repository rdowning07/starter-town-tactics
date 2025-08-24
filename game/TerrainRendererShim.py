# Standard library imports
from typing import List, Tuple, Optional

# Third-party imports
import pygame

# Local imports
from .TileCatalog import TileCatalog


class TerrainRendererShim:
    """Minimal terrain renderer that draws a char map using TileCatalog.

    Expected map symbols:
      G: grass
      F: forest (uses grass-like tile by default)
      M: stone/mountain
      W: water
      R: road
      #: wall/cliff

    Layer order is expected to be handled by the caller;
    this shim only draws the terrain layer onto the given surface.

    Coding standards:
      - Import order respected (stdlib → third-party → local)
      - No broad exceptions
      - Type annotations included
    """

    SYMBOL_ALIAS = {
        'G': 'grass',
        'F': 'forest',
        'M': 'stone',
        'W': 'water',
        'R': 'road',
        '#': 'wall',
    }

    def __init__(self, catalog: TileCatalog) -> None:
        self.catalog = catalog
        self.tile_w, self.tile_h = catalog.tile_size

    def draw(
        self,
        surface: pygame.Surface,
        char_map: List[str],
        camera_px: Tuple[int, int] = (0, 0),
    ) -> None:
        """Draw the map to the surface at a camera offset in pixels."""
        cam_x, cam_y = camera_px
        for y, row in enumerate(char_map):
            for x, ch in enumerate(row):
                alias = self.SYMBOL_ALIAS.get(ch)
                if alias is None:
                    continue
                tile = self.catalog.get_alias(alias)
                if tile is None:
                    continue
                screen_x = x * self.tile_w - cam_x
                screen_y = y * self.tile_h - cam_y
                surface.blit(tile, (screen_x, screen_y))
