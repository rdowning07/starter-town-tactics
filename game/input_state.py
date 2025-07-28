# game/input_state.py

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from game.grid import Grid
    from game.game import Game
    from game.unit import Unit
    from game.sprite_manager import SpriteManager


class InputState:
    def __init__(self, game: Game | None = None):
        self.game: Game | None = game
        self.cursor_x: int = 0
        self.cursor_y: int = 0
        self.selected_unit: Unit | None = None
        self.key_states: set[str] = set()
        self.mouse_click: tuple[int, int] | None = None
        self.state: str = "idle"

    @property
    def keys_pressed(self) -> set[str]:
        """Return all key states normalized to uppercase (for test comparisons)."""
        return {key.upper() for key in self.key_states}

    def set_key_down(self, key: str) -> None:
        """Register a key as being pressed (case insensitive)."""
        self.key_states.add(key.lower())

    def set_key_up(self, key: str) -> None:
        """Register a key as being released (case insensitive)."""
        self.key_states.discard(key.lower())

    def set_mouse_click(self, pos: tuple[int, int]) -> None:
        """Register a mouse click at the given (x, y) tile coordinates."""
        self.mouse_click = pos

    def clear_mouse_click(self) -> None:
        """Clear the mouse click after it's been processed."""
        self.mouse_click = None

    def move_cursor(self, dx: int, dy: int) -> None:
        """Move the selection cursor, clamped to the map bounds."""
        self.cursor_x += dx
        self.cursor_y += dy
        if self.game and hasattr(self.game, "grid"):
            self.cursor_x = max(0, min(self.cursor_x, self.game.grid.width - 1))
            self.cursor_y = max(0, min(self.cursor_y, self.game.grid.height - 1))

    def confirm_selection(self) -> None:
        """Handles selection or movement based on current cursor state."""
        if not self.game or not hasattr(self.game, "grid"):
            return

        tile = self.game.grid.get_tile(self.cursor_x, self.cursor_y)
        if tile.unit:
            self.selected_unit = tile.unit
            self.state = "selected"
        elif self.selected_unit:
            moved = self.selected_unit.move(self.cursor_x, self.cursor_y, self.game.grid)
            if moved:
                self.selected_unit = None
                self.state = "idle"
                if hasattr(self.game, "turn_controller"):
                    self.game.turn_controller.end_turn()

    def cancel_selection(self) -> None:
        """Cancel current unit selection."""
        self.selected_unit = None
        self.state = "idle"

    def draw_cursor(
        self,
        surface: pygame.Surface,
        tile_size: int,
        offset_x: int,
        offset_y: int,
        sprites: SpriteManager,
    ) -> None:
        """Draw a cursor sprite at the current tile position."""
        try:
            sprite = sprites.get_cursor_sprite()
        except AttributeError:
            # Fallback dummy sprite for test environments
            sprite = pygame.Surface((tile_size, tile_size))
            sprite.fill((255, 255, 255))  # White block

        x = self.cursor_x * tile_size + offset_x
        y = self.cursor_y * tile_size + offset_y
        surface.blit(sprite, (x, y))
