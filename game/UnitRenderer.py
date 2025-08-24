# Standard library imports
from typing import Tuple, Optional

# Third-party imports
import pygame

# Local imports
from .AnimationCatalog import AnimationCatalog, frame_index, get_current_frame


class UnitRenderer:
    """Renders units on the game grid."""

    def __init__(
        self, catalog: AnimationCatalog, tile_size: Tuple[int, int] = (32, 32)
    ) -> None:
        self.catalog = catalog
        self.tile_w, self.tile_h = tile_size

    def draw_unit(
        self,
        surface: pygame.Surface,
        unit_sprite: str,
        state: str,
        grid_xy: Tuple[int, int],
        camera_px: Tuple[int, int],
        elapsed_ms: int,
    ) -> None:
        """Draw a unit at the specified grid position."""
        meta = self.catalog.get(unit_sprite, state)
        if not meta:
            return

        # Get the current frame
        frame_surface = self._get_current_frame_surface(meta, elapsed_ms)
        if frame_surface is None:
            return

        # Calculate world position (center of tile)
        world_x = grid_xy[0] * self.tile_w + self.tile_w // 2
        world_y = grid_xy[1] * self.tile_h + self.tile_h

        # Apply origin offset
        w, h = frame_surface.get_size()
        ox, oy = meta.get("origin", [w // 2, h])
        screen_x = world_x - camera_px[0] - ox
        screen_y = world_y - camera_px[1] - oy

        # Draw the unit
        surface.blit(frame_surface, (int(screen_x), int(screen_y)))

    def draw_unit_simple(
        self,
        surface: pygame.Surface,
        unit_sprite: str,
        state: str,
        grid_xy: Tuple[int, int],
        camera_px: Tuple[int, int],
        elapsed_ms: int,
    ) -> None:
        """Draw a unit with simplified positioning (for demos)."""
        meta = self.catalog.get(unit_sprite, state)
        if not meta:
            return

        # Get the current frame
        frame_surface = self._get_current_frame_surface(meta, elapsed_ms)
        if frame_surface is None:
            return

        # Simple positioning (top-left of tile)
        screen_x = grid_xy[0] * self.tile_w - camera_px[0]
        screen_y = grid_xy[1] * self.tile_h - camera_px[1]

        # Draw the unit
        surface.blit(frame_surface, (int(screen_x), int(screen_y)))

    def _get_current_frame_surface(self, meta: dict, elapsed_ms: int) -> Optional[pygame.Surface]:
        """Get the current frame surface for an animation."""
        if "frame_files" in meta:
            # Frame-based animation
            frame_files = meta.get("frame_files", [])
            if not frame_files:
                return None
            idx = frame_index(meta, elapsed_ms)
            if idx < len(frame_files):
                frame_file = frame_files[idx]
                return self.catalog.get_frame(frame_file)
        elif "sheet" in meta:
            # Sheet-based animation (legacy)
            sheet = self.catalog.get_sheet(meta)
            if sheet is None:
                return None
            w, h = meta.get("frame_size", [32, 32])
            idx = frame_index(meta, elapsed_ms)
            src = pygame.Rect(idx * w, 0, w, h)
            frame_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), src)
            return frame_surface
        return None
