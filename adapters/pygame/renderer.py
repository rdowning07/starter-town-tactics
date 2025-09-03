"""
Pull-only renderer: reads a snapshot, draws tiles + units, small UI with objective summary
"""
from typing import Any, Tuple

import pygame


class Renderer:
    def __init__(self, screen: pygame.Surface, sprites: Any):
        self.screen = screen
        self.sprites = sprites
        self.font = pygame.font.Font(None, 16)  # Default font for text rendering

    def draw(self, snapshot: Any) -> None:
        """
        Draw the game state from a snapshot.

        Args:
            snapshot: Game state snapshot with tiles, units, highlights, text
        """
        # Clear screen
        self.screen.fill((0, 0, 0))

        # Draw tiles
        for tile in snapshot.tiles:
            tile.draw(self.screen)

        # Draw units
        for unit in snapshot.units:
            self.screen.blit(self.sprites[unit.sprite_id], unit.pixel_pos)

        # Draw objective text
        y = 4
        for line in snapshot.objective_lines:
            self._draw_text(line, (4, y))
            y += 16

    def _draw_text(self, text: str, pos: Tuple[int, int]) -> None:
        """
        Draw text at the specified position.

        Args:
            text: Text to draw
            pos: (x, y) position in pixels
        """
        if text:
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, pos)
