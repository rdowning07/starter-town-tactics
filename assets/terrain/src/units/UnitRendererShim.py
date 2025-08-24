# Standard library imports
from typing import Tuple

# Third-party imports
import pygame

# Local imports
from .AnimationCatalog import AnimationCatalog


class UnitRendererShim:
    def __init__(self, catalog: AnimationCatalog, tile_size: Tuple[int, int] = (32, 32)) -> None:
        self.catalog = catalog
        self.tile_w, self.tile_h = tile_size

    def draw_unit(self, surface: pygame.Surface, unit_sprite: str, state: str,
                  grid_xy: Tuple[int, int], camera_px: Tuple[int, int], elapsed_ms: int) -> None:
        meta = self.catalog.get(unit_sprite, state)
        if not meta:
            return
        frames = self.catalog.frames_for(meta)
        if not frames:
            return
        idx = self.catalog.frame_index(meta, elapsed_ms)
        frame = frames[idx]
        fw, fh = frame.get_width(), frame.get_height()
        world_x = grid_xy[0] * self.tile_w + self.tile_w // 2
        world_y = grid_xy[1] * self.tile_h + self.tile_h
        ox, oy = meta.get('origin', [fw // 2, fh])  # type: ignore[assignment]
        screen_x = world_x - camera_px[0] - int(ox)
        screen_y = world_y - camera_px[1] - int(oy)
        surface.blit(frame, (screen_x, screen_y))
